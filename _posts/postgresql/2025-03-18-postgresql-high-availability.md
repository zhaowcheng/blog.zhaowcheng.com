---
title: PostgreSQL 高可用（high availability)
date: 2025-03-18 22:40:00 +0800
categories: [PostgreSQL]
tags: [postgresql, high-availability, unfinished]
---

## 1 简介

主节点持续归档/传送 WAL，备节点持续恢复/接收 WAL 并回放（replay），以此实现一个高可用集群，这种方式叫做 `log shipping`，这样的备节点也叫做 `warm standby`，如果备节点还可以接受 `只读查询`，则叫做 `hot standby`。

PostgreSQL 支持 2 种级别的 `log shipping`：

1. **文件级（file-based）**：主节点配置 `archive_command` 持续归档 WAL 文件，备节点配置 `restore_command` 持续恢复 WAL 文件并回放。

2. **记录级（record-based）**： 主节点持续传送 WAL 记录，备节点持续接收 WAL 记录并回放，即 `流复制（streaming replication）`。

## 2 环境要求

- **硬件**：主备节点之间的 CPU 架构必须相同（不同架构下的数据类型长度可能不同，从而导致存储结构的差异）。

- **版本**：主备节点之间的 major 版本必须相同（minor 版本可以不同，通常 minor 版本之间的存储结构不发生变化，但是官方不对此做正式保证，所以建议主备之间版本尽量一致；如果需要升级整个集群的 minor 版本，建议先升级备节点，再升级主节点）。

- **表空间（TABLESPACE）**：主备节点之间必须存在相同的表空间路径。

## 3 备节点基本原理

当一个数据库实例的数据目录（datadir）下存在 `standby.signal` 文件时，该实例启动时则进入 `备节点模式（standby mode）`。

备节点模式下启动，数据库按照如下顺序读取 WAL 并回放：

1. 如果配置了 `restore_command`，则调用 restore_command 从归档中恢复 WAL 并回放直到 restore_command 失败为止。

2. 然后读取 `pg_wal` 目录中的所有可用 WAL 并回放直到结束；

3. 然后，如果配置了流复制，则通过流复制从主节点持续接收 WAL 并回放；

4. 如果流复制断开，则重新从第 1 步开始，如此循环往复；

当备节点执行升主操作（`pg_ctl promote` 或调用 `pg_promote()` 函数）后，则退出备节点模式，但是在升主前，会把 `归档` 和 `pg_wal` 中的可用 WAL 都先回放了。

## 4 文件级（持续归档和恢复）

### 4.1 主节点配置

1. 配置 `archive_mode` 参数为 `on`。

2. 配置 `archive_command` 参数来持续归档 WAL 到一个即使主节点挂掉了，备节点也能访问的地方，可以是第三方节点或者就在备节点上。

### 4.2 备节点配置

1. 使用 `pg_basebackup` 命令从主节点拉取数据目录，如 `pg_basebackup -P -h <PRIMARY_NODE_IP> -U <REPLICATION_USER> -p <DBPORT> -D <DATADIR>`。

2. 配置 `restore_command` 参数来从归档持续恢复 WAL 文件并回放。

3. 配置 `archive_mode` 和 `archive_command` 参数和主节点一样，以备当前备节点提升为主节点后能继续归档（除非 `archive_mode` 为 `always`，否则备节点模式下不会执行归档命令）。

4. 配置 `recovery_target_timeline` 为 `latest`（默认值），以此保证当发生切主到其他备节点时，当前备节点能及时跟随新主。

5. 如果只有一主一备，则可以同时在 `archive_cleanup_command` 参数中调用 `pg_archivecleanup` 命令来自动清理当前备节点已不再需要的 WAL 文件。

6. 在数据目录下创建 `standby.signal` 文件并启动数据库。

### 4.3 备节点配置持续归档

当 `archive_mode` 参数配置为 `always` 时，备节点模式下仍然会执行 `archive_command` 来归档 WAL 文件。这通常用在级联复制的上游（upstream）备节点中，用于给下游（downstream）备节点提供归档。

## 5 记录级（流复制）

### 5.1 主节点配置

1. 配置 `listen_addresses` 参数为包括备节点 IP 的范围，如 `*`。

2. 创建一个带 `REPLICATION` 权限的用户，如 `CREATE USER <REPLICATION_USER> PASSWORD '<REPLICATION_PWD>' REPLICATION;`。

3. 在 `pg_hba.conf` 文件中增加允许备节点访问的配置，如 `host replication <REPLICATION_USER> <STANDBY_NODE_IP>/32 md5`（`database` 列配置为虚拟数据库名 `replication`）。

4. 配置 `max_wal_senders` 参数为足够所有备节点使用的值。

