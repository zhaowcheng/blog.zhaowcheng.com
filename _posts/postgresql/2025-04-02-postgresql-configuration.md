---
title: PostgreSQL 配置说明
date: 2025-04-02 12:58:00 +0800
categories: [PostgreSQL]
tags: [postgresql, unfinished]
---

## 1 Preface

### 1.1 参数值类型

参数名都是`大小写不敏感的（case-insensitive）`，参数值类型分为 `boolean`、`string`、`integer`、`floating point`、`enumerated (enum)` 这几种，下面分别对几种参数值类型的写法进行说明（注：参数值需要引号包裹的地方均指的单引号，不能使用双引号）：
- **Boolean**: 布尔类型，合法值包括 `on`、`off`、`true`、`false`、`yes`、`no`、`1`、`0`，以及这些值的没有歧义的前缀，比如 `of`、`t`、`f`、`y` 等。所有值都是`大小写不敏感的（case-insensitive）`。该类型的值`不需要引号包裹`。
- **String**: 字符串类型，该类型的值通常需要使用`单引号（Single quotes）`包裹，如果值中包含单引号，则需要`双写（Doubling any single quotes）`值中的单引号。如果是简单的标识符（没有特殊字符），也可以不用单引号包裹，但是如果是 `SQL 关键字`，则必须使用单引号包裹。
- **Numeric (integer and floating point):**: 数值类型，包括 `integer` 和 `floating point`。integer 类型参数还接受`小数（Fractional）`、`十六进制（以 0x 开头）`、`八进制（以 0 开头）`等形式的值，但是小数形式会被四舍五入为最近的整数，除十六进制外，其他形式都可以不加单引号包裹。不接受千分位（Thousands separators）形式。
- **Numeric with Unit**: 有的数值类型是有单位的，比如和存储和时间相关的参数，该类型的值如果是给的纯数字，那么会使用默认单位（可以从 `pg_settings.unit` 查看默认单位），关于单位的写法要求如下：
    - 存储相关的单位可以是 `B(bytes)`、`kB(kilobytes)`、`MB(megabytes)`、`GB(gigabytes)`、`TB(terabytes)`，不同级别单位之间的乘数是 `1024`。
    - 时间相关的单位可以是 `us(microseconds)`、`ms(milliseconds)`、`s(seconds)`、`min(minutes)`、`h(hours)`、`d(days)`。
    - 给的其他级别单位的值最终会被转换为默认级别单位的值。
    - 带单位的时候必须使用单引号包裹起来，单位和数字之间可以有空格。
    - 单位是`大小写敏感的（case-sensitive）`。
    - 如果一个带单位的值写成了小数，PostgreSQL 会先把它换算成“更小一级的单位”后再取整。比如 30.1 GB 会被换算成 30822 MB，而不是直接变成 32319628902 B。如果这个参数本身还是整数类型，那么在单位换算之后，还会再做一次整数取整。
- **Enumerated**: 枚举类型，本质上是字符串类型，只是限定了值的范围，所以规则与字符串相同，某个参数具体哪些值合法可以查看 `pg_settings.enumvals`，该类型的值是`大小写不敏感的（case-insensitive）`。

### 1.2 设置方式

#### 1.2.1 通过配置文件

data 目录下的 `postgresql.conf` 是提供给用户手动修改设置数据库`全局默认参数（global defaults）` 的。

文件格式要求如下：
- 一行一个参数；
- `=` 是可选的；
- `#` 后面的内容是注释；
- 参数值如果包含特殊字符，应该用 `单引号（'）` 括起来；
- 如果要在参数值中包含 `单引号（'）`，可以用 `双写单引号（''）` 或 `反斜杠单引号（\'）` 的方式，推荐使用前者；
- 同一个参数多次配置，则以最后一个的值为准；

在数据库运行期间修改了配置文件后可通过 `pg_ctl reload` 命令或 `pg_reload_conf()` SQL 函数来向主进程发送 `SIGHUP` 信号，当主进程收到该信号会重载配置文件，重载过程中如果发现值设置无效的参数会忽略（但是会输出日志），但是如果配置文件存在语法错误或不支持的参数名时，则不会重载。

