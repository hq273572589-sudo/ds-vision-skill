#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ZCode UserPromptSubmit 钩子：向每个用户消息注入企业规范摘要。

协议：stdin 收到事件 JSON（含 prompt 字段），stdout 输出 JSON {"additionalContext": "..."}
即可把内容注入对话开头；出错一律静默（exit 0，绝不阻断会话）。
"""
import json
import os
import re
import sys

RED_LINE_JAVA = (
    "本任务遵循 company-standards 技能（滨海湾 Java 后端规范）。红线：禁 SELECT*、"
    "SQL 参数必须 #{} 禁 ${}、统一返回 ResponseJson<T>、业务异常抛 BusinessException、"
    "禁魔法数字/裸状态字面量；表 t_ 前缀、主键 varchar(32) UUID、逻辑删除 isdeleted。"
    "完整规范见技能 references/java-backend-规范.md，不确定时务必回查，不要凭记忆。"
)

RED_LINE_FRONTEND = (
    "本任务遵循 company-standards 技能（滨海湾前端规范）。红线：Vue3 <script setup> + "
    "Element Plus / uni-app + uView、禁滥用 any、defineProps/defineEmits 带泛型、"
    "样式 <style scoped> 或 CSS Modules 隔离、主色调浅蓝。"
    "完整规范见技能 references/frontend-规范.md，不确定时务必回查，不要凭记忆。"
)

DEV_KEYWORDS = re.compile(
    r"(java|spring|mybatis|sql|查询|表|字段|索引|接口|controller|service|mapper|实体|bean|"
    r"vue|element|uni-app|前端|后端|页面|组件|typescript|pinia|axiox*|axios|"
    r"代码|实现|开发|修改|新增|重构|优化|测试|提交|commit|bug|接口文档|升级|部署|"
    r"抽象|工具类|枚举|数据库|表设计|事务|缓存|redis|消息队列|定时任务|权限|登录)",
    re.IGNORECASE,
)


def main() -> int:
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8")

        raw = sys.stdin.read() or ""
        prompt = raw
        try:
            payload = json.loads(raw)
            if isinstance(payload, dict):
                prompt = payload.get("prompt") or payload.get("userPrompt") or raw
        except Exception:
            pass

        project_dir = (
            os.environ.get("ZCODE_PROJECT_DIR")
            or os.environ.get("CLAUDE_PROJECT_DIR")
            or os.getcwd()
        )
        name = os.path.basename(os.path.normpath(project_dir)).lower()

        has_pom = os.path.isfile(os.path.join(project_dir, "pom.xml"))
        has_package_json = os.path.isfile(os.path.join(project_dir, "package.json"))
        is_company_dir = bool(re.search(r"(bhw|smr|滨海湾|风华苑)", name))

        dev_task = bool(DEV_KEYWORDS.search(prompt or ""))

        # 公司/Java 项目：每次消息都提醒（用户要求"每轮强制可见"）
        if has_pom:
            inject = RED_LINE_JAVA
        # 纯前端项目：走前端规范
        elif has_package_json and not has_pom:
            inject = RED_LINE_FRONTEND
        # 无法识别项目类型但目录像公司项目且话题是开发相关
        elif is_company_dir and dev_task:
            inject = RED_LINE_JAVA if "java" in prompt.lower() or "后端" in prompt else RED_LINE_FRONTEND
        else:
            inject = None

        if not inject:
            return 0

        sys.stdout.write(json.dumps({"additionalContext": inject}, ensure_ascii=False))
        return 0
    except Exception:
        # 任何异常都不能阻断会话
        return 0


if __name__ == "__main__":
    sys.exit(main())