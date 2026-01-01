---
title: PostgreSQL 流复制
date: 9999-01-01 00:00:00 +0800
categories: [PostgreSQL]
tags: [postgresql, replication]
---

## 1 简介

流复制是指通过 `主节点（Primary）` 持续发送 WAL 记录，`备节点（Standby）` 持续接收 WAL 记录并 `回放（replay）` 的方式来达到实时备份主节点的一种机制。

流复制中最主要的几个进程及其作用如下：
- **postgres**: 主节点上的后端进程，负责处理客户端连接，一个后端进程对应一个客户端。
- **walsender**: 主节点上负责发送 WAL 记录的进程。
- **walreceiver**: 备节点上负责接收 WAL 记录的进程，一个 walreceiver 对应主节点上一个 walsender。
- **startup**: 备节点上负责启动 walreceiver 和 `回放` WAL 记录的进程。

PostgreSQL 流复制支持 `一主多备`，但为了便于理解，后续的内容我们均以 `一主一备` 为例。

## 2 启动过程

下图展示了主备之间的启动过程，也就是从请求连接到进入稳定的流复制阶段：

![rep_startup_process](/assets/img/postgresql/rep_startup_process.png)

1. 主节点和备节点分别启动。

2. 备节点 `startup` 进程启动。

3. 备节点 `walreceiver` 进程启动。

4. 备节点 `walreceiver` 进程向主节点发送连接请求，如果主节点未运行，备节点会周期性的重试。

5. 主节点收到连接请求后启动一个 `walsender` 来处理连接。

6. 备节点发送自己数据库的 `最新 LSN（latest LSN）` 给主节点，该阶段在通信领域也叫做 `握手（handshaking）`。

7. 如果备节点的最新 LSN 小于主节点的最新 LSN，那么主节点会把备节点上没有的这些 WAL 记录发送给备节点，备节点接收 WAL 记录并回放，直到和主节点一致，该阶段也叫做 `追赶（catch-up）`。

8. 主备节点数据达到一致后则进入稳定的 `流复制（streaming）` 阶段。

## 3 复制过程

下图展示了在进入稳定流复制阶段之后，主备节点之间的通信过程：

![rep_streaming_process](/assets/img/postgresql/rep_streaming_process.png)

1. 主节点 `postgres` 进程提交事务并刷盘了一些 WAL 记录到段文件。

2. 主节点 `walsender` 进程马上把新写入的 WAL 记录发送给备节点 `walreceiver` 进程。

3. 主节点 `postgres` 进程锁定事务提交过程并等待备节点 `响应（ACK）`。

4. 备节点 `walreceiver` 把接收到的 WAL 记录通过系统调用 `write()` 函数进行写入，并返回一个 ACK 给主节点。

5. 备节点 `walreceiver` 通过系统调用 `fsync()` 把 WAL 记录刷盘，然后再返回一个 ACK 给主节点。

6. 备节点 `startup` 把新刷盘的 WAL 记录进行回放。

7. 主节点 `postgres` 进程结束等待并释放事务提交锁定，然后返回成功给客户端。这里的释放时机会根据数据库参数 [synchronous_commit](https://www.postgresql.org/docs/current/runtime-config-wal.html#GUC-SYNCHRONOUS-COMMIT) 的配置不同而不同，当配置为 `on` 时则在第 5 步时释放，当配置为 `remote_write` 时则在第 4 步就释放，当配置为 `remote_apply` 时则在 第 6 步完成后才释放。

没有 WAL 记录发送时备节点也会定期向主节点发送 ACK 报告自己的状态信息，这个称为 `心跳检测（heart-beats）`，每次发送 ACK 包括如下信息：
- 备节点最新刷盘（flushed）的 LSN。
- 备节点最新写入（written）的 LSN。
- 备节点最新回放（replayed）的 LSN。
- 本次 ACK 的时间戳。

## 4 参考资料

[Streaming Replication] : https://www.interdb.jp/pg/pgsql11/index.html