可通过视图 [pg_file_settings](#125-pg_file_settings) 在重载前查看修改是否有效或者查看重载没有生效的原因。

当注释参数行（`#` 开头）时表示把参数恢复为编译时确定的内建默认值（built-in default）。

该方式支持设置的参数 context 类型为 postmaster、sighup、superuser-backend、backend、superuser、user，支持重载生效的参数 context 类型为 sighup、superuser-backend、backend、superuser、user（关于 context 类型请查看 [pg_settings](#127-pg_settings)）。

支持重载生效的参数 context 类型为 sighup、superuser-backend、backend、superuser、user，且前提是没有被后续所诉的方式覆盖设置。

配置文件中支持使用 `include 'filename'` 指令来导入其他配置文件。  
被 include 的配置文件路径如果是相对路径，则是相对于使用 include 指令的配置文件路径。  
被 include 的配置文件也可以使用 include 导入其他配置文件。  
被 include 的配置文件如果不存在，则会报错，可以使用 `include_if_exists` 指令来避免错误。

配置文件中支持使用 `include_dir 'directory'` 指令来导入指定目录中的配置文件。  
被 include 的目录路径如果是相对路径，则是相对于使用 include 指令的配置文件所在目录的路径。 
被 include 的目录中的文件以 `C locale` 的顺序被读取，即 `numbers before letters, and uppercase letters before lowercase ones`。  
被 include 的目录中的文件只有以 `.conf` 结尾的文件才会被读取，但是以 `.` 开头的文件会被忽略，因为这样的格式在 Linux 平台上表示隐藏文件。  

`include` 指令主要是为了管理多个数据库服务器的配置文件而设计的，比如：
```
include 'shared.conf'  # 每个服务器都相同的配置参数。
include 'memory.conf'  # 内存大小相同的服务器的配置参数。
include 'server.conf'  # 每个服务器自己独有的配置参数。
```

#### 1.2.2 通过启动命令

postgres 启动时可通过 `-c name=value` 或 `--name=value` 命令选项来设置`全局默认参数（global defaults）`，如果是通过 pg_ctl 启动的则可以使用 `-o '-c name=value'` 或 `-o '--name=value'` 选项来设置。

该方式设置的参数优先级高于[通过配置文件](#121-通过配置文件)方式，所以通过该方式设置的参数，是无法通过修改配置文件然后重载生效的（即使 context 类型支持），只能重启数据库并重新传入新的命令选项才能生效。

该方式支持设置的参数 context 类型同配置文件方式相同。

#### 1.2.3 通过 SQL 命令

##### 1.2.3.1 [ALTER SYSTEM](https://www.postgresql.org/docs/18/sql-altersystem.html)

`ALTER SYSTEM` 命令是 PostgreSQL 提供的一种通过 SQL 命令修改配置文件的方式，通过该命令设置的参数会写入到 `postgresql.auto.conf` 文件中，格式要求与 `postgresql.conf` 一样，所以本质上还是通过修改配置文件的方式来设置`全局默认参数（global defaults）`，所以其他方面都与[通过配置文件](#121-通过配置文件)方式相同。

可以通过设置 [allow_alter_system](#allow_alter_system-boolean) 参数为 `off` 来禁用 `ALTER SYSTEM` 命令。

`postgresql.auto.conf` 中设置的参数值会覆盖 `postgresql.conf` 中的同名参数，所以其优先级更高。

当执行 `ALTER SYSTEM SET configuration_parameter { TO | = } DEFAULT` 或 `ALTER SYSTEM RESET configuration_parameter` 时，表示把指定参数从 `postgresql.auto.conf` 中移除。  
当执行 `ALTER SYSTEM RESET ALL` 表示清空 `postgresql.auto.conf` 文件。

##### 1.2.3.2 [ALTER DATABASE](https://www.postgresql.org/docs/18/sql-alterdatabase.html)

`ALTER DATABASE` 命令可以设置`库级（per-database）默认参数`，设置后的值保存在 [pg_db_role_setting ](#126-pg_db_role_setting) 系统表中，设置的值对当前已连接的会话不影响，只影响后续连接的会话。

当执行 `ALTER DATABASE name SET configuration_parameter { TO | = } DEFAULT` 或 `ALTER DATABASE name RESET configuration_parameter` 时，表示把指定库的指定默认参数移除（即从系统表 `pg_db_role_setting` 中移除）。  
当执行 `ALTER DATABASE name RESET ALL` 时表示移除指定库的所有默认参数。  
当执行 `ALTER DATABASE name SET configuration_parameter FROM CURRENT` 表示把指定库的指定参数的默认值设置为当前会话中的值。

该方式设置的参数值优先级高于上述的几种方式。

该方式支持设置的参数 context 类型为 sighup、superuser-backend、backend、superuser、user。

##### 1.2.3.3 [ALTER ROLE](https://www.postgresql.org/docs/18/sql-alterrole.html)

`ALTER ROLE` 命令可以设置`角色级（per-role）默认参数`，设置后的值保存在 [pg_db_role_setting ](#126-pg_db_role_setting) 系统表中，设置的值对当前已连接的会话不影响，只影响后续连接的会话。

当执行 `ALTER ROLE name SET configuration_parameter { TO | = } DEFAULT` 或 `ALTER ROLE name RESET configuration_parameter` 时，表示把指定角色的指定默认参数移除（即从系统表 `pg_db_role_setting` 中移除）。  
当执行 `ALTER ROLE name RESET ALL` 时表示移除指定角色的所有默认参数。  
当执行 `ALTER ROLE name SET configuration_parameter FROM CURRENT` 表示把指定角色的指定参数的默认值设置为当前会话中的值。

该方式设置的参数值优先级高于上述的几种方式。

该方式支持设置的参数 context 类型为 sighup、superuser-backend、backend、superuser、user。

##### 1.2.3.4 [SET](https://www.postgresql.org/docs/18/sql-set.html)

`SET` 命令允许设置`会话/事务级（session-local）`参数，其设置的参数仅影响当前会话（SET 或 SET SESSION）或当前事务（SET LOCAL），其对应的 SQL 函数 [set_config(setting_name, new_value, is_local)](https://www.postgresql.org/docs/18/functions-admin.html#FUNCTIONS-ADMIN-SET) 具有相同功能。

`SET` 或 `SET SESSION` 仅影响当前会话。如果在一个事务中执行，但是最终这个事务回滚了，那么这个设置不会对当前会话产生影响。

[SHOW](https://www.postgresql.org/docs/18/sql-show.html) 命令可以查询当前会话的参数值，其对应的 SQL 函数 [current_setting(setting_name text)](https://www.postgresql.org/docs/18/functions-admin.html#FUNCTIONS-ADMIN-SET) 具有相同的功能。

也可以通过 [pg_settings](#127-pg_settings) 来查看和设置当前会话的参数。

当执行 `SET [ SESSION | LOCAL ] configuration_parameter { TO | = } DEFAULT` 或 `RESET configuration_parameter` 时表示恢复当前会话指定参数的值为默认值（即 pg_settings 中的 reset_val 列），即假设当前会话没有 `SET` 修改过该参数的情况下的值，该值有可能来自于任意其他参数设置方式，但是不能叫做`会话开始时的值`，因为假如这个值是来自于配置文件，那么在会话期间如果配置文件修改了该值，这个默认值也会跟着改变（即使修改后没有重载）。  
当执行 `RESET ALL` 时表示恢复所有当前会话的值为默认值，该默认值的含义与上述相同。

该方式设置的参数值优先级高于上述的几种方式。

该方式支持设置的参数 context 类型为 superuser、user。

#### 1.2.4 通过客户端连接请求

只要是按照 PostgreSQL 协议规定来实现的客户端，都支持在连接时设置`会话级（session-local）`参数，比如 psql 可以通过 `env PGOPTIONS="-c geqo=off --statement-timeout=5min" psql` 这样的方式来设置，`PGOPTIONS` 的格式与[通过启动命令](#122-通过启动命令)方式设置参数的格式一致。

该方式设置的参数优先级高于 [ALTER ROLE](#1233-alter-role) 但低于 [SET](#1234-set)。

该方式支持设置的参数 context 类型为 superuser-backend、backend、superuser、user。

#### 1.2.5 [pg_file_settings](https://www.postgresql.org/docs/18/view-pg-file-settings.html)

`pg_file_settings` 视图是表示当前的`配置文件（们）`的解析结果的，每当查询该视图时才会去读取配置文件并返回解析结果，它仅仅反映当前配置文件内容，不是表示当前数据库已应用的参数（[pg_settings](#127-pg_settings) 才是）。

配置文件中一行内容（如 `name = value`）会在该视图中产生一行数据（entry），同名参数多次出现也会产生多行数据。

默认情况下，该视图只有`超级用户（superuser）`才能读取。

该视图具体的列说明请查看[官方文档](https://www.postgresql.org/docs/18/view-pg-file-settings.html)，这里对几个重要的列进行说明：
- **applied bool**: 表示当前这行参数设置能否应用成功，以下这些情况下会是 false:
    - 配置文件有`语法错误`或`存在无效参数名`时，这种情况下所有的行的该列都会是 false，并且视图中可能会有额外的一到几行（根据错误数量）数据会对错误进行说明（error 列）。
    - 参数值错误时。
    - 被后面的同名参数覆盖时。
    - 当前参数必须重启才能生效时（即 context 类型为 postmaster）。
- **error text**: 如果当前这行参数不能应用成功，这里会有原因说明（被后面的同名参数覆盖导致不能应用成功的情况除外）。

#### 1.2.6 [pg_db_role_setting](https://www.postgresql.org/docs/18/catalog-pg-db-role-setting.html) 

`pg_db_role_setting` 系统表保存的是`库级（per-database）默认参数`或`角色级（per-role）默认参数`，该表包含如下几列：
- **setdatabase oid**: 被设置参数的库的 oid，如果不是库级的（即角色级），则为 0。
- **setrole oid**: 被设置参数的角色（role）的 oid，如果不是角色级的（即库级），则为 0。
- **setconfig text[]**: 被设置的参数列表。

该系统表是系统级的，整个数据库系统只有一张，不像别的系统表是每个库一张。

#### 1.2.7 [pg_settings](https://www.postgresql.org/docs/18/view-pg-settings.html)

`pg_settings` 视图展示的是数据库系统当前的各种配置参数的值，效果等同于 [SHOW](https://www.postgresql.org/docs/18/sql-show.html) 命令，但是比 SHOW 命令看到的方面更多，除了可以看到参数的`当前值（setting）`外，还可以看到参数的 `值类型（vartype）`、`值范围（min_val, max_val, enumvals）`、`单位（unit）`、`上下文类型（context）`、`初始值（boot_val）`、`默认值（reset_val）`等。

该视图不允许插入（INSERT）或删除（DELETE），但是允许更新（UPDATE），比如更新 `setting` 列就相当于 [SET](#1234-set) 命令修改参数。同 SET 命令一样，UPDATE 仅影响当前会话。如果 UPDATE 在一个事务中执行，但是最终这个事务取消回滚了，那么这个 UPDATE 不会对当前会话产生影响。

下面对该视图中的几个重要的列进行说明（完整列说明请参考[官方文档](https://www.postgresql.org/docs/18/view-pg-settings.html)）：
- **settings text**: 参数的当前值。
- **vartype text**: 参数的值类型。
- **unit text**: 参数值的默认单位。
- **min_val text**: 参数的最小值，仅对数值类型参数有效，非数值类型参数该列为空（null）。
- **max_val text**: 参数的最大值，仅对数值类型参数有效，非数值类型参数该列为空（null）。
- **enumvals text[]**: 参数的枚举值列表，仅对枚举类型参数有效，非枚举类型参数该列为空（null）。
- **boot_val text**: 参数的初始值，即编译时决定的值（built-in default）。
- **reset_val text**: 参数的默认值，即假设当前会话没有 `SET` 修改过该参数的情况下的值，该值有可能来自于任意其他参数设置方式，但是不能叫做`会话开始时的值`，因为假如这个值是来自于配置文件，那么在会话期间如果配置文件修改了该值，这个默认值也会跟着改变（即使修改后没有重载）。该值也就是 `SET [ SESSION | LOCAL ] configuration_parameter { TO | = } DEFAULT` 和 `RESET configuration_parameter` 命令设置的值。
- **context text**: 参数的上下文类型，分别有以下几种（按照修改难度从高到低）：
    - **internal**: 该类型的参数有的完全无法修改，有的需要重新编译才可修改，有的需要重新 initdb 才可修改。
    - **postmaster**: 该类型的参数修改后需要重启数据库才可生效。
    - **sighup**: 该类型的参数修改后可以重载生效。
    - **superuser-backend**: 该类型的参数可以在客户端连接时修改，但是仅限超级用户。
    - **backend**: 该类型的参数可以在客户端连接时修改。
    - **superuser**: 该类型的参数可以在会话中使用 `SET` 命令修改，但是仅限超级用户。
    - **user**: 该类型的参数可以在会话中使用 `SET` 命令修改。

## 2 File Locations

## 3 Connections and Authentication

## 4 Resource Consumption

## 5 Write Ahead Log

### [synchronous_commit](https://www.postgresql.org/docs/18/runtime-config-wal.html#GUC-SYNCHRONOUS-COMMIT) (enum)

设置事务提交时需要等到 WAL 被保存到何种程度才返回，下表描述了可设置的值及其说明（数据安全程度依次递减）：

| 值 | 说明 |
| -- | --- |
| remote_apply | 等到同步备节点回放了 WAL |
| on | 等到同步备节点把 WAL 写入了磁盘 |
| remote_write | 等到同步备节点把 WAL 写入了文件系统缓存 |
| local | 等到主节点把 WAL 写入了磁盘 |
| off | 不等待 |

主节点会在 WAL 写入自己的磁盘之后才发送给备节点。

操作系统上数据的写入是先写入文件系统缓存，再刷新到磁盘，如果操作系统故障，文件系统缓存的数据会丢失，所以已写入磁盘的数据安全程度高于文件系统缓存中的数据。

如果 [synchronous_standby_names](#synchronous_standby_names-string) 设置为空，那么 `remote_apply`、`on` 和 `remote_write` 这几个设置都等同于 `local`。

该参数可以随时修改，比如可以通过 `SET LOCAL synchronous_commit TO OFF` 命令来临时为当前事务关闭同步等待。

## 6 Replication

### [synchronous_standby_names](https://www.postgresql.org/docs/18/runtime-config-replication.html#GUC-SYNCHRONOUS-STANDBY-NAMES) (string)

指定同步备节点的数量以及可以作为同步备节点的备节点列表，配置同步备节点后，主节点事务提交时需要等待所有同步备节点保存该事务的 WAL 记录，参数只在主节点上生效，语法如下：

```
[FIRST] num_sync ( standby_name [, ...] )
ANY num_sync ( standby_name [, ...] )
standby_name [, ...]
```

下面分别对这几种写法进行说明：

1. **[FIRST] num_sync ( standby_name [, ...] )** : 在给出的 `standby_name` 列表中，从前往后选择 `num_sync` 个 `正常（streaming）` 的备节点作为同步备节点，在事务提交时等待这些同步备节点保存该事务的 WAL 记录，剩余的则作为潜在（`potential`）备节点，当有同步备节点发送故障时，则选择优先级最高的潜在备节点来进行替换，`FIRST` 可以不写，默认即为 `FIRST` 规则，这种模式也叫做 `基于优先级的（priority-based）`。

2. **ANY num_sync ( standby_name [, ...] )** : 在给出的 `standby_name` 列表中，在事务提交时等待任意 `num_sync` 个备节点保存该事务的 WAL 记录，这种模式也叫做 `基于规定数量的（quorum-based）`。

3. **standby_name [, ...]** : 9.6 版本以前的写法，现在仍然有效，等同于 `FIRST 1 ( standby_name [, ...] )`。

4. **通配符** : 以上 3 种写法中的 `standby_name [, ...]` 部分可以写成 `*`，表示所有备节点。也可以只写 `*`，等同于 `FIRST 1 (*)`。

关于 `FIRST` 和 `ANY` 关键字，有如下注意事项：

- 大小写不敏感。

- 如果 `standby_name` 和这两个关键字重名，则需要把 `standby_name` 用双引号包裹。

关于 `num_sync`，有以下注意事项：

- 正常应该配置为小于等于后面给出的 `standby_name` 的数量，但是如果配置的超过了也没关系，数据库会自动调整为合适的值。

关于 `standby_name`，有以下注意事项：

- `standby_name` 默认匹配备节点连接信息中的 [application_name](https://www.postgresql.org/docs/18/libpq-connect.html#LIBPQ-CONNECT-APPLICATION-NAME) 字段，如果备节点连接时未设置该字段，则匹配规则如下：
    - **物理复制**：如果备节点配置了 [cluster_name](#cluster_name-string)，则匹配该字段，否则为固定值 `walreceiver`。
    - **逻辑复制**：订阅者名称（[subscription name](https://www.postgresql.org/docs/18/sql-createsubscription.html#SQL-CREATESUBSCRIPTION-PARAMS-NAME))

- `standby_name` 用来和备节点连接的 [application_name](https://www.postgresql.org/docs/18/libpq-connect.html#LIBPQ-CONNECT-APPLICATION-NAME) 进行比较时，是 `大小写不敏感` 的。

- `standby_name` 必须是直连到主节点的备节点，不能是级联复制备节点。

- 如果备节点重名，具体匹配上哪个节点作为同步备节点是不确定的。

如果该参数配置为空（默认值），则相当于禁用同步复制。但是在配置了的情况下，每个事务也可以通过配置 [synchronous_commit](#synchronous_commit-enum) 为 `off` 的方式来关闭当前事务的同步等待。

可以从视图 [pg_stat_replication](https://www.postgresql.org/docs/18/monitoring-stats.html#MONITORING-PG-STAT-REPLICATION-VIEW) 中查询到复制客户端的 `状态（sync_state）` 和 `优先级（sync_priority）`，关于这两个字段的说明如下：

- 在给定备节点列表中（`standby_name [, ...]`）：
    - `FIRST` 模式下：
        - `sync_priority` 根据给定顺序，从 `1` 开始递增，`数字越小，优先级越高`；
        - 被选定为同步的 `sync_state` 为 `sync`，其他的则为 `potential`；
    - `ANY` 模式下：
        - `sync_priority` 均为 `1`；
        - `sync_state` 均为 `quorum`；

- 而没在给定列表中的 `sync_priority` 和 `sync_state` 则为 `0` 和 `async`。

### [hot_standby_feedback](https://www.postgresql.org/docs/18/runtime-config-replication.html#GUC-HOT-STANDBY-FEEDBACK) (boolean)



### [recovery_min_apply_delay](https://www.postgresql.org/docs/18/runtime-config-replication.html#GUC-RECOVERY-MIN-APPLY-DELAY) (integer)

设置备节点回放 WAL 记录的延迟时间（默认值 `0`，即不延迟；默认单位 `ms(毫秒)`，也可以指定单位，如 `5min`），该设置可以保留一个时间窗口用于修复错误的 WAL 数据。

实际延迟的时间计算方式如下：
```
recovery_min_apply_delay - (当前备节点系统时间 - WAL记录中的时间戳(主节点上被创建时写入))
```
所以，如果主备节点系统时间不一致，可能会导致和预期的延迟不同；如果网络延迟大到超过了该值，备节点收到 WAL 记录后就会立即回放。

该设置只对 `事务提交` 类型的 WAL 记录有效，其他类型的 WAL 收到后立即回放，因为 MVCC 机制下，没提交的事务的 WAL 是不可见的，因此不会对其他事务产生影响。

该设置只有当备节点达到一致状态后才会生效。

在延迟等待期间，如果备节点收到 `升主（promote）` 信号，会立即结束等待。

如果设置时间太长，可能会导致备节点积压过多 WAL 文件从而占用磁盘空间。

当 [hot_standby_feedback](#hot_standby_feedback-boolean) 参数设置为 `on` 时，该设置会导致备节点发送 `feedback` 消息的延迟。

当 [synchronous_commit](#synchronous_commit-enum) 参数设置为 `remote_apply` 时，该设置会导致每次 `COMMIT` 都需等待该延迟结束。

## 7 Query Planning

## 8 Error Reporting and Logging

### [cluster_name](https://www.postgresql.org/docs/18/runtime-config-logging.html#GUC-CLUSTER-NAME) (string)

为当前数据库实例配置一个名称。

该名称会显示在进程标题（process title）中，比如 Linux 上用 `ps aux | grep postgres` 命令可以看到。

该名称还会作为物理复制备节点连接时 [application_name](https://www.postgresql.org/docs/18/libpq-connect.html#LIBPQ-CONNECT-APPLICATION-NAME) 参数的默认值（连接时也可以指定其他值）。

## 9 Run-time Statistics

## 10 Vacuuming

## 11 Client Connection Defaults

## 12 Lock Management

## 13 Version and Platform Compatibility

### [allow_alter_system](https://www.postgresql.org/docs/18/runtime-config-compatible.html#GUC-ALLOW-ALTER-SYSTEM) (boolean) 

当该参数设置为 `off` 时（默认值 `on`），通过 [ALTER SYSTEM](https://www.postgresql.org/docs/18/sql-altersystem.html) 命令去设置参数的方式会被禁用（执行时返回错误）。

这个主要是为了在数据库配置文件由第三方工具进行管理时，通过禁用 `ALTER SYSTEM` 命令来避免不知情的管理员通过该命令设置参数，从而导致和第三方工具冲突。

## 14 Error Handling

## 15 Preset Options

## 16 Customized Options

## 17 Developer Options

## 18 References

- [Server Configuration] : https://www.postgresql.org/docs/18/runtime-config.html
