---
title: PostgreSQL 流复制
date: 9999-01-01 00:00:00 +0800
categories: [PostgreSQL]
tags: [postgresql, replication]
---

## 1 简介

流复制是指通过 `主节点（Primary）` 持续发送 WAL 数据，`备节点（Standby）` 持续接收 WAL 数据并 `回放（replay）` 的方式来达到实时备份主节点的一种机制。

流复制中主要涉及的 3 个进程及其作用如下：
- **postgres**: 主节点上的后端进程，负责处理客户端连接，一个后端进程对应一个客户端。
- **walsender**: 主节点上负责发送 WAL 数据的进程。
- **walreceiver**: 备节点上负责接收 WAL 数据的进程，一个 walreceiver 对应主节点上一个 walsender。
- **startup**: 备节点上负责启动 walreceiver 和 `回放` WAL 数据的进程。

PostgreSQL 流复制支持 `一主多备`，但为了叙述方便，后续的内容我们均以 `一主一备` 为例。

## 2 启动过程

下图展示了主备之间的启动过程，也就是从请求连接到进入稳定的流复制阶段：

![rep_startup_process](/assets/img/postgresql/rep_startup_process.png)

1. 主节点和备节点分别启动。

2. 备节点 `startup` 进程启动。

3. 备节点 `walreceiver` 进程启动。

4. 备节点 `walreceiver` 进程向主节点发送连接请求，如果主节点未运行，备节点会周期性的重试。

5. 主节点收到连接请求后启动一个 `walsender` 来处理连接。

6. 备节点发送自己数据库的 `最新 LSN（latest LSN）` 给主节点，该阶段在通信领域也叫做 `握手（handshaking）`。

7. 如果备节点的最新 LSN 小于主节点的最新 LSN，那么主节点会把备节点上没有的这些 WAL 数据发送给备节点，备节点接收 WAL 数据并回放，直到和主节点一致，该阶段也叫做 `追赶（catch-up）`。

8. 主备节点数据达到一致后则进入稳定的 `流复制（streaming）` 阶段。

## 3 通信过程

下图展示了在进入稳定流复制过程之后，主备节点之间的通信过程：

![rep_streaming_process](/assets/img/postgresql/rep_streaming_process.png)

1. 主节点 `postgres` 进程提交事务并刷盘了一些 WAL 数据到段文件。

2. 主节点 `walsender` 进程马上把新写入的 WAL 数据发送给备节点 `walreceiver` 进程。

3. 主节点 `postgres` 进程锁定事务提交过程并等待备节点 `响应（ACK）`。

4. 备节点 `walreceiver` 把接收到的 WAL 数据通过系统调用 `write()` 函数进行写入，并返回一个 ACK 给主节点。

5. 备节点 `walreceiver` 通过系统调用 `fsync()` 把 WAL 数据刷盘，然后再返回一个 ACK 给主节点。

6. 备节点 `startup` 把新刷盘的 WAL 数据进行回放。

7. 主节点 `postgres` 进程结束等待并释放事务锁定，然后返回成功给客户端。这里的释放时机会根据数据库参数 [synchronous_commit](https://www.postgresql.org/docs/current/runtime-config-wal.html#GUC-SYNCHRONOUS-COMMIT) 的配置不同而不同，当配置为 `on` 时则在第 5 步时释放，当配置为 `remote_write` 时则在第 4 步就释放，当配置为 `remote_apply` 时则在 第 6 步完成后才释放。

没有 WAL 数据发送时备节点也会定期向主节点发送 ACK 报告自己的状态信息，这个称为 `心跳检测（heart-beats）`，每次发送 ACK 包括如下信息：
- 备节点最新刷盘（flushed）的 LSN。
- 备节点最新写入（written）的 LSN。
- 备节点最新回放（replayed）的 LSN。
- 本次 ACK 的时间戳。

## 4 配置步骤

### 4.1 主节点配置

1. 配置 `listen_addresses` 参数为包括备节点 IP 的范围，如 `*`。

2. 创建一个带 `REPLICATION` 权限的用户，如 `CREATE USER <REPLICATION_USER> PASSWORD '<REPLICATION_PWD>' REPLICATION;`。

3. 在 `pg_hba.conf` 文件中增加允许备节点访问的配置，如 `host replication <REPLICATION_USER> <STANDBY_NODE_IP>/32 md5`（`database` 列配置为虚拟数据库名 `replication`）。

4. 配置 `max_wal_senders` 参数为足够所有备节点使用的值。

5. 为了防止 WAL 文件在备节点接收前被回收，可以配置 `wal_keep_size` 参数或 `复制槽` 来为备节点保留 WAL。

6. 在支持 `socket keepalive` 的系统上，可以配置 `tcp_keepalives_idle`、`tcp_keepalives_interval` 和 `tcp_keepalives_count` 这几个参数来帮助主节点及时发现流复制连接断开情况。

### 4.2 备节点配置

1. 使用 `pg_basebackup` 命令从主节点拉取数据目录，如 `pg_basebackup -P -h <PRIMARY_NODE_IP> -U <REPLICATION_USER> -p <DBPORT> -D <DATADIR>`。

2. 配置 `primary_conninfo` 参数连接到主节点，如 `primary_conninfo = 'host=<PRIMARY_NODE_IP> port=<DBPORT> user=<REPLICATION_USER> password=<REPLICATION_PWD>'`。

3. 在数据目录下创建 `standby.signal` 文件并启动数据库。

4. 启动并连接成功后，可以在备节点看到一个 `walreceiver` 进程，还可以在主节点看到一个 `walsender` 进程。