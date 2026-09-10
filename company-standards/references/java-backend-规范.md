# 滨海湾 Java 后端开发规范

> 本文件由公司《滨海湾JAVA后端开发规范》整理（去除 Word 导出噪声，内容保持一致）。

## 1. 研发规范

### 1.1 数据库规范

#### 1.1.1 字段属性

- **主键 ID**：使用 varchar(32) 存储，采用 UUID 方式生成。例如：`String id = CommonUtils.getUUID();`
- **枚举类字段**：使用 int4 存储，数字对应枚举值（例如：0-未删除，1-已删除）。
- **时间类型**：使用 TIMESTAMP，后端使用 java.time.Date | LocalDateTime。
- **长数字**：使用 int8 存储，对应后端 Long 类型。
- **经纬度**：使用 numeric(10,6) 存储，对应后端 Double 类型。
- **富文本**：使用 Text 类型，方便存储大文本内容。
- **字符串长度**：使用 varchar 时，必须标明长度，防止出现不可控存储异常。
- **金额字段**：使用 decimal(10,2) 存储，对应后端 BigDecimal。
- **逻辑删除字段**：统一命名为 isdeleted，默认值为 0。

#### 1.1.2 索引使用

- **合理创建索引**：避免不走索引的情况。LIKE 右匹配（%xx）、对索引列使用函数或隐式转换都会导致索引失效。
- **避免过度索引**：联合查询 JOIN 的表数量尽量控制在 5 个以内。
- **索引设计原则**：联合索引遵循最左前缀原则；唯一索引用于业务唯一性约束；索引字段选择区分度高的列。
- **索引命名规范**：普通索引 `idx_user_phone`，唯一索引 `uk_user_email`。
- **慢查询分析**：定期使用 EXPLAIN 分析慢查询，重点关注 type、key、rows、Extra 字段。

### 1.2 代码规范

#### 1.2.1 查询规范

- **禁止 SELECT \***：必须显式列出需要的列名，多表查询时列名需加别名。
- **禁止手动拼接 SQL**：利用 MyBatis 等 ORM 框架的动态 SQL 实现，参数必须使用 `#{}` 避免 SQL 注入，禁用 `${}` 方式进行查询。
- **尽量减少动态拼接 WHERE 1=1**：使用 MyBatis 动态 SQL 标签（如 `<where>`）实现。
- **分页查询**：使用统一分页框架 `com.baomidou.mybatisplus.core.metadata.IPage`。
- **批量操作**：使用批量 SQL，避免在循环中执行单条 SQL。

  ```xml
  <!-- MyBatis 批量插入示例 -->
  <insert id="batchInsert" parameterType="java.util.List">
    INSERT INTO sys_user (id, user_name, age) VALUES
    <foreach collection="list" item="item" separator=",">
      (#{item.id}, #{item.userName}, #{item.age})
    </foreach>
  </insert>
  ```

- **复杂查询**：考虑使用视图或物化视图，减少应用层计算压力。
- **基础 SQL**：尽量使用基础 SQL 语句进行业务实现，少用特定数据库独有方法，提高不同数据库不同版本的兼容性。

#### 1.2.2 魔法数字

- **禁止使用魔法数字与裸状态字面量**：必须使用枚举或常量类进行定义，增强代码可读性。

  ```java
  // ❌ 反面示例
  if (user.getStatus() == 1) { ... }
  Thread.sleep(3000);

  // ✅ 正面示例
  if (Objects.equals(user.getStatus(), UserStatusEnum.ACTIVE.getCode())) { ... }
  Thread.sleep(TimeUnit.SECONDS.toMillis(3));
  ```

### 1.3 接口规范

- **RESTful API 设计规范**：URL 使用名词复数，HTTP 方法表示操作类型（GET/POST/PUT/DELETE）。
- **请求参数规范**：查询参数使用 @RequestParam，请求体使用 @RequestBody，尽量减少路径参数使用。
- **响应体规范**：统一返回 `ResponseJson<T>` 包装类，包含 code、message、data 三个字段。
- **分页规范**：统一分页参数 pageNumber、pageSize，请求 bean 继承 BasePageModel 类，返回根据实际分页组件决定。

  ```java
  public class FacilityQueryRequest extends BasePageModel {}
  ```

- **Bean 使用规范**：除分页参数外，其他业务 bean 继承 BaseModel，要加上类说明和参数说明。

  ```java
  /**
   * 设施新增请求
   *
   * @author lwb
   * @date 2026年6月25日
   */
  @Data
  public class FacilityAddRequest extends BaseModel {
    /**
     * 所属项目ID
     */
    @NotBlank(message = "所属项目不能为空")
    private String proId;
    ...
  }
  ```

### 1.4 异常处理规范

- **全局异常处理**：使用 @RestControllerAdvice 全局捕获异常，禁止在 Controller 内 try-catch 拼凑错误响应。
- **自定义业务异常**：业务可预期的失败应抛出业务异常，禁止通过 if 返回错误码。

  ```java
  if (facilityVO == null) {
    throw new BusinessException("设施不存在");
  }
  ```

