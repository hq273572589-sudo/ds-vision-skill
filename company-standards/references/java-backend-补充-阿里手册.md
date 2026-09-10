# Java 补充规范（来源：阿里巴巴《Java 开发手册》强制级规则精选）

> 本文是公司规范（`java-backend-规范.md`）的**补充**，两者冲突时以公司规范为准。
> 规则精选自 alibaba/p3c《Alibaba Java Coding Guidelines》【Mandatory/强制】级（30,850+⭐），
> 只收录公司规范未覆盖、且对 AI 编码防幻觉最有价值的条目。来源标注 [P3C]。

## 1. 命名与 POJO（补充）

- boolean 变量**禁止加 is 前缀**（部分框架序列化会出异常）；DB 布尔列可命名 `is_xxx`，但 POJO 属性不带 is 前缀，需做映射。[P3C]
- Service/DAO 类必须是接口，实现类以 `Impl` 结尾。[P3C]
- long/Long 赋值用大写 `L`，禁止小写 `l`（易与 1 混淆）。[P3C]
- POJO 类（DO/DTO/VO）属性**不要设默认值**；必须实现 `toString()`；序列化类更新时不得修改 `serialVersionUID`。[P3C]
- 构造方法里禁止业务逻辑，初始化放 `init()` 方法。[P3C]
- 包名统一小写、单数；类名可复数。[P3C]

## 2. OOP 与相等判断（补充）

- 包装类比较必须用 `equals()`，禁止 `==`（缓存区间外 `==` 恒为 false）。[P3C]
- `equals` 由常量或确定非 null 的对象调用，防 NPE：`"str".equals(var)` 或 `Objects.equals(a, b)`。[P3C]
- 浮点数判等：基本类型禁 `==`，包装类禁 `equals`，应指定误差范围比较；金额一律 BigDecimal（公司规范已定 decimal(10,2)）。[P3C]
- 所有 POJO 类属性必须用包装数据类型；RPC 方法返回值和参数必须用包装类型；局部变量推荐基本类型。[P3C]
- 禁止使用已 `@Deprecated` 的类与方法；禁止为规避调用方影响而改方法签名，废弃要加 @Deprecated 并说明替代方案。[P3C]
- 获取当前毫秒用 `System.currentTimeMillis()`，禁止 `new Date().getTime()`。[P3C]

## 3. 集合处理（补充，公司规范空白）

- 禁止在 foreach 循环里对集合做 remove/add，删除用 `Iterator`（并发场景需加锁）。[P3C]
- `Arrays.asList()` 得到的列表禁止 add/remove/clear（UnsupportedOperationException）。[P3C]
- 禁止向 `keySet()/values()/entrySet()`、`Collections.emptyList()/singletonList()` 等不可变集合添加元素。[P3C]
- `subList` 禁止强转 ArrayList；对原列表做结构性修改会导致 subList 遍历异常。[P3C]
- 转 数组用 `toArray(T[] array)`，传入与 `list.size()` 一致的数组。[P3C]
- `Comparator` 必须满足自反性/传递性/对称性，否则 sort 抛 IllegalArgumentException。[P3C]

## 4. 并发处理（补充，公司规范空白）

- **禁止显式创建线程**，一律通过线程池；线程池必须用 `ThreadPoolExecutor` 手动创建，**禁止 `Executors`** 快捷工厂（FixedThreadPool/SingleThreadPool 无界队列 OOM、CachedThreadPool 线程数无上限）。[P3C]
- 线程/线程池必须指定有意义的名字，便于排查问题。[P3C]
- `SimpleDateFormat` 线程不安全，禁止定义为 static；用 `DateTimeFormatter` 或加锁。[P3C]
- `ThreadLocal` 用完必须 `remove()`，尤其线程池复用场景。[P3C]
- 定时任务用 `ScheduledExecutorService`，禁止 `Timer`（异常会杀掉全部线程）。[P3C]
- 多资源加锁时保持全局一致加锁顺序，避免死锁；锁块优于锁方法，对象锁优于类锁。[P3C]
- 并发修改同一记录必须加锁（应用层/缓存/数据库乐观锁 version），否则更新丢失。[P3C]
- 单例的初始化与所有方法必须保证线程安全。[P3C]