5. 为了防止 WAL 文件在备节点接收前被回收，可以配置 `wal_keep_size` 参数或 [复制槽](#53-复制槽) 来为备节点保留 WAL。

6. 在支持 `socket keepalive` 的系统上，可以配置 `tcp_keepalives_idle`、`tcp_keepalives_interval` 和 `tcp_keepalives_count` 这几个参数来帮助主节点及时发现流复制连接断开情况。

### 5.2 备节点配置

1. 使用 `pg_basebackup` 命令从主节点拉取数据目录，如 `pg_basebackup -P -h <PRIMARY_NODE_IP> -U <REPLICATION_USER> -p <DBPORT> -D <DATADIR>`。

2. 配置 `primary_conninfo` 参数连接到主节点，如 `primary_conninfo = 'host=<PRIMARY_NODE_IP> port=<DBPORT> user=<REPLICATION_USER> password=<REPLICATION_PWD>'`。

3. 在数据目录下创建 `standby.signal` 文件并启动数据库。

4. 启动并连接成功后，可以在备节点看到一个 `walreceiver` 进程，还可以在主节点看到一个 `walsender` 进程。

### 5.3 复制槽

如果流复制备节点连接断开后过了较长时间才恢复连接，那么有些还没有被备节点接收的 WAL 文件可能在主节点已经被回收，导致备节点无法追赶（catch-up）上主节点。我们可以通过配置 `wal_keep_size` 参数或 `复制槽` 来避免该问题。但是配置 `wal_keep_size` 的方式需要估计一个比实际需要保存更大的值，这样就会又些冗余文件的方式，而 `复制槽` 的方式则更精确，仅保留未被绑定到该复制槽上的备节点们接收的 WAL 文件。

需要注意的是配置复制槽后，如果备节点长期离线，可能会导致主节点积压过多的 WAL 文件而占用大量空间，为了避免该问题，可以配置 `max_slot_wal_keep_size` 参数来限制保留的最大值。

可以通过 [流复制协议](https://www.postgresql.org/docs/17/protocol-replication.html) 或 [相关 SQL 函数](https://www.postgresql.org/docs/17/functions-admin.html#FUNCTIONS-REPLICATION) 来创建管理复制槽，比如：

```console
postgres=# SELECT * FROM pg_create_physical_replication_slot('node_a_slot');
  slot_name  | lsn
-------------+-----
 node_a_slot |

postgres=# SELECT slot_name, slot_type, active FROM pg_replication_slots;
  slot_name  | slot_type | active
-------------+-----------+--------
 node_a_slot | physical  | f
(1 row)
```

备节点通过配置 `primary_slot_name` 参数来绑定复制槽，比如：

```
primary_slot_name = 'node_a_slot'
```

### 5.4 级联复制

备节点可以不连接主节点而连接其他备节点并接收 WAL，这样所组成的多级流复制拓扑就是 `级联复制（cascading replication）`，这样可以减少主节点的连接数量以此减少主节点的带宽占用。

级联复制的层级数量不受限制，更靠近主节点一端备节点被称为 `上游节点（upstream）`，离主节点更远一端的节点则被称为 `下游节点（downstream）`，一个备节点可以有多个下游，但是只能有一个上游（流复制本身也只能连接到一个发送方，即只能配置一个 primary_conninfo）。

级联复制中的上游节点不仅发送自己接收到的 WAL，如果配置了持续恢复（restore_command），还会发送恢复出来的 WAL（主节点不会，因为主节点不会执行 restore_command），所以即使上游节点与更上游节点的连接断开，只要有持续恢复出来的新的可用的 WAL，还是会继续向下游节点发送（也就是说上游节点可以是 `file-based` 方式的备节点）。

级联复制中只有 `直接备节点（直连到主节点）` 支持同步，其他 `间接备节点` 只能是异步的，就算是在主节点 `synchronous_standby_names` 参数中指定了级联复制中的间接备节点也不会产生作用。

如果级联复制备节点中开启了 `hot_standby_feedback` 参数，那么该备节点的 `feedback` 消息会逐级往上传播直到主节点。

如果上游节点提升为了主节点，下游节点在配置 `recovery_target_timeline` 参数为 `latest`（默认值）的情况下，会自动跟随新主。

要使用级联复制，上游节点除了需要像主节点一样的相关配置（`listen_addresses`、`pg_hba.conf`、`max_wal_senders`、`wal_keep_size` 或复制槽）之外，还需要配置 `hot_standby` 参数为 `on`（也就是设置为热备），因为备节点的流复制连接需要进行一些必要的只读查询。

### 5.5 同步复制（synchronous replication）

流复制默认是 `异步（asynchronous）` 的，即一个事物在主节点提交后如果马上去备节点查询，有可能还查询不到，因为 WAL 记录可能还没有传送到备节点或者备节点还没有回放该记录。

可以把一个或多个备节点指定为 `同步（synchronous）` 备节点，配置了同步备节点的流复制集群，在事务提交时需要 `一直等待` 直到收到同步备节点回复的 WAL 记录已保存的消息后，才给客户端返回成功。

以下情况不需要等待同步备节点回复：
- 只读事务（read-only transactions）
- 事务回滚（transaction rollbacks）
- 子事务（subtransaction）
- 数据载入（data loading）
- 索引构建（index building）

同步备节点可以是 `物理（流）复制备节点（physical/stream replication standby）`，也可以是 `逻辑复制订阅者（logical replication subscriber）`，也可以是其他一些第三方程序，比如 `pg_receivewal` 和 `pg_recvlogical` 等。

发生 `fast shutdown` 请求时，数据库会将正在等待的同步备节点的事务提交立即返回给客户端让其停止等待，但是仍然会等到 WAL 都已发送到所有备节点后才关闭（异步情况下也是如此）。

启用同步复制，需要在发送节点同时配置参数 [synchronous_commit](/posts/postgresql-configuration/#synchronous_commit-enum) 和 [synchronous_standby_names](/posts/postgresql-configuration/#synchronous_standby_names-string)，配置说明请点击对应参数链接查看。

如果因为同步备节点故障导致事务提交被阻塞，可以设置 `synchronous_standby_names` 参数为空并 `reload` 来立即关闭同步模式，从而解决阻塞的问题：

```SQL
ALTER SYSTEM SET synchronous_standby_names TO '';
SELECT pg_reload_conf();
```

### 5.6 状态查询

查询流复制状态主要通过以下函数和视图：

| 函数/视图 | 说明 | 使用范围/条件 |
| -------- | --- | ----------- |
| [pg_current_wal_flush_lsn()](https://www.postgresql.org/docs/17/functions-admin.html#FUNCTIONS-ADMIN-BACKUP) | 已刷盘的最新的 LSN | 恢复状态下不可用 |
| [pg_current_wal_lsn()](https://www.postgresql.org/docs/17/functions-admin.html#FUNCTIONS-ADMIN-BACKUP) | 已写入文件系统缓存的最新的 LSN | 恢复状态下不可用 |
| [pg_current_wal_insert_lsn()](https://www.postgresql.org/docs/17/functions-admin.html#FUNCTIONS-ADMIN-BACKUP) | 已插入 WAL 缓存的最新的 LSN | 恢复状态下不可用 |
| [pg_last_wal_receive_lsn()](https://www.postgresql.org/docs/17/functions-admin.html#FUNCTIONS-RECOVERY-CONTROL) | 已收到并且已刷盘的最新的 LSN | 没有 receiver 进程则返回 NULL |
| [pg_last_wal_replay_lsn()](https://www.postgresql.org/docs/17/functions-admin.html#FUNCTIONS-RECOVERY-CONTROL) | 恢复状态下已回放的最新的 LSN | 非恢复状态下则返回 NULL |
| [pg_stat_replication](https://www.postgresql.org/docs/17/monitoring-stats.html#MONITORING-PG-STAT-REPLICATION-VIEW) | 每个 sender 进程对应流复制的状态信息 | N/A |
| [pg_stat_wal_receiver](https://www.postgresql.org/docs/17/monitoring-stats.html#MONITORING-PG-STAT-WAL-RECEIVER-VIEW) | receiver 进程对应的流复制状态信息 | N/A |

> 注：一个数据库实例最多只能有一个 receiver。

## 6 文件级 + 记录级

同时配置文件级和记录级的 `log shipping` 可以达到更佳的效果，例如当备节点长时间离线后重新回归时，主节点上有些 WAL 可能已经被回收，但是备节点可以通过持续恢复从归档中获取 WAL，避免了 WAL 缺失导致的备节点回归失败。

## 7 热备（hot standby）

当数据库 `hot_standby` 参数配置为 `on` 时，则在恢复状态下仍然可以接受 `只读查询`，所以如果备节点开启了该参数，也就可以同时接受只读查询，也就是一个 `热备（hot standby）`。

## 8 故障转移（failover）

当主节点故障时，备节点可以通过执行 `pg_ctl promote` 命令或者 `pg_promote()` 函数来升级为主节点，以此实现故障转移。

故障切换后，原主节点故障修复后应该配置为备节点跟随新主节点，如果仍然以主节点启动，将会导致脑裂（即存在多个主节点）。

可以使用 [pg_rewind](https://www.postgresql.org/docs/17/app-pgrewind.html) 帮助原主节点作为备节点快速同步新主节点的数据。

## 9 参考资料

- [High Availability, Load Balancing, and Replication] : https://www.postgresql.org/docs/17/high-availability.html
