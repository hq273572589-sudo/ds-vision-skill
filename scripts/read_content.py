#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
vision-bridge: 本地内容识别与 OCR 桥接脚本。

把图片、PDF、Office 文档转换为纯文本，供不支持视觉的模型（如 DeepSeek-V4-Flash）使用。

策略（按文件类型分层，能本地提取就不调视觉模型）：
  图片 (.png/.jpg/.jpeg/.gif/.bmp/.webp/.tiff/.ico/.svg)
      → 直接走视觉模型（无 OCR 本地兜底可用）
  文字版 PDF
      → 本地 pymupdf 提取文本；某页无文字（扫描页）自动降级为视觉模型
  Excel (.xlsx/.xlsm/.xltx/.xltm)
      → 本地 openpyxl 提取（含公式与计算值）
  Word (.docx) → 本地 python-docx 提取
  PPT  (.pptx)  → 本地 python-pptx 提取（含备注）
  其他/失败 → 视觉模型兜底

配置（首次使用时交互式生成 <skill>/scripts/config.json）：
  {
    "base_url": "https://api.openai.com/v1",   // OpenAI 兼容端点
    "api_key":  "sk-...",                       // 或 ""（本地模型无需鉴权）
    "model":    "gpt-4o"                        // 或 qwen2.5vl / llava 等
  }
"""
import argparse
import base64
import json
import mimetypes
import os
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

# Windows 控制台默认 GBK 会破坏 UTF-8 中文输出，统一强制 UTF-8
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


# 支持列表：键为扩展名（含点），值为 "image" / "doc"
SUPPORTED = {
    ".png": "image", ".jpg": "image", ".jpeg": "image", ".gif": "image",
    ".bmp": "image", ".webp": "image", ".tiff": "image", ".tif": "image",
    ".ico": "image", ".svg": "image",
    ".pdf": "pdf",
    ".docx": "docx", ".xlsx": "xlsx", ".xlsm": "xlsx",
    ".xltx": "xlsx", ".xltm": "xlsx", ".pptx": "pptx",
}
MAGIC_SIGNATURES = {
    b"%PDF": "pdf",
    b"PK\x03\x04": "office-zip",  # docx/xlsx/pptx 均为此魔数
    b"\x89PNG\r\n\x1a\n": "image",
    b"\xff\xd8\xff": "image",   # JPEG
    b"GIF87a": "image", bytes("GIF89a", "ascii"): "image",
    b"BM": "image",             # BMP
    b"II*\x00": "image", b"MM\x00*": "image",  # TIFF
    b"RIFF": "image",           # WEBP
}
CONFIG_NAME = "config.json"


# ---------------------------------------------------------------- 配置与杂项

def skill_dir() -> Path:
    return Path(__file__).resolve().parent


def load_config() -> dict | None:
    cfg = skill_dir() / CONFIG_NAME
    if cfg.exists():
        try:
            return json.loads(cfg.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"配置文件解析失败 {cfg}: {e}，将重新配置", file=sys.stderr)
    return None


def first_run_config() -> dict:
    """首次使用：交互式引导配置 OpenAI 兼容端点。"""
    print("=" * 60)
    print("vision-bridge 首次使用：请配置视觉模型端点")
    print("如果不确定，本地 Ollama 示例:  http://localhost:11434/v1")
    print("示例模型: gpt-4o / qwen2.5vl / llava / gemini-2.0-flash")
    print("=" * 60)
    base = input("  API 请求地址 (base_url): ").strip().rstrip("/") or "http://localhost:11434/v1"
    key = input("  API Key (本地模型可留空回车): ").strip()
    model = input(f"  模型名称 (默认 {base.rsplit('/', 1)[-1] or '不填'}): ").strip()
    if not model:
        model = "gpt-4o"
    cfg = {"base_url": base, "api_key": key, "model": model}
    try:
        (skill_dir() / CONFIG_NAME).write_text(
            json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(f"已保存配置到 {skill_dir() / CONFIG_NAME}")
    except OSError as e:
        print(f"配置文件写入失败（只读目录？）：{e}", file=sys.stderr)
        print("请手动创建含以下内容的 config.json：")
        print(json.dumps(cfg, ensure_ascii=False, indent=2))
    return cfg


def check_runtime() -> None:
    """校验本地提取所需的库；缺失时给出安装提示（中文）。"""
    missing = []
    try:
        import pymupdf  # noqa: F401
    except ImportError:
        missing.append("pymupdf                    (PDF 提取)  → python -m pip install pymupdf")
    try:
        import docx  # noqa: F401
    except ImportError:
        missing.append("python-docx                (Word)      → python -m pip install python-docx")
    try:
        import openpyxl  # noqa: F401
    except ImportError:
        missing.append("openpyxl                   (Excel)     → python -m pip install openpyxl")
    try:
        import pptx  # noqa: F401
    except ImportError:
        missing.append("python-pptx                 (PPT)       → python -m pip install python-pptx")
    if missing:
        # 不致命：仅失去本地提取能力，视觉模型仍可兜底全文理解
        print("以下本地提取库缺失（不影响图片识别，但 PDF/Office 将依赖视觉模型）：",
              file=sys.stderr)
        for m in missing:
            print(f"  - {m}", file=sys.stderr)


def probe_type(path: Path) -> str | None:
    """根据扩展名 + 魔数判断文件类型（返回 SUPPORTED 键或 None）。"""
    ext = path.suffix.lower()
    if ext in SUPPORTED:
        return SUPPORTED[ext]
    with open(path, "rb") as f:
        head = f.read(12)
    for sig, t in MAGIC_SIGNATURES.items():
        if head.startswith(sig):
            return t if t != "office-zip" else "docx"  # zip 统一按 docx 尝试,内部再分派
    return None


# ---------------------------------------------------------------- 本地提取

def extract_pdf_text(path: Path, cfg: dict) -> tuple[str, list[int]]:
    """本地提取 PDF 文本。返回 (全文, 无文本需视觉处理的页索引)。"""
    import pymupdf
    doc = pymupdf.open(path)
    parts, vision_pages = [], []
    for i, page in enumerate(doc):
        txt = page.get_text("text").strip()
        parts.append(f"===== [第 {i+1} 页] =====\n{txt}" if txt else f"===== [第 {i+1} 页] =====\n(本页无可提取文本——扫描页，需视觉模型处理)")
        if not txt:
            vision_pages.append(i)
    return "\n\n".join(parts), vision_pages


def extract_docx(path: Path) -> str:
    import docx
    d = docx.Document(path)
    lines = [p.text for p in d.paragraphs if p.text.strip()]
    for tbl in d.tables:
        for row in tbl.rows:
            cells = [c.text.strip() for c in row.cells]
            if any(cells):
                lines.append(" | ".join(cells))
    return "\n".join(lines)


def extract_xlsx(path: Path) -> str:
    import openpyxl
    wb = openpyxl.load_workbook(path, data_only=True, read_only=True)
    parts = []
    for ws in wb.worksheets:
        parts.append(f"===== 工作表: {ws.title} =====")
        for row in ws.iter_rows(values_only=True):
            vals = ["" if v is None else str(v) for v in row]
            if any(vals):
                parts.append(" | ".join(vals))
    return "\n".join(parts)


def extract_pptx(path: Path) -> str:
    from pptx import Presentation
    prs = Presentation(path)
    parts = []
    for i, slide in enumerate(prs.slides, 1):
        parts.append(f"===== 幻灯片 {i} =====")
        for shape in slide.shapes:
            if shape.has_text_frame:
                t = shape.text_frame.text.strip()
                if t:
                    parts.append(t)
            if shape.shape_type == 13 and shape.has_text_frame:  # 表格
                pass
            if getattr(shape, "has_table", False) and shape.has_table:
                for row in shape.table.rows:
                    cells = [c.text.strip() for c in row.cells]
                    if any(cells):
                        parts.append(" | ".join(cells))
        if slide.has_notes_slide and slide.notes_slide.notes_text_frame.text.strip():
            parts.append(f"    [备注] {slide.notes_slide.notes_text_frame.text.strip()}")
    return "\n".join(parts)


def extract_office(path: Path, kind: str) -> tuple[str, bool]:
    """本地 Office 提取。返回 (文本, 是否仅尽力而为)。"""
    if kind == "docx":
        return extract_docx(path), True
    if kind == "xlsx":
        return extract_xlsx(path), True
    if kind == "pptx":
        return extract_pptx(path), True
    return "", False


# ---------------------------------------------------------------- 视觉模型

def _request_json(method: str, url: str, headers: dict, data, timeout: int, retries: int, label: str = "调用"):
    """带自动重试的 HTTP 请求：对 5xx/429/超时/连接错误自动重试，返回解析后的 JSON。"""
    last = None
    for attempt in range(1, retries + 1):
        try:
            req = urllib.request.Request(url, data=data, headers=headers, method=method)
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 504) and attempt < retries:
                wait = min(2 * attempt, 10)
                print(f"[vision-bridge] {label} HTTP {e.code}，{wait}s 后重试（{attempt}/{retries}）", file=sys.stderr)
                time.sleep(wait); last = e; continue
            raise
        except (urllib.error.URLError, TimeoutError, ConnectionError, OSError) as e:
            if attempt < retries:
                wait = min(2 * attempt, 10)
                print(f"[vision-bridge] {label} {type(e).__name__}，{wait}s 后重试（{attempt}/{retries}）", file=sys.stderr)
                time.sleep(wait); last = e; continue
            raise
    raise last


def call_vision(cfg: dict, file_paths: list[str], prompt: str, timeout: int = 120, retries: int = 3) -> str:
    """调用 OpenAI 兼容端点识别一个或多个文件。返回模型文本。"""
    import io as _io

    _pil = None
    try:
        from PIL import Image as _PILImage
        _pil = _PILImage
    except ImportError:
        pass  # 未安装 Pillow 时跳过压缩，直接发送原图

    def attach(p: str) -> dict:
        path = Path(p)
        mime, _ = mimetypes.guess_type(p) or "application/octet-stream"
        if mime.startswith("image/"):
            if _pil is not None:
                with _pil.open(path) as im:
                    im.thumbnail((2000, 2000))  # 压缩超大图
                    buf = _io.BytesIO()
                    im.save(buf, format=im.format or "PNG")
                    b64 = base64.b64encode(buf.getvalue()).decode()
            else:
                b64 = base64.b64encode(path.read_bytes()).decode()
            return {"type": "image_url",
                    "image_url": {"url": f"data:{mime};base64,{b64}"}}
        # 非图片：当作文件交给模型（部分模型支持 file_url）
        b64 = base64.b64encode(path.read_bytes()).decode()
        return {"type": "file", "file": {"filename": path.name,
                "file_data": f"data:{mime};base64,{b64}"}}

    payload = {
        "model": cfg["model"],
        "messages": [{
            "role": "user",
            "content": [
                {"type": "text", "text": prompt + "\n\n(请只输出内容本身，不要额外评论)"},
                *[attach(p) for p in file_paths],
            ],
        }],
        "temperature": 0.1,
    }
    url = f"{cfg['base_url']}/chat/completions"
    headers = {"Content-Type": "application/json"}
    if cfg.get("api_key"):
        headers["Authorization"] = f"Bearer {cfg['api_key']}"

    try:
        body = _request_json("POST", url, headers,
                             json.dumps(payload).encode("utf-8"),
                             timeout, retries, label="视觉模型")
        return body["choices"][0]["message"]["content"] or ""
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="replace")[:500]
        return f"[视觉模型调用失败] HTTP {e.code}: {detail}"
    except Exception as e:
        return f"[视觉模型调用失败] {e}"



def list_models(cfg: dict, timeout: int = 60, retries: int = 3) -> str:
    """列出端点可用模型（便于挑选支持图像的视觉模型）。"""
    url = f"{cfg['base_url']}/models"
    headers = {}
    if cfg.get("api_key"):
        headers["Authorization"] = f"Bearer {cfg['api_key']}"
    try:
        body = _request_json("GET", url, headers, None, timeout, retries, label="列出模型")
        ids = [m.get("id") for m in body.get("data", []) if isinstance(m, dict)]
        return "\n".join(str(x) for x in ids) if ids else json.dumps(body, ensure_ascii=False, indent=2)
    except urllib.error.HTTPError as e:
        return f"[列出模型失败] HTTP {e.code}: {e.read().decode('utf-8', errors='replace')[:500]}"
    except Exception as e:
        return f"[列出模型失败] {e}"


def call_vision_extract_text(cfg: dict, paths: list[str], lang: str, timeout: int = 120, retries: int = 3) -> str:
    """供文档/图片统一入口：仅输出原始文本。"""
    region = "请把图片中的文字、表格、图表内容完整、准确地转录为纯文本"
    prompt = (f"{region}。\n要求：\n"
              f"- 语言：使用{'中文' if lang == 'zh' else '英文'}\n"
              "- 保留原有换行与段落结构\n"
              "- 表格用 '|' 分隔列\n"
              "- 只输出内容本身，不要解释或评论")
    return call_vision(cfg, paths, prompt, timeout, retries)


# ---------------------------------------------------------------- 主流程

def process(path: Path, cfg: dict, opts) -> tuple[str, list[str]]:
    """处理单个文件，返回 (文本, 已用策略标签列表)。"""
    logs: list[str] = []
    kind = probe_type(path)
    if kind is None:
        logs.append(f"无法识别类型 {path.name}，尝试视觉模型")
        return call_vision_extract_text(cfg, [str(path)], opts.lang, opts.timeout, opts.retries), logs

    if kind == "image":
        logs.append("图片 → 视觉模型")
        return call_vision_extract_text(cfg, [str(path)], opts.lang, opts.timeout, opts.retries), logs

    if kind == "pdf":
        try:
            text, vision_pages = extract_pdf_text(path, cfg)
        except Exception as e:
            text, vision_pages = "", [0]
            logs.append(f"PDF 本地提取失败({e})，整份走视觉模型")
        if not vision_pages:
            logs.append("PDF → 本地提取文本")
            return text, logs
        # 有扫描页：只把扫描页切图送视觉模型
        logs.append(f"PDF → 混合（{len(text.splitlines())} 行本地 + {len(vision_pages)} 页视觉）")
        import pymupdf
        doc = pymupdf.open(path)
        tmp = tempfile.mkdtemp(prefix="visionbridge_")
        imgs = []
        for idx in vision_pages:
            pix = doc[idx].get_pixmap(dpi=150)
            p = os.path.join(tmp, f"page_{idx+1}.png")
            pix.save(p)
            imgs.append(p)
        ocr_text = call_vision_extract_text(cfg, imgs, opts.lang, opts.timeout, opts.retries)
        return f"{text}\n\n----- [扫描页 OCR 内容] -----\n{ocr_text}", logs

    if kind in ("docx", "xlsx", "pptx"):
        try:
            local_text, _ = extract_office(path, kind)
        except Exception as e:
            local_text = ""
            logs.append(f"Office 本地提取失败({e})")
        if local_text and not opts.force_vision:
            logs.append(f"{kind.upper()} → 本地提取文本")
            return local_text, logs
        logs.append(f"{kind.upper()} → 提取为空/强制视觉，走视觉模型")
        return (local_text + "\n\n----- [视觉模型补充] -----\n"
                + call_vision_extract_text(cfg, [str(path)], opts.lang, opts.timeout, opts.retries)), logs

    logs.append(f"未匹配类型 {kind}，走视觉模型")
    return call_vision_extract_text(cfg, [str(path)], opts.lang, opts.timeout, opts.retries), logs


def main() -> int:
    ap = argparse.ArgumentParser(description="把图片/PDF/Office 文档转成文本")
    ap.add_argument("paths", nargs="*", help="要处理的文件（可多个，用空格分隔）")
    ap.add_argument("--lang", choices=["zh", "en"], default="zh",
                    help="视觉模型转录语言（默认 zh）")
    ap.add_argument("--force-vision", action="store_true",
                    help="Office 文档也强制走视觉模型（不信任本地提取时）")
    ap.add_argument("--configure", action="store_true",
                    help="仅重新配置视觉模型端点，不处理文件")
    ap.add_argument("--list-models", action="store_true",
                    help="列出端点可用模型（便于选择视觉模型），不处理文件")
    ap.add_argument("--model", default=None,
                    help="临时覆盖 config.json 中的模型名（不写入配置）")
    ap.add_argument("--check", action="store_true",
                    help="仅检查本地提取依赖，不处理文件")
    ap.add_argument("--timeout", type=int, default=120,
                    help="单次请求超时秒数（默认 120）")
    ap.add_argument("--retries", type=int, default=3,
                    help="失败自动重试次数（默认 3，对 5xx/429/超时/连接错误生效）")
    args = ap.parse_args()

    if args.check:
        check_runtime(); return 0

    if args.list_models:
        cfg = load_config()
        if cfg is None:
            cfg = first_run_config()
        print(list_models(cfg, args.timeout, args.retries))
        return 0


    if not args.paths and not args.configure:
        ap.error("至少需要指定一个文件路径（或使用 --check / --configure）")
    cfg = load_config()
    if args.configure or cfg is None:
        cfg = first_run_config()

    if not args.paths and args.configure:
        return 0

    if args.model:
        cfg["model"] = args.model

    # 校验文件存在
    exist = [p for p in args.paths if Path(p).exists()]
    if not exist:
        print("没有找到任何有效的输入文件，请检查路径。", file=sys.stderr)
        return 2

    # 收集所有文本
    blocks, logs_all = [], []
    for p in exist:
        text, logs = process(Path(p), cfg, args)
        blocks.append(f"######## 文件: {os.path.basename(p)} ########\n{text}")
        logs_all.append((os.path.basename(p), logs))

    print("\n\n".join(blocks))
    print("\n===== vision-bridge 处理日志 =====", file=sys.stderr)
    for name, logs in logs_all:
        print(f"  {name}: " + "; ".join(logs), file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
