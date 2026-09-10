# AGENTS.md — 滨海湾公司项目模板

本仓库属于滨海湾公司业务项目。除下列「项目特有约定」外，一律遵守公司统一规范：
加载 `company-standards` 技能，按需读取 `references/java-backend-规范.md`（Java 后端）与 `references/frontend-规范.md`（前端）。

## 项目特有约定

> 每个项目在这里覆盖/补充全局规范，例如：

- **项目说明**：（一句话描述该系统）。
- **模块划分**：（按公司规范 basecore/file_server/_hub/_adapt/_auth/_gateway 之外的差异说明）。
- **模块/表前缀**：（如 t_bhw_xxx、bhw_）。
- **特有命名/接口约定**：（如 URL 前缀、特定包装类、特殊枚举）。
- **部署/上线注意事项**：（构建命令、环境变量、IP/端口动态识别配置等）。

## 通用硬性要求（摘要；完整版以 company-standards 为准）

Java 后端：
- 禁止 SELECT * / 手动拼接 SQL；参数必须 #{}；统一返回 ResponseJson<T>；业务异常抛 BusinessException。
- 禁止魔法数字；逻辑删除字段统一 isdeleted；主键 varchar(32) UUID；金额 decimal(10,2)。
- 命名按公司规范（t_ 前缀、Enum/Utils/VO/Query/Cmd 后缀等）；构造器注入；@Override 必须加。

前端：
- Vue 3 + `<script setup>` + Element Plus / uni-app + uView；禁止滥用 any；样式 scoped 隔离；主色调浅蓝色。
- 目录结构按规范（api/assets/components/views/stores/utils/types）。

## 验收清单（每次代码改动必须全绿）

- [ ] 后端 `mvn compile` / 前端构建通过
- [ ] 相关单元测试通过（核心业务覆盖率 ≥ 70%）
- [ ] 符合公司命名/注释/日志规范，无敏感信息入日志
- [ ] Commit message 符合 Conventional Commits
- [ ] （后端）无魔法数字、无 SELECT *、无手动拼接 SQL