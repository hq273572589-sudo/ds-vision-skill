# 前端补充规范（来源：Vue 官方风格指南 Priority A/B + TypeScript 严格规则）

> 本文是公司规范（`frontend-规范.md`）的**补充**，两者冲突时以公司规范为准。
> 来源：Vue 官方 Style Guide（vuejs.org/style-guide）Priority A（Essential，防错误）与
> Priority B（Strongly Recommended，可读性），及社区共识的 TS 严格规则。

## 1. Priority A：防错误（Essential，必须遵守）

- **组件名多单词**：组件名必须多单词（如 `UserProfile`、`TodoItem`），禁止单单词（`User`、`Todo`），防止与原生 HTML 元素冲突。[Vue A]
- **组件 data 必须是函数**：`data` 必须返回对象的函数（`<script setup>` 中天然满足）；禁止共享对象引用。[Vue A]
- **Prop 必须完整定义**：禁止裸数组定义 props，必须带类型（公司规范已定 defineProps 泛型参数）。[Vue A]
- **v-for 必须绑定 key**：key 用稳定唯一 id，禁止用数组 index（列表变动会错位复用）。[Vue A]
- **禁止 v-if 与 v-for 同元素连用**：v-for 优先级高于 v-if，会全量遍历后过滤；必须先用 computed 过滤数据源。[Vue A]
- **组件样式必须隔离**：`<style scoped>` 或 CSS Modules（公司规范已定）。[Vue A]
- **私有属性命名**：插件/mixin 自定义属性加前缀（如 `$` 或项目统一前缀），避免与组件属性冲突。[Vue A]

## 2. Priority B：强推（Strongly Recommended）

- **单文件组件文件名**：要么全大驼峰（`UserProfile.vue`），要么全 kebab-case（`user-profile.vue`）——公司规范已定小驼峰视图文件 + kebab-case 工具文件，冲突时按公司规范；但**同一项目内必须统一一种**，禁止混用。[Vue B]
- **基础组件命名**：通用基础组件用 `Base`/`App`/`V` 前缀（`BaseButton.vue`、`BaseModal.vue`），便于按序归组、按需引入。[Vue B]
- **单例组件命名**：全局唯一组件用 `The` 前缀（`TheHeader.vue`、`TheSidebar.vue`）。[Vue B]
- **组件名用完整单词**，禁止自造缩写。[Vue B]
- **模板中组件名用 PascalCase**（`<UserProfile />`）或统一 kebab-case，禁止混用；自闭合组件写法 `<MyComponent />`。[Vue B]
- **Prop 命名 camelCase，模板绑定 kebab-case**：`props: { greetingText }` ↔ `<Greeting greeting-text="hi" />`。[Vue B]
- **多属性元素每个属性独占一行**，便于阅读 diff。[Vue B]
- **模板表达式保持简单**：复杂逻辑抽为 computed 或方法，禁止在模板里写超过一行的表达式。[Vue B]
- **简单 computed**：一个 computed 只做一件事，复杂 computed 拆分。[Vue B]
- **属性值必须带引号**：`:style="{ width: '10px' }"`，禁止裸值。[Vue B]
- **指令简写统一**：全用 `:` / `@` 或全用 `v-bind:` / `v-on:`，禁止混用。[Vue B]

## 3. Vue 3 / `<script setup>` 专属规则（结合公司栈）

- 组件选项顺序（内部代码组织）：`defineProps → defineEmits → 响应式状态 → computed → 方法 → 生命周期钩子`，保持一致。
- `v-for` 遍历对象时 key 顺序敏感，尽量避免；遍历数组优先。
- `defineProps`/`defineEmits` 用类型泛型声明（公司规范已定），且 props 必须 `withDefaults` 或可选标记默认值。
- `ref`/`reactive` 选择：基本类型与简单对象用 `ref`；`reactive` 禁止解构（丢响应式），需要解构用 `toRefs`。
- 组件间通信：父子 props/emit；跨层 provide/inject 只用于库类场景；**禁止 $parent/$children 链式访问**（官方 D 级警告）。[Vue D]
- 全局状态只放 Pinia store；组件私有状态禁止塞进全局 store。[Vue D]
- `scoped` 内禁止用元素选择器做根级样式（性能与覆盖范围问题），用类名选择器。[Vue D]

## 4. TypeScript 严格规则（补充）

- **禁止滥用 any**（公司规范已定）：确需逃生舱用 `unknown` + 类型收窄，或 `as never`/具体联合类型；禁止 `as any` 链式规避。
- 接口/类型二选一并保持一致：对外 API 数据结构用 `interface`，工具类型用 `type`。
- 枚举用 `const enum` 或字符串字面量联合类型；**禁止数字魔法枚举散落**（对应后端枚举值统一放 `src/types/` 或 `src/enums/`）。
- API 响应必须定义类型：配合后端 ResponseJson 统一封装 `ApiResponse<T>` 泛型（code/message/data），禁止裸 `Promise<any>`。
- 函数返回值公开 API 必须显式标注；导出函数/组件 props 必须类型完整。
- 空值判断用 `??` 与 `?.`，禁止用 `||` 兜底非布尔值（0/空串会误判）。

## 5. 工程化硬约束（结合公司规范）

- ESLint 必须含 `vue/recommended`（官方推荐规则集）与 `@typescript-eslint/recommended`；Prettier 单引号、2 空格、末尾逗号（公司规范已定）。
- 组件文件放 `src/components/`（全局）或页面就近 `components/`（页面私有），禁止页面巨型单文件超过 ~500 行不拆分。
- 路由懒加载（公司规范已定 `() => import(...)`）；异步组件用 `defineAsyncComponent`。
- 环境变量 `VITE_` 前缀 + `import.meta.env`（公司规范已定）；API 地址动态识别（公司规范已定）。
- 小程序端 DOM 层级 ≤ 8 层（公司规范已定）；图片统一走文件服务 URL/id（后端规范联动）。
