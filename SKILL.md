---
name: vision-bridge
description: 为不支持视觉的模型（如 DeepSeek 文本模型）把图片、PDF、扫描件、Word/Excel/PPT 等文件内容识别并转成文本，再供当前模型使用。当用户上传图片（截图/照片/图表/流程图/二维码/表情包）、PDF、文档并希望读取其内容时，务必使用本技能。即使当前模型无法直接"看"图像，也要通过本技能的桥接脚本把非文本内容转为文本。也用于图片 OCR、扫描件 PDF 转文字、从图片/文档中提取信息、把图片表格转成 markdown 等场景。
---

# vision-bridge

把 **图片 / PDF / Office 文档** 的内容识别为文本，桥接给不支持视觉的模型使用。

## 使用前：首次必须配置视觉模型
1. `cp scripts/config.example.json scripts/config.json`
2. 编辑 `scripts/config.json`：`base_url`（OpenAI 兼容 `/v1` 端点）、`api_key`（你的 Key）、`model`（**必须支持图片**，如 `qwen2.5vl` / `llava` / `gpt-4o`）。

> 注意：`scripts/config.json` 已被 `.gitignore` 排除，请勿包含密钥到仓库/提交。

## 调用
- Windows：`run_vision_bridge.bat <文件>`
- 直接：`python scripts/read_content.py <文件>`
- 图片 → 视觉模型识别；PDF/Office → 优先本地提取（需 `pymupdf/python-docx/openpyxl/python-pptx`），扫描无文本页则走视觉模型。

## 参数
`--lang en` / `--list-models` / `--configure` / `--check` / `--timeout 120` / `--retries 3`