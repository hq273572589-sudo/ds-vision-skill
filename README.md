# vision-bridge

> 为**不支持视觉的模型**（如 DeepSeek-V4-Flash）把图片、PDF、扫描件、Word/Excel/PPT 等文件内容识别并转成文本，再交回当前模型使用。

## 这是什么

当前会话模型（如 DeepSeek-V4-Flash）不支持图像输入，发图给它会被网关以 `unknown variant image_url, expected text` 拒绝。vision-bridge 通过一个 **OpenAI 兼容端点**（你自己配置的视觉模型，如 `gpt-5.6-terra`）做识别，再把文本拿回来给当前模型——相当于给文本模型外挂了一双"眼睛"。

## 工作原理

```
当前模型(无视觉) → vision-bridge 启动器 → 你配置的视觉模型(gpt-5.6-terra 等) → 返回文本 → 交回当前模型
```

- HTTP 只用 **Python 标准库**（`urllib`），无需 `requests`。
- 图片：先走**本地 RapidOCR 快速通道**（CPU 秒级、不联网）；未安装 / 识别失败 / 有效文字过少（图表、照片）时自动降级视觉模型（无 Pillow 发原图，有 Pillow 压缩超大图）。`--force-vision` 可跳过 OCR。
- PDF：本地 `pymupdf` 提取文字层；扫描页自动切图送视觉模型。
- Office：本地 `python-docx`/`openpyxl`/`python-pptx` 提取；失败降级给视觉模型。
- 网络请求带**自动重试**（5xx/429/超时/连接错误），可配 `--timeout`/`--retries`。

## 环境要求（通用/跨电脑）

- **Python 3.9+**（推荐 3.12）。通过启动器 `run_vision_bridge.bat` 自动查找解释器，**不要直接用裸 `python`**（部分机器上可能指向 MSYS2 等无依赖环境）。
- **可选依赖**（本地提取 PDF/Office、图片本地 OCR、压缩大图）：`pillow`、`pymupdf`、`python-docx`、`openpyxl`、`python-pptx`、`rapidocr-onnxruntime`。启动器首次运行自动尝试安装；缺失时对应能力自动降级（图片本地 OCR 缺失则直接走视觉模型）。
- **视觉端点**：一个支持图像的 OpenAI 兼容端点 + 模型（如 `gpt-5.6-terra` / `gpt-4o` / `qwen2.5vl` / `llava` / `gemini-2.0-flash`）。纯文本模型不行。

## 安装

### 方式 A：作为 Codex / Claude Code 技能

把本仓库放到技能目录，或建一个指向它的链接：

- Codex：`~/.codex/skills/vision-bridge`（Windows: `C:\Users\<你>\.codex\skills\vision-bridge`）
- Claude Code：`~/.claude/skills/vision-bridge`（Windows: `C:\Users\<你>\.claude\skills\vision-bridge`）

> 技能在会话启动时加载，安装/更新后需**重启会话**。

### 方式 B：独立脚本

克隆到任意位置，运行 `run_vision_bridge.bat` 即可。

## 配置

首次使用，运行配置向导（交互式输入端点/密钥/模型）：

```bat
run_vision_bridge.bat --configure
```

或复制 `scripts/config.example.json` 为 `scripts/config.json` 后编辑：

```json
{
  "base_url": "https://your-gateway.example.com/v1",
  "api_key": "sk-your-api-key",
  "model": "gpt-5.6-terra"
}
```

> ⚠️ `config.json` 含密钥，**切勿提交到仓库**（已在 `.gitignore` 排除）。

不确定端点有哪些模型？先列出再选：

```bat
run_vision_bridge.bat --list-models
```

## 使用

```bat
:: 单文件
run_vision_bridge.bat "C:\path\to\image.png"

:: 多文件
run_vision_bridge.bat "a.png" "b.pdf" "c.docx"

:: 英文转录
run_vision_bridge.bat "image.png" --lang en
```

### 参数

| 参数 | 默认 | 说明 |
|---|---|---|
| `路径...` | — | 要处理的文件（可多个） |
| `--find-in DIR` | — | **仅在用户明确要求时**：在指定目录(递归)中查找图片/文档并识别。Python 原生 `os.walk`，不经过 shell `find`（Windows 无 GNU find） |
| `--name-part SUBSTR` | — | 与 `--find-in` 联用：只匹配文件名包含该关键字的文件 |
| `--latest` | — | 与 `--find-in` 联用：只处理最新修改的那一个文件 |
| `--max-results N` | `10` | 与 `--find-in` 联用：最多处理结果数 |
| `--lang {zh,en}` | `zh` | 视觉模型转录语言 |
| `--force-vision` | 关 | 图片和 Office 文档都跳过本地提取/OCR，强制走视觉模型 |
| `--configure` | — | 重新配置端点 |
| `--list-models` | — | 列出端点可用模型 |
| `--model NAME` | — | 临时覆盖 config 中的模型名（不写入配置） |
| `--check` | — | 只检查本地提取依赖 |
| `--timeout N` | `120` | 单次请求超时秒数 |
| `--retries N` | `3` | 失败自动重试次数（5xx/429/超时/连接错误） |

> ⚠️ **绝不全盘自动扫描**：技能只查**用户显式提供的路径**、用户明确说"帮我找"时用 `--find-in`（限定在指定目录），以及本会话转录 JSONL 里已落盘的 base64 图块。**不要**读取无关应用的缓存目录（如 zcode）。工具调用被拒绝/中断时立即止损，不残留无效 payload（避免 `400 inference request is invalid`）。粘贴图片会触发 400 是纯文本后端的预期行为——失败请求通常不落盘，根治需在自建网关改写 image 块。

## 文件结构

```
vision-bridge/
├── SKILL.md                  # 技能定义（模型据此触发）
├── README.md
├── LICENSE
├── run_vision_bridge.bat     # 通用启动器（自动找 Python、装依赖、透传参数）
├── .gitignore
└── scripts/
    ├── read_content.py        # 主脚本（标准库 urllib，无外部依赖）
    ├── config.json            # 你的配置（不入库）
    └── config.example.json    # 配置模板
```

## 排错

| 现象 | 解决 |
|---|---|
| `unknown variant image_url, expected text` | 当前模型是**纯文本模型**（如 DeepSeek-V4-Flash）。用 `--list-models` 选支持视觉的模型，`--configure` 更新 |
| `视觉模型调用失败` / 超时 | 检查 `base_url`/`api_key`/模型名；调大 `--timeout`/`--retries`；本地 Ollama 需 `ollama pull` 且在 `/v1` 提供 OpenAI 兼容接口 |
| PDF 整份走视觉模型 | 未装 `pymupdf`，或确为扫描件；`python -m pip install pymupdf` |
| 启动器找不到 Python | 装 Python 3.9+，或把 `python.exe` 加入 PATH |

## 通用性

启动器按优先级查找 Python：`py -3` → `%LOCALAPPDATA%\Programs\Python\Python3*` → `C:\Python3*` → `python3.12`/`python3`/`python`。换电脑换人，只要装了 Python 3.9+ 就能跑，自动装可选依赖。

## 安全

- 只调用**你配置的端点**，不发送数据到任何第三方。
- 涉及敏感内容（身份证/合同等），选本地视觉模型（如 Ollama + qwen2.5vl），数据不出本机。
- `config.json` 含密钥，切勿入库。

## License

MIT