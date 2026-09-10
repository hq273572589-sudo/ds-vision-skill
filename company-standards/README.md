# company-standards：滨海湾企业开发规范技能

> 滨海湾公司 Java 后端 + 前端开发规范，封装为标准 Agent Skill（SKILL.md 格式），
> 兼容 ZCode / Claude Code / Codex 等支持技能目录的编码代理。

## 目录结构

```
company-standards/
├── SKILL.md                                  # 技能入口 + 核心红线速查（含冲突裁决顺序）
└── references/
    ├── java-backend-规范.md                  # 公司 Java 后端规范（数据库/代码/接口/异常/安全/命名/日志/缓存/MQ/测试/审查/依赖/模块）
    ├── java-backend-补充-阿里手册.md          # 阿里《Java 开发手册》强制级精选（并发/集合/OOP/异常日志/SQL 深化/依赖安全）
    ├── frontend-规范.md                      # 公司前端规范（Vue3/uni-app/TS/目录/UI/性能/环境变量/动态配置）
    ├── frontend-补充-vue官方指南.md           # Vue 官方风格指南 Priority A/B + Vue3 script setup + TS 严格规则
    └── project-agents-template.md            # 项目级 AGENTS.md 模板（复制到公司仓库根目录按项目补充）
```

## 冲突裁决顺序

**项目 AGENTS.md > 公司规范 > 补充规范（阿里/Vue 官方）> 常识**

## 安装（其他电脑）

1. 把 `company-standards/` 文件夹复制到目标机器的技能目录：
   - ZCode：`C:\Users\<你>\.zcode\skills\company-standards`
   - Claude Code：`~/.claude/skills/company-standards`
   - Codex：`~/.codex/skills/company-standards`
2. 重启会话（技能在会话启动时扫描加载）。

## 配套：UserPromptSubmit 钩子（常驻注入红线）

`../hooks/inject-standards.py` 配合钩子配置，可在**每次用户发消息时**自动注入一两行
当前项目规范摘要（Java 项目注入后端红线、前端项目注入前端红线），对抗长上下文遗忘：

- 检测逻辑：工作目录有 `pom.xml` → Java 红线；有 `package.json` → 前端红线；其他情况零开销。
- 注册方式（ZCode 为例，`~/.zcode/cli/config.json` 的 `hooks` 键）：

```json
"hooks": {
  "enabled": true,
  "timeoutMs": 10000,
  "events": {
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "process",
            "command": "C:\\Python312\\python.exe",
            "args": ["C:\\Users\\<你>\\.zcode\\hooks\\inject-standards.py"],
            "timeoutMs": 5000
          }
        ]
      }
    ]
  }
}
```

> 把 `command` 换成目标机器的 Python 3 路径、`args` 换成脚本实际路径即可。

## 新项目落地

复制 `references/project-agents-template.md` 到公司项目仓库根目录，重命名为 `AGENTS.md`，
补充"项目特有约定"（模块前缀、URL 风格、部署要点等）。项目级规则优先于本技能默认值。
