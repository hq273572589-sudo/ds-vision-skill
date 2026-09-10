---
name: company-standards
description: 滨海湾企业内部开发规范（Java 后端 + 前端）。当任务涉及公司业务项目（bhw_*、smr-data 等仓库）、或在编写/修改/评审 Java 后端代码（Spring Boot 3.x、MyBatis-Plus）、前端代码（Vue 3、Element Plus、uni-app、TypeScript），或涉及数据库表设计/SQL、接口设计、异常处理、日志、缓存、Redis、MQ、定时任务、单元测试（JUnit5/Mockito）、Git 提交信息、命名规范、目录结构时，必须先加载本技能并按 references 中的规范执行。规范文件按需读取：Java 见 references/java-backend-规范.md，前端见 references/frontend-规范.md，项目规范见 references/project-agents-template.md。
---

# 滨海湾企业开发规范（Company Standards）

企业级开发规范，适用于所有公司业务项目（Java 后端 + 前端）。所有公司项目代码的编写、修改、评审必须遵守本技能中的规范。

## 使用方式

1. 加载本技能后，**按需读取**对应规范文件（不要一次性全塞进上下文）：
   - Java 后端：`references/java-backend-规范.md`（公司规范）
   - Java 补充：`references/java-backend-补充-阿里手册.md`（阿里《Java 开发手册》强制级精选：并发/集合/OOP/异常日志/SQL 深化）
   - 前端：`references/frontend-规范.md`（公司规范）
   - 前端补充：`references/frontend-补充-vue官方指南.md`（Vue 官方风格指南 Priority A/B + TS 严格规则）
2. 冲突裁决：**公司规范 > 补充规范 > 常识**；公司规范未覆盖的领域按补充规范执行。
3. 按规范执行任务；**不确定时回查 references 文件，不要凭记忆**（防幻觉）。
4. 涉及具体公司项目时，同时遵守该项目仓库根目录的 AGENTS.md —— **项目级规则优先于本技能默认值**（每个项目可覆盖全局约定）。

## 核心红线（违反即返工）

### Java 后端（红线速查）

- 禁止 `SELECT *`；禁止手动拼接 SQL；参数必须 `#{}`，禁用 `${}`；少用 `WHERE 1=1`（用 `<where>`）。
- 禁止魔法数字与裸状态字面量，一律用枚举/常量类。
- Controller 内禁止 try-catch 拼错误响应；可预期失败统一 `throw new BusinessException(...)`；全局用 @RestControllerAdvice。
- 统一返回 `ResponseJson<T>`（code/message/data）；分页 bean 继承 BasePageModel；业务 bean 继承 BaseModel 并带类说明与参数说明。
- 命名：数据库表 `t_` 前缀小写下划线（t_sys_user）；索引 `idx_表_字段` / `uk_表_字段`；枚举 `Enum` 结尾放 `enums` 包；工具类 `Utils` 结尾；数据对象 `Cmd/Query/VO` 后缀；方法 CRUD 用 get/list/count、save/update/delete。
- 数据库字段：主键 varchar(32) UUID；逻辑删除统一 `isdeleted` 默认 0；金额 decimal(10,2) BigDecimal；时间 TIMESTAMP + LocalDateTime。
- 依赖注入用构造器注入，优先接口而非实现类；覆写方法必须加 @Override。
- 注释用中文 Javadoc；TODO/FIXME 必须带作者和日期：`// TODO(zhangsan, 2026-08-12)`。
- 单元测试：命名 `test_方法名_场景_预期结果`，核心业务覆盖率 ≥ 70%，@Mock/@Spy 模拟外部依赖。
- 提交信息用 Conventional Commits（feat/fix/docs/style/refactor/test/chore）。
- 并发（补充）：线程一律走 ThreadPoolExecutor 手动创建的线程池并命名，禁止 Executors 与显式 new Thread；ThreadLocal 用完 remove；SimpleDateFormat 禁 static。
- 集合（补充）：foreach 内禁 remove/add；Arrays.asList 与不可变集合禁改；包装类比较用 equals。
- SQL 深化（补充）：JOIN ≤ 3 表（公司上限 5）；禁外键级联、禁存储过程；COUNT(*) 统计；update/delete 前先 SELECT；分页 LIKE '%xx' 禁止。

### 前端（红线速查）

- PC 端：Vue 3（Composition API + `<script setup>`）+ Element Plus + TypeScript + Vite；移动端/小程序：uni-app + uView（或 uView Pro）。
- 禁止滥用 `any`，必须定义明确 Interface/类型守卫；defineProps/defineEmits 必须携带泛型参数。
- 样式必须 `<style scoped>` 或 CSS Modules 隔离；全局主色调统一浅蓝色。
- 状态管理 Pinia 按业务模块划分；Axios 统一封装（Token 注入、统一错误、超时）。
- 目录结构按规范：api/assets/components/views/stores/utils/types。
- 文件名/变量小驼峰，工具/路由文件 kebab-case，常量全大写+下划线；ESLint + Prettier（单引号、2 空格、末尾逗号）。
- 环境变量 `VITE_` 前缀 + `import.meta.env`；配置文件需支持动态识别 IP/端口。
- Vue 官方 A 级（补充）：组件名多单词；v-for 必绑 key（禁 index）；禁 v-if 与 v-for 同元素；props 带类型。
- Vue 官方 B 级（补充）：基础组件 Base 前缀、单例组件 The 前缀；模板表达式简单化；多属性每行一个；reactive 禁解构。

## 完整规范

- Java 后端（数据库/代码/接口/异常/安全/命名/日志/缓存/MQ/定时任务/测试/审查/依赖/框架模块/技术栈）：见 `references/java-backend-规范.md`
- Java 补充（阿里手册强制级精选：并发/集合/OOP/异常日志/MySQL 深化/依赖安全）：见 `references/java-backend-补充-阿里手册.md`
- 前端（技术栈/目录/编码/TS/UI 样式/性能/环境变量/动态配置）：见 `references/frontend-规范.md`
- 前端补充（Vue 官方风格指南 A/B 级 + Vue3 script setup 规则 + TS 严格规则）：见 `references/frontend-补充-vue官方指南.md`

## 新项目落地

把 `references/project-agents-template.md` 复制到公司项目仓库根目录命名为 `AGENTS.md`，按项目情况补充"项目特有约定"，将公司规范锚定到该仓库。