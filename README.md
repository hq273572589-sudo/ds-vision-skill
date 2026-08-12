# ds-vision-skill（Vision Bridge）

把 **图片 / PDF / 扫描件 / Word / Excel / PPT** 等内容识别为纯文本，桥接给**不支持视觉**的模型使用（例如 DeepSeek 文本模型）。它调用一个 **OpenAI 兼容的视觉端点**（Ollama / one-api / SiliconFlow / vLLM 等，支持图片输入的模型）做识别，再把文本结果返回给调用它的模型。

## ⚠️ 安全说明（必读）
- 本仓库**不包含任何真实 API Key / 令牌**。
- `scripts/config.json`（含你的 Key）已被 `.gitignore` 排除，**切勿**手动把它提交到仓库 / 提交你的密钥。

## 1. 安装
克隆或下载本仓库，放到下列任一 skill 目录均可：
- Codex: `C:\Users\<you>\.codex\skills\vision-bridge`
- Claude Code: `C:\Users\<you>\.claude\skills\vision-bridge`
- 或任意自用目录随意运行

## 2. 首次使用：必须先配置视觉模型
1. 复制 `scripts\config.example.json` 为 `scripts\config.json`
   - Windows: `copy scripts\config.example.json scripts\config.json`
   - Linux/macOS: `cp scripts/config.example.json scripts/config.json`
2. 编辑 `scripts\config.json`，填三样：
   ```json
   {
     "base_url": "https://your-gateway.example.com/v1",
     "api_key": "sk-你的视觉模型Key",
     "model": "支持图片的模型名"
   }
   ```
   - `base_url`：OpenAI 兼容端点，结尾要带 `/v1`（Ollama 本地示例 `http://localhost:11434/v1`）。
   - `model`：必须是**支持图片输入**的视觉模型（如 `qwen2.5vl` / `llava` / `gpt-4o` / `gemini-2.0-flash` 等）。纯文本模型会报 `unknown variant image_url`。
3. 配置好即可用。

## 3. 使用
- Windows 启动器：`run_vision_bridge.bat <文件路径>`
- 直接命令（Linux/macOS 或 conda 环境）：`python scripts\read_content.py <文件路径>`

常用参数：
- `--lang en`：识别语言用英文（默认中文）
- `--list-models`：列出端点可用模型，便于挑选视觉模型
- `--configure`：重新配置端点
- `--timeout 120` / `--retries 3`
- `--check`：只检查本地提取依赖

## 4. 常见问题
- `unknown variant image_url` → 当前 `model` 是纯文本模型，换成支持图片的视觉模型。
- `401/403` → `api_key` 无效或未填。
- 想要 PDF/Office 本地快速提取：`python -m pip install pillow pymupdf python-docx openpyxl python-pptx`（图片始终可用）。

## 5. 许可证
MIT