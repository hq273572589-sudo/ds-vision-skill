# 滨海湾前端开发规范

> 本文件由公司《前端代码开发规范》整理（还原了被 HTML 剥离的 `<script setup>` / `<style scoped>` 标签，内容保持一致）。

## 1. 技术栈与核心框架规范

- **PC 端项目**：采用 Vue 3（推荐开启 Composition API + `<script setup>` 语法）+ Element Plus + TypeScript + Vite 构建工具。
- **移动端/小程序项目**：采用 uni-app（Vue 3 版本）+ uView（或 uView Pro）+ TypeScript 框架及组件。
- **状态管理**：统一采用 Pinia，支持 TypeScript 原生集成，按业务模块划分 Store。
- **路由管理**：PC 端采用 Vue Router 4，开启 history 模式；uni-app 端遵循其内置的 pages.json 路由配置规范。
- **网络请求**：统一封装 Axios，配置全局请求/响应拦截器（处理 Token 注入、统一错误提示、接口超时等）。
- **运行环境**：Node.js 版本要求 20.0 及以上，包管理器推荐使用 pnpm。

## 2. 目录结构规范

建立清晰的工程化目录结构，确保代码的高可维护性：

- `src/api/`：按业务模块拆分接口请求（如 user.ts, order.ts）。
- `src/assets/`：存放需打包的静态资源（图片、全局样式等）。
- `src/components/`：存放全局通用组件（如按钮、弹窗），建议采用小驼峰命名，首字母小写如：userProfile。
- `src/views/`（或 `src/pages/`）：存放路由级页面组件。
- `src/stores/`（或 `src/store/`）：存放 Pinia 状态管理模块。
- `src/utils/`：存放纯工具函数（如格式化、防抖节流、权限校验）。
- `src/types/`：集中存放 TypeScript 类型定义（interfaces, enums）。

## 3. 编码与 TypeScript 规范

- **语法要求**：TypeScript，禁止滥用 any 类型，必须定义明确的接口（Interfaces）或类型守卫。
- **组件规范**：优先使用 Vue 3 Composition API 与 `<script setup>` 语法；defineProps 和 defineEmits 必须携带泛型参数。
- **命名规范**：
  - 文件名/变量/函数：采用小驼峰（如 userProfile.vue, userName）；
  - 工具/路由文件采用 kebab-case（如 user-profile.ts）；
  - 常量：全大写加下划线（如 MAX_COUNT）。
- **代码格式化**：统一集成 ESLint + Prettier，字符串统一使用单引号，多行对象/数组末尾添加逗号，缩进统一为 2 空格。

## 4. UI 设计与样式规范

- **主色调**：PC 端与移动端/小程序端全局主色调统一为浅蓝色，如有行业特殊要求再另行确定。
- **样式隔离**：Vue 组件中必须使用 `<style scoped>` 或 CSS Modules，避免全局样式污染。

## 5. 性能与工程化优化

- **PC 端优化**：路由采用懒加载（`() => import('...')`）；Element Plus 等 UI 库配置自动按需引入，减小打包体积。
- **移动端/小程序优化**：
  - 严格控制 DOM 嵌套层级（建议 ≤ 8 层），以贴合小程序原生渲染引擎规则；
  - 非首屏业务组件采用异步按需引入，减轻首屏渲染压力。

## 6. 环境变量与配置

- 使用 `.env.dev` 和 `.env.production` 区分开发与生产环境配置。
- Vite 环境变量必须以 `VITE_` 为前缀，通过 `import.meta.env` 访问。

## 7. 动态配置要求

配置文件要做成动态配置的：本地的时候就按本地来，部署到服务器就自动识别 IP 和端口，不需要每次换服务器就重新打包。