## 5. 控制语句与注释（补充）

- switch 每个 case 必须 break/return 收尾，且必须有 default。[P3C]
- if/else/for/do/while 即使单语句也必须加大括号；嵌套条件不超过 3 层。[P3C]
- 正则表达式必须预编译（`Pattern.compile` 放类常量），禁止在循环里重复 compile。[P3C]
- Javadoc 只用 `/** */`；抽象方法（含接口方法）必须 Javadoc 说明参数/返回值/异常；枚举字段必须注释；类必须有作者与日期（公司规范已定中文注释）。[P3C]

## 6. 异常与日志（补充）

- 禁止捕获 JDK 预定义的 RuntimeException（NPE、越界等）掩盖问题，应提前判空/检查；禁止用异常做流程控制；禁止对大段代码 try-catch。[P3C]
- 禁止吞异常：不处理就向上抛，最外层负责转成用户可理解的信息；事务方法抛异常必须保证回滚。[P3C]
- 可关闭资源（流/连接）必须在 finally（或 try-with-resources）中关闭；finally 禁止 return（会吞异常和返回值）。[P3C]
- 日志一律走 SLF4J 门面，禁止直接用 Log4j/Logback API。[P3C]
- TRACE/DEBUG/INFO 级日志必须用占位符或条件开关：`log.debug("id={}", id)`，禁止字符串拼接。[P3C]
- 日志要同时输出上下文信息与异常堆栈，二者缺一不可。[P3C]
- 结合公司规范：日志 ≥15 天保留、敏感信息（密码/身份证/银行卡）禁止落日志并脱敏。

## 7. MySQL/SQL 规则（补充；公司数据库为 PostgreSQL，规则通用）

- 布尔概念列命名 `is_xxx`（公司规范已定 isdeleted，冲突时按公司规范）。[P3C]
- 表名/列名小写字母+数字+下划线，禁止复数名词表名，禁用保留字（desc/range/match 等）。[P3C]
- 小数一律 decimal，禁止 float/double 存金额。[P3C]
- varchar 超过 5000 改用 text 并独立成表。[P3C]
- 表必备三字段：`id`、`gmt_create`、`gmt_modified`（公司项目可用 created_at/updated_at 等既有约定，但必须统一）；更新记录必须同步更新修改时间字段。[P3C]
- **JOIN 不超过 3 张表**（公司规范为 5 张以内，按公司规范执行），关联字段类型一致且有索引。[P3C]
- 分页搜索禁止 `LIKE '%xx'`/`'%xx%'`（索引失效），确需走搜索引擎。[P3C]
- 统计行数用 `COUNT(*)`（SQL92 标准），禁止 COUNT(列名)/COUNT(常量) 代替。[P3C]
- 分页查询 count 为 0 应立即返回，不再执行分页查询。[P3C]
- **禁止外键与级联更新**，外键逻辑在应用层保证。[P3C]
- **禁止存储过程**（难调试、难扩展、不可移植）。[P3C]
- update/delete 前必须先 SELECT 确认数据（公司规范同款红线，生产环境尤其）。[P3C]
- 禁止用 HashMap/HashTable 作为 DB 查询结果接收类型，必须定义对应 DO。[P3C]
- ORM 框架配置里禁用 `${}` 传参（公司规范已定 `#{}`）。[P3C]

## 8. 依赖与安全（补充）

- 线上应用禁止依赖 SNAPSHOT 版本；同 GroupId+ArtifactId 的版本在各子模块必须一致；版本号用属性变量统一管理（公司规范已定）。[P3C]
- 库中枚举可用于参数类型，禁止用于接口返回类型（含含枚举的 POJO）。[P3C]
- 用户页面/功能必须鉴权（公司 RBAC 已定）；用户输入一律校验；输出到 HTML 前必须转义/过滤（防 XSS，公司规范已定）；表单与 AJAX 提交必须 CSRF 校验。[P3C]
- 用户提交的 SQL 参数必须校验/白名单限制，禁止拼接 SQL（公司规范已定 #{}）。[P3C]
- 反爬/防滥用：接口做频次限制、验证码等防重放措施（公司 sign+timestamp 已定）。[P3C]
