---
title: Patroni 配置说明
date: 2025-03-18 21:58:00 +0800
categories: [Patroni]
tags: [patroni, postgresql]
---

## 1 配置类型

- **全局配置（Global Configuration）**

    - **作用范围**：所有节点。

    - **修改方式**：初始化（[bootstrap](https://patroni.readthedocs.io/en/latest/replica_bootstrap.html#bootstrap)）前，修改配置文件中的 `bootstrap.dcs` 部分；初始化后，通过 [patronictl edit-config](https://patroni.readthedocs.io/en/latest/patronictl.html#patronictl-edit-config) 命令或 REST 接口 [/config](https://patroni.readthedocs.io/en/latest/rest_api.html#config-endpoint) 修改。

    - **配置项**：https://patroni.readthedocs.io/en/latest/dynamic_configuration.html#dynamic-configuration

    - **其他说明**：Patroni 官方文档中通常叫做 `动态配置（dynamic configuration）`，初始化以后保存在 DCS 中，修改查询均是访问的 DCS，配置文件中的内容将不再有效。

- **本地配置（Local Configuration）**

    - **作用范围**：单个节点。

    - **修改方式**：启动前，修改配置文件或配置 [环境变量](https://patroni.readthedocs.io/en/latest/ENVIRONMENT.html#environment)（优先级更高）；启动后，修改配置文件，然后通过 [patronictl reload](https://patroni.readthedocs.io/en/latest/patronictl.html#patronictl-reload) 命令或 REST 接口 [/reload](https://patroni.readthedocs.io/en/latest/rest_api.html#reload-endpoint)，或者直接向 Patroni 进程发送 `SIGHUP` 信号使其生效。

    - **配置项**：https://patroni.readthedocs.io/en/latest/yaml_configuration.html#yaml-configuration

## 2 数据库相关配置

在 Patroni 的 `全局配置` 和 `本地配置` 的 `postgresql` 段落中，都可以配置数据库相关配置项，下面把这些配置项分为 `数据库参数配置` 和 `其他数据库配置` 两部分来进行说明。

### 2.1 数据库参数配置

#### 2.1.1 数据库参数分类

在 Patroni 的 `全局配置` 和 `本地配置` 的 `postgresql.parameters` 段落中都能配置数据库参数，但是并不是都能生效，根据其可配置范围，分类如下：

1. 只能全局配置，本地配置无效的数据库参数（由于集群高可用的需要，Patroni 限制这些参数只能全局配置以此保持主备一致），这些参数及其默认值如下：
    - max_connections: 100
    - max_locks_per_transaction: 64
    - max_worker_processes: 8
    - max_prepared_transactions: 0
    - wal_level: hot_standby
    - track_commit_timestamp: off
    - max_wal_senders: 10
    - max_replication_slots: 10
    - wal_log_hints: on（v3 强制为 on，v4 可修改）
    - wal_keep_segments: 8（PG13 以前）
    - wal_keep_size: 128MB（PG13 及以后）

2. 全局配置和本地配置中都不能配置（即使配置了也不生效）的数据库参数，这些参数由 Patroni 自动从一些本地配置项里解析出来或者是固定的值，这些参数及其获取方式如下：
    - listen_addresses: 从本地配置的 `postgresql.listen` 字段或环境变量 `PATRONI_POSTGRESQL_LISTEN` 中解析出来。
    - port: 从本地配置的 `postgresql.listen` 字段或环境变量 `PATRONI_POSTGRESQL_LISTEN` 中解析出来。
    - cluster_name: 从本地配置的 `scope` 字段或环境变量 `PATRONI_SCOPE` 中解析出来。
    - hot_standby: 固定值 `on`。

3. 全局配置和本地配置中都可配置的数据库参数，都配置的情况下本地配置优先级更高，这些参数就是除了以上 2 类之外的其他所有数据库参数。

上述分类中的第 1 类和第 2 类统称为 `Patroni 托管的数据库参数`（[PostgreSQL parameters controlled by Patroni](https://patroni.readthedocs.io/en/latest/patroni_configuration.html#postgresql-parameters-controlled-by-patroni)），Patroni 把除 `wal_keep_segments/wal_keep_size` 以外的其他参数在数据库启动时通过命令行选项 `--name=value` 方式传入，以此保证其最高优先级，而不会被其他配置方式（如 `ALTER SYSTEM`）所覆盖。

#### 2.1.2 数据库参数优先级

Patroni 会把数据库原有配置文件 `postgresql.conf` 改名为 `postgresql.base.conf`（不考虑配置由 `custom_conf` 情况，关于该配置请参考[官方文档]([PostgreSQL parameters controlled by Patroni](https://patroni.readthedocs.io/en/latest/patroni_configuration.html#postgresql-parameters-controlled-by-patroni))），然后创建一个新的 `postgresql.conf` 并在开头 `include 'postgresql.base.conf'`，然后写入通过 Patroni 配置的数据库参数（包括托管的），所以数据库参数的优先级如下（越靠后优先级越高）：

1. `postgresql.base.conf` 中的参数。
2. `postgresql.conf` 中的参数。
3. `postgresql.auto.conf` 中的参数（即通过 `ALTER SYSTEM` 命令设置的参数）。
4. 数据库启动时通过命令行选项 `--name=value` 方式传入的参数。

当数据库参数有变动时，Patroni 会重写 `postgresql.conf` 文件，所以建议不要直接修改该文件，而是通过 Patroni 来配置。

#### 2.1.3 修改后对重启顺序有要求的数据库参数

通过 Patroni 修改数据库参数后，Patroni 会自动 `reload` 数据库使其生效，而如果修改的参数需要重启数据库才能生效，Patroni 则只是把需要重启的节点标记为 `pending_restart`（可通过 [patronictl list](https://patroni.readthedocs.io/en/latest/patronictl.html#patronictl-list) 命令查看），直到用户通过 [patronictl restart](https://patroni.readthedocs.io/en/latest/patronictl.html#patronictl-restart) 命令或 REST 接口 [/restart](https://patroni.readthedocs.io/en/latest/rest_api.html#restart-endpoint) 来重启数据库后该标记才消除（**注意**: 如果直接通过 `pg_ctl` 重启数据库会导致 Patroni 托管的数据库参数没有在命令行传入而失去最高优先级。如果直接重启 Patroni，则可能发生故障转移）。

Patroni 托管的数据库参数中，有一些参数由于涉及到共享内存的使用，备节点在回放 WAL 的时候，可能会使用到和主节点生成这些 WAL 时一样大小的共享内存，所以需要始终保持备节点的配置值 `不小于` 主节点的，否则备节点可能发生共享内存耗尽的情况，这些参数如下：

- max_connections
- max_prepared_transactions
- max_locks_per_transaction
- max_wal_senders
- max_worker_processes

当修改这些涉及共享内存使用的数据库参数时，由于它们都是应用到所有节点的全局配置，所以需要重启所有节点数据库使其生效，但是为了保持备节点配置值不小于主节点，根据其修改后的值是增大还是减小，对于重启的顺序要求如下：

- 修改后的值 `增大`：
    1. 先重启所有备节点；
    2. 然后重启主节点；

- 修改后的值 `减小`：
    1. 先重启主节点；
    2. 然后重启所有备节点；

如果修改后的重启顺序与预期相反时，会发生如下情况：

- **修改后的值增大，但是却先重启主节点，后重启备节点**：如果主备重启间隔较短，则无影响，重启后集群正常如初。如果主备重启间隔较大，那么备节点在主节点重启完成后，自己还未重启前，接收到新的 WAL 时发现 WAL 里记录的参数值（WAL 中会记录这些参数当时的值）比自己的参数值大，则会暂定回放并打印 `WARNING` 日志（`hot_standby` 为 `on` 时会暂停，否则会直接退出，但是 Patroni 强制把所有备节点 `hot_standby` 都配置为 `on`），而 Patroni 发现数据库的回放暂停后会去恢复回放，这会导致数据库立即关闭，然后 Patroni 会去拉起关闭的数据库，如果拉起成功，则备节点恢复正常状态（如果 `PG < 14`，无论 `hot_standby` 什么配置，都不会暂停回放，而是出现进程 crash 导致数据库关闭）。

- **修改后的值减小，但是却先重启备节点，后重启主节点**：Patroni 在重启备节点时会对比这些参数当前全局配置中的值和数据库 `pg_controldata` 获取到的值（数据库 `control` 文件中会记录这些值），如果发现当前全局配置中的值比 `pg_controldata` 获取到的值小，则会以旧参数值（`pg_controldata` 获取到的值）重启备节点数据库，这样做是为了避免数据库陷入重启死循环，因为如果直接以新参数值重启数据库，数据库在启动时发现新参数值（全局配置中的值）比 `control` 文件中记录的小，则会打印 `FATAL` 日志并退出，而 Patroni 发现数据库停止了则会去拉起数据库，从而陷入重启死循环。待主节点重启完成后再次重启备节点才会以新的参数值进行重启。

下面对不同重启顺序进行验证，验证环境的信息如下：

```console
$ patronitl list
+ Cluster: batman (7469053056424145047) +-----------+----+-----------+
| Member | Host               | Role    | State     | TL | Lag in MB |
+--------+--------------------+---------+-----------+----+-----------+
| node1  | 192.168.1.101:5432 | Leader  | running   | 31 |           |
| node2  | 192.168.1.102:5432 | Replica | streaming | 31 |         0 |
| node3  | 192.168.1.103:5432 | Replica | streaming | 31 |         0 |
+--------+--------------------+---------+-----------+----+-----------+
$ patronitl show-config | grep max_connections
    max_connections: 100
```

(1) 验证增大配置后，先重启备节点，再重启主节点：

```console
$ patronitl edit-config -s "postgresql.parameters.max_connections=200"
...
$ patronitl restart batman node3
...
$ patronitl restart batman node2
...
$ patronitl restart batman node1
...
$ patronitl list
+ Cluster: batman (7469053056424145047) +---------+----+-----------+
| Member | Host               | Role    | State   | TL | Lag in MB |
+--------+--------------------+---------+---------+----+-----------+
| node1  | 192.168.1.101:5432 | Leader  | running | 31 |           |
| node2  | 192.168.1.102:5432 | Replica | running | 31 |         0 |
| node3  | 192.168.1.103:5432 | Replica | running | 31 |         0 |
+--------+--------------------+---------+---------+----+-----------+
```

(2) 验证减小配置后，先重启主节点，再重启备节点：

```console
$ patronitl edit-config -s "postgresql.parameters.max_connections=80"
...
$ patronitl restart batman node1
...
$ patronitl restart batman node2
...
$ patronitl restart batman node3
...
$ patronitl list
+ Cluster: batman (7469053056424145047) +---------+----+-----------+
| Member | Host               | Role    | State   | TL | Lag in MB |
+--------+--------------------+---------+---------+----+-----------+
| node1  | 192.168.1.101:5432 | Leader  | running | 31 |           |
| node2  | 192.168.1.102:5432 | Replica | running | 31 |         0 |
| node3  | 192.168.1.103:5432 | Replica | running | 31 |         0 |
+--------+--------------------+---------+---------+----+-----------+
```

(3) 验证增大配置后，先重启主节点，再重启备节点：

```console
$ patronitl edit-config -s "postgresql.parameters.max_connections=200"
...
$ patronitl restart batman node1
...
$ patronitl restart batman node2
...
Failed: restart for member node2, status code=503, (restarting after failure already in progress)
$ cat postgres.log  # on node2
...
CONTEXT:  WAL redo at 0/1701CFD0 for XLOG/PARAMETER_CHANGE: max_connections=200 max_worker_processes=8 max_wal_senders=10 max_prepared_xacts=0 max_prepared_foreign_transactions=0max_lockss_per_xact=64 wal_level=replica wal_log_hints=on track_commit_timestamp=off
LOG:  recovery has paused
DETAIL:  If recovery is unpaused, the server will shut down.
HINT:  You can then restart the server after making the necessary configuration changes.
CONTEXT:  WAL redo at 0/1701CFD0 for XLOG/PARAMETER_CHANGE: max_connections=200 max_worker_processes=8 max_wal_senders=10 max_prepared_xacts=0 max_prepared_foreign_transactions=0max_lockss_per_xact=64 wal_level=replica wal_log_hints=on track_commit_timestamp=off
FATAL:  recovery aborted because of insufficient parameter settings
DETAIL:  max_connections = 80 is a lower setting than on the primary server, where its value was 200.
HINT:  You can restart the server after making the necessary configuration changes.
CONTEXT:  WAL redo at 0/1701CFD0 for XLOG/PARAMETER_CHANGE: max_connections=200 max_worker_processes=8 max_wal_senders=10 max_prepared_xacts=0 max_prepared_foreign_transactions=0max_lockss_per_xact=64 wal_level=replica wal_log_hints=on track_commit_timestamp=off
LOG:  startup process (PID 2407) exited with exit code 1
LOG:  terminating any other active server processes
LOG:  shutting down due to startup process failure
LOG:  database system is shut down
...
$ cat patroni.log  # on node2
...
INFO: Resuming paused WAL replay for PostgreSQL 14+
INFO: no action. I am (node2), a secondary, and following a leader (node1)
WARNING: Postgresql is not running.
...
INFO: starting as a secondary
INFO: closed patroni connections to postgres
INFO: postmaster pid=2734
INFO: Lock owner: node1; I am node2
INFO: restarting after failure in progress
INFO: Lock owner: node1; I am node2
INFO: establishing a new patroni heartbeat connection to postgres
INFO: no action. I am (node2), a secondary, and following a leader (node1)
...
$ patronitl list
+ Cluster: batman (7469053056424145047) +---------+----+-----------+
| Member | Host               | Role    | State   | TL | Lag in MB |
+--------+--------------------+---------+---------+----+-----------+
| node1  | 192.168.1.101:5432 | Leader  | running | 31 |           |
| node2  | 192.168.1.102:5432 | Replica | running | 31 |         0 |
| node3  | 192.168.1.103:5432 | Replica | running | 31 |         0 |
+--------+--------------------+---------+---------+----+-----------+
```

(4) 验证减小配置后，先重启备节点，再重启主节点：

```console
$ patronitl edit-config -s "postgresql.parameters.max_connections=80"
...
$ patronitl restart batman node3
...
$ patronitl restart batman node2
...
$ patronitl restart batman node1
...
$ patronitl list
+ Cluster: batman (7469053056424145047) +-----------+----+-----------+-----------------+--------------------------+
| Member | Host               | Role    | State     | TL | Lag in MB | Pending restart | Pending restart reason   |
+--------+--------------------+---------+-----------+----+-----------+-----------------+--------------------------+
| node1  | 192.168.1.101:5432 | Leader  | running   | 31 |           |                 |                          |
| node2  | 192.168.1.102:5432 | Replica | streaming | 31 |         0 | *               | max_connections: 100->80 |
| node3  | 192.168.1.103:5432 | Replica | streaming | 31 |         0 | *               | max_connections: 100->80 |
+--------+--------------------+---------+-----------+----+-----------+-----------------+--------------------------+
$ cat patroni.log  # on node2
...
INFO: max_connections value in pg_controldata: 100, in the global configuration: 80. pg_controldata value will be used. Setting 'Pending restart' flag
...
$ patronitl restart batman node3
...
$ patronitl restart batman node2
...
$ patronitl list
+ Cluster: batman (7469053056424145047) +-----------+----+-----------+
| Member | Host               | Role    | State     | TL | Lag in MB |
+--------+--------------------+---------+-----------+----+-----------+
| node1  | 192.168.1.101:5432 | Leader  | running   | 31 |           |
| node2  | 192.168.1.102:5432 | Replica | streaming | 31 |         0 |
| node3  | 192.168.1.103:5432 | Replica | streaming | 31 |         0 |
+--------+--------------------+---------+-----------+----+-----------+
```

### 2.2 其他数据库配置

除数据库参数以外的其他数据库配置项，根据其可配置范围，分类如下：

1. 只能全局配置，本地配置无效的配置项：
    - use_slots

2. 只能本地配置，全局配置无效的配置项：
    - connect_address
    - proxy_address
    - listen
    - config_dir
    - data_dir
    - pgpass
    - authentication

3. 全局配置和本地配置中都能配置的配置项（本地配置优先级更高），这些是除了以上 2 类和数据库参数（`postgresql.parameters`）以外的其他数据库配置项。

## 3 全局配置备份文件

Patroni 在首次启动时会把 DCS 中的全局配置转储到数据库数据目录下的 `patroni.dynamic.json` 文件中，当全局配置有变化时也会更新该文件，如果 DCS 中的全局配置丢失，主节点会使用该文件来恢复全局配置。

## 4 配置文件生成与校验

使用 `patroni` 程序可以进行配置文件的生成和校验，以下是命令示例，具体说明请参考[官方文档](https://patroni.readthedocs.io/en/latest/patroni_configuration.html#configuration-generation-and-validation)。

(1) 生成示例文件（用户需要根据实际环境信息进行修改后才可使用）：

```console
$ patroni --generate-sample-config patroni.yml
```

(2) 生成指定环境的配置文件（可直接使用）：

```console
$ patroni --generate-config --dsn "host=192.168.1.101 port=5432 dbname=postgres user=postgres password=postgres" patroni.yml
```

(3) 校验配置文件：

```console
$ patroni --validate-config patroni.yml 
```

## 5 参考资料

- [Patroni configuration] : https://patroni.readthedocs.io/en/latest/patroni_configuration.html

- [Hot Standby Administrator's Overview] : https://www.postgresql.org/docs/current/hot-standby.html#HOT-STANDBY-ADMIN
