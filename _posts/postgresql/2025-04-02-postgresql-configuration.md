---
title: PostgreSQL 配置说明
date: 2025-04-02 12:58:00 +0800
categories: [PostgreSQL]
tags: [postgresql, unfinished]
---

## Preface

## Write Ahead Log

### [synchronous_commit](https://www.postgresql.org/docs/17/runtime-config-wal.html#GUC-SYNCHRONOUS-COMMIT) (enum)

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

## Replication

### [synchronous_standby_names](https://www.postgresql.org/docs/17/runtime-config-replication.html#GUC-SYNCHRONOUS-STANDBY-NAMES) (string)

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

- `standby_name` 默认匹配备节点连接信息中的 [application_name](https://www.postgresql.org/docs/17/libpq-connect.html#LIBPQ-CONNECT-APPLICATION-NAME) 字段，如果备节点连接时未设置该字段，则匹配规则如下：
    - **物理复制**：如果备节点配置了 [cluster_name](#cluster_name-string)，则匹配该字段，否则为固定值 `walreceiver`。
    - **逻辑复制**：订阅者名称（[subscription name](https://www.postgresql.org/docs/17/sql-createsubscription.html#SQL-CREATESUBSCRIPTION-PARAMS-NAME))

- `standby_name` 用来和备节点连接的 [application_name](https://www.postgresql.org/docs/17/libpq-connect.html#LIBPQ-CONNECT-APPLICATION-NAME) 进行比较时，是 `大小写不敏感` 的。

- `standby_name` 必须是直连到主节点的备节点，不能是级联复制备节点。

- 如果备节点重名，具体匹配上哪个节点作为同步备节点是不确定的。

如果该参数配置为空（默认值），则相当于禁用同步复制。但是在配置了的情况下，每个事务也可以通过配置 [synchronous_commit](#synchronous_commit-enum) 为 `off` 的方式来关闭当前事务的同步等待。

可以从视图 [pg_stat_replication](https://www.postgresql.org/docs/17/monitoring-stats.html#MONITORING-PG-STAT-REPLICATION-VIEW) 中查询到复制客户端的 `状态（sync_state）` 和 `优先级（sync_priority）`，关于这两个字段的说明如下：

- 在给定备节点列表中（`standby_name [, ...]`）：
    - `FIRST` 模式下：
        - `sync_priority` 根据给定顺序，从 `1` 开始递增，`数字越小，优先级越高`；
        - 被选定为同步的 `sync_state` 为 `sync`，其他的则为 `potential`；
    - `ANY` 模式下：
        - `sync_priority` 均为 `1`；
        - `sync_state` 均为 `quorum`；

- 而没在给定列表中的 `sync_priority` 和 `sync_state` 则为 `0` 和 `async`。

## Error Reporting and Logging

### [cluster_name](https://www.postgresql.org/docs/17/runtime-config-logging.html#GUC-CLUSTER-NAME) (string)

为当前数据库实例配置一个名称。

该名称会显示在进程标题（process title）中，比如 Linux 上用 `ps aux | grep postgres` 命令可以看到。

该名称还会作为物理复制备节点连接时 [application_name](https://www.postgresql.org/docs/17/libpq-connect.html#LIBPQ-CONNECT-APPLICATION-NAME) 参数的默认值（连接时也可以指定其他值）。

## References

- [Server Configuration] : https://www.postgresql.org/docs/17/runtime-config.html