- **参数校验**：使用 JSR380 注解（如 @NotBlank）结合 @Valid 进行参数校验，常规验证尽量减少手动编写大量 if 判断。
- **日志规范**：所有接口入参/出参可根据需要打印日志（使用 SLF4J），严禁打印密码等敏感数据。

### 1.5 安全规范

- **SQL 注入防护**：所有 SQL 参数必须使用预编译方式（`#{}`），禁止字符串拼接。
- **XSS 防护**：前端展示用户输入内容时使用 HTML 转义，后端统一配置 XSS 过滤器。
- **敏感数据加密**：密码等敏感数据必须加密存储。
- **权限控制**：使用 RBAC 模型，接口级别进行权限校验，禁止在业务代码中硬编码权限判断。
- **防重放攻击**：对第三方提供的关键接口使用 sign + timestamp 签名机制。

## 2. 命名规范

### 2.1 数据库命名

- **大小写**：名称统一使用小写。
- **格式**：使用英文+下划线命名，并控制总长度（如 t_sys_user）。
- **前缀**：表名建议采用 `t_` 前缀，中间为功能或模块（如 t_sys_user）。
- **索引与约束命名**：普通索引 `idx_表名_字段名`，唯一索引 `uk_表名_字段名`，主键约束 `pk_表名`。
- **其他对象命名**：视图命名以 `v_` 开头，存储过程命名以 `sp_` 开头。

### 2.2 代码命名

#### 2.2.1 类命名

- **基础规则**：采用大驼峰命名法（如 UserService），禁止使用拼音与英文混合。
- **特殊类**：抽象类以 Abstract 或 Base 开头；异常类以 Exception 结尾；测试类以 Test 结尾。
- **工具/帮助类**：通用工具类以 Utils 结尾，业务辅助类以 Helper 结尾。
- **数据对象**：命令类以 Cmd 结尾，查询类以 Query 结尾，视图对象以 VO 结尾。
- **枚举类**：以 Enum 结尾，如 IsDeleteEnum，存放文件夹：enums。

#### 2.2.2 方法命名

- **基础规则**：采用小驼峰命名法，遵循"动作+属性"模式（如 getName）。
- **CRUD 规范**：获取单个对象用 get，获取列表用 list，统计数量用 count；新增用 save/create，修改用 update，删除用 delete/remove。
- **判断类方法**：以 is/has/can 开头（如 isValid、hasPermission）。
- **线程相关方法**：以 start/stop/run 开头。

#### 2.2.3 工具命名

- **常量类**：以 Constants 结尾，按层次（跨应用、应用内、模块内）分类放置。
- **枚举类**：以 Enum 结尾。
- **配置类**：以 Config 结尾，如 RedisConfig、SecurityConfig。
- **设计模式类**：工厂类以 Factory 结尾，策略类以 Strategy 结尾，适配器类以 Adapter 结尾。

## 3. 其他规范

### 3.1 标识

- **覆写标识**：所有覆写的方法必须加上 @Override 注解。
- **依赖注入**：推荐使用构造器注入（而非字段注入），优先注入接口而非实现类。
- **final 关键字**：不可变字段使用 final，方法参数不可变使用 final。
- **@Deprecated 注解**：废弃方法必须标注 @Deprecated 并在 Javadoc 中说明替代方案。

### 3.2 注释规范

- **Javadoc 规范**：使用 Javadoc 格式对类、方法和字段进行注释，说明功能、参数和返回值。
- **简洁中文**：注释要求简洁明了，使用中文，不使用 Emoji 与装饰符号。
- **方法注释模板**：

  ```java
  /**
   * 根据用户ID获取用户信息
   *
   * @param userId 用户唯一标识
   * @return 用户视图对象
   * @throws BusinessException 当用户不存在时抛出
   */
  public UserVO getUserById(String userId) { ... }
  ```

- **TODO/FIXME 规范**：临时标记必须包含作者姓名和日期，如 `// TODO(zhangsan, 2026-08-12)`。

### 3.3 版本标识

- **技术栈版本**：Spring Boot 3.2.5+，前端 Vue 3 + Element UI。
- **pom.xml 版本管理**：使用版本号属性统一管理依赖版本，避免硬编码。

### 3.4 日志规范

- **日志级别**：ERROR（系统错误）、WARN（警告但不影响流程）、INFO（关键流程）、DEBUG（调试信息）。
- **日志格式**：统一包含时间戳、线程名、日志级别、类名、消息内容。
- **统一模板**：目前有统一 logback 模板。
- **敏感信息脱敏**：日志中禁止出现密码、身份证号、银行卡号等敏感信息。

  ```java
  public static String maskIdCard(String idCard) {
    if (StringUtils.isBlank(idCard) || idCard.length() < 15) return "***";
    return idCard.substring(0, 4) + "***********" + idCard.substring(idCard.length() - 3);
  }
  ```

### 3.5 前后端交互规范

- **统一响应体**：所有接口统一返回 ResponseJson 等标准包装类，禁止直接返回业务对象或自定义 Map 拼 JSON。
- **参数校验**：使用 JSR380 注解（如 @NotBlank）结合 @Valid 进行参数校验，减少手动编写大量 if 判断。
- **HTTP 方法**：GET 请求使用 @PathVariable 或 @RequestParam，POST 请求使用 @RequestBody 接收 JSON。
- **文件上传**：统一使用 MultipartFile 接收文件，限制文件大小和类型，返回文件访问 URL 或文件 id，而非文件本身。

### 3.6 缓存规范

- **缓存穿透**：使用布隆过滤器或缓存空值策略。
- **缓存雪崩**：设置随机过期时间，使用互斥锁或逻辑过期。
- **缓存一致性**：采用 Cache-Aside 模式，先更新数据库再删除缓存。
- **Redis Key 命名**：使用冒号分隔层级，如 `user:info:{userId}`。

### 3.7 消息队列规范

- **消息格式**：统一消息体结构，包含 messageId、timestamp、eventType、payload 等字段。
- **消息可靠性**：确保消息不丢失，设置重试机制和死信队列。
- **消息幂等性**：消费者必须实现幂等处理，防止消息重复消费。

### 3.8 定时任务规范

- **Cron 表达式**：使用标准 Cron 表达式，避免过于频繁的定时任务。
- **任务幂等性**：定时任务必须实现幂等性，支持重复执行不产生副作用。
- **任务监控**：定时任务执行结果必须记录日志，失败时发送告警通知。

### 3.9 单元测试规范

- **测试覆盖率**：核心业务逻辑单元测试覆盖率不低于 70%。
- **测试命名**：测试方法命名遵循 `test_方法名_场景_预期结果` 格式。
- **测试数据**：使用 @Mock 和 @Spy 模拟外部依赖，测试数据使用 Builder 模式构造。
- **单元测试示例**：

  ```java
  @ExtendWith(MockitoExtension.class)
  class UserServiceTest {

    @Mock
    private UserRepository userRepository;

    @InjectMocks
    private UserService userService;

    @BeforeEach
    void setUp() {
      // 初始化测试数据
    }

    @Test
    void test_getUserById_userExists_returnsUserVO() {
      // Given
      String userId = "123";
      UserPO userPO = new UserPO();
      userPO.setId(userId);
      when(userRepository.findById(userId)).thenReturn(Optional.of(userPO));

      // When
      UserVO result = userService.getUserById(userId);

      // Then
      assertNotNull(result);
      assertEquals(userId, result.getId());
      verify(userRepository, times(1)).findById(userId);
    }
  }
  ```

### 3.10 代码审查规范

- **代码提交规范**：使用 Conventional Commits 规范，如 add/feat/fix/docs/style/refactor/test/chore 前缀。
- **代码审查要点**：命名规范、逻辑正确性、性能隐患、安全风险、注释完整性。
- **Git Commit Message 示例**：

  ```
  feat(user): 新增根据手机号查询用户接口

  - 增加 getUserByPhone 方法
  - 添加手机号唯一性校验
  - 补充单元测试
  ```

### 3.11 依赖与构建规范

- **依赖管理**：使用 BOM 统一管理 Spring 生态依赖版本，避免版本冲突。
- **禁止传递依赖**：非必要不引入传递依赖，明确指定依赖版本。
- **构建优化**：使用多模块项目结构，合理拆分模块边界。

## 4. 框架流程说明

- **basecore**：基础工具模块，存放项目公用基础配置、bean 和工具。
- **file_server**：文件模块，进行实际文件的存储和读取。
- **_hub**：总线模块，操作统一入口，输出统一出口，规范操作规则。
- **_adapt**：适配模块，总线统一输出后适配不同端规则的实现。
- **_auth**：权限管理模块，用作整个项目的权限管理。
- **_gateway**：网关模块，项目的统一入口，做统一拦截和权限控制，特别需要做好安全防护。

## 5. 技术栈版本说明

- **后端**：Spring Boot 3.2.5+，JDK 17+
- **前端**：Vue 3 + Element Plus
- **数据库**：PostgreSQL 8.0+（规范原文为 PostSql）
- **缓存**：Redis
- **消息队列**：MQTT / Kafka（根据项目选型）
- **构建工具**：Maven 3.8+

## 6. 开发小技巧

1. 数组判空：

   ```java
   if (CollectionUtils.isEmpty(list)) {
     // 判断是否为空或者 null
   }
   ```

2. 对象比较：

   ```java
   if (Objects.equals(param1, param2)) {
     // 判断值是否一样
   }
   ```

3. 字符串判空：

   ```java
   if (StringUtils.isBlank(param1)) {
     // 判断字符串为空
   }
   if (StringUtils.isNoneBlank(param1)) {
     // 判断字符串不为空
   }
   ```
