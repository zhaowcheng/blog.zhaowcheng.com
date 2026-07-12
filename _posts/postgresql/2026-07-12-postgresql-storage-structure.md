---
title: PostgreSQL 存储结构
date: 2026-07-12 15:15:00 +0800
categories: [PostgreSQL]
tags: [postgresql, unfinished]
---

## 1 逻辑结构

PostgreSQL 中 `Cluster` 的概念指的不是多个 PostgreSQL 实例所组成的集群，而是单个 PostgreSQL 实例中的多个数据库（Databases），所以翻译为`集簇`。每个集簇下可以存在多个相互独立的`数据库（Database）`，一个数据库是多个`数据库对象（Database object）`的集合，这些对象包括`表（Table）`、`视图（View）`、`索引（Index）`、`序列（Sequence）`、`函数（function）`等，数据库本身也是对象。关系型数据库理论中，数据库对象指的是一种用于存储和引用数据的`数据结构（Data structure）`。

![Logical Structure of Cluster](/assets/img/postgresql/cluster_logical_structure.png)

所有数据库对象都有一个唯一的标识符 `object identifiers (OIDs)`，OID 是一个 4 字节无符号整数类型，根据对象类型的不同，可以从对应的系统表中查询对象的 OID，比如数据库的 OID 可以从 [pg_database](https://www.postgresql.org/docs/18/catalog-pg-database.html) 中查询，表的 OID 可以从 [pg_class](https://www.postgresql.org/docs/18/catalog-pg-class.html) 中查询。

```sql
sampledb=# SELECT datname, oid FROM pg_database WHERE datname = 'sampledb';
 datname  |  oid
----------+-------
 sampledb | 16384
(1 row)

sampledb=# SELECT relname, oid FROM pg_class WHERE relname = 'sampletbl';
  relname  |  oid
-----------+-------
 sampletbl | 18740
(1 row)
```

在版本 `12` 以前，表中每一行（row）数据都有一个 OID，查询表时该列默认是隐藏的，但是可以通过 `SELECT oid` 查询出来：

```sql
testdb=# SELECT version();
                                                   version
-------------------------------------------------------------------------------------------------------------
 PostgreSQL 8.0.26 on arm-apple-darwin24.5.0, compiled by GCC Apple clang version 17.0.0 (clang-1700.0.13.5)
(1 row)

testdb=# \d tbl
      Table "public.tbl"
 Column |  Type   | Modifiers
--------+---------+-----------
 id     | integer |
 data   | text    |

testdb=# SELECT * FROM tbl;
 id | data
----+------
  1 | a
  2 | b
  3 | c
(3 rows)

testdb=# SELECT oid, * FROM tbl;
  oid  | id | data
-------+----+------
 17236 |  1 | a
 17237 |  2 | b
 17238 |  3 | c
(3 rows)
```

数据行的 OID 设计来自 PostgreSQL 的前身 POSTGRES，由于受到当时流行的面向对象思想的影响，所以 POSTGRES 想要被设计成一个 `对象关系型数据库（Object-Relational Database）`，即把一切都当作对象。但是由于通过 OID 访问行数据的方式与关系型数据库通过实际值管理数据的核心理念冲突，再加上 OID 是 4 字节无符号整型表示，只有 32 位，如果每一行数据都分配一个 OID 的话，很快就会达到上限，所以从 8.1 开始默认禁用该特性，最终从 12 开始完全移除了该特性。

## 2 物理结构

使用 initdb 程序初始化出数据库集簇目录，通常把该目录的路径定义为 `PGDATA` 环境变量，集簇目录下的 `base` 子目录下则是以各个数据库 OID 命名的目录，再往下则是该数据库中的表和索引相关文件，也是以 OID 开头来命名。除了 base 外还有其他的一些存放特定类型数据的子目录和文件，另外还有一个表空间相关的 `pg_tblspc` 子目录。

![Physical Structure of Cluster](/assets/img/postgresql/cluster_physical_structure.png)

## 3 文件布局

### 3.1 集簇布局

集簇目录下的文件和子目录及其用途说明如下：

| 文件/子目录 | 用途 |
| --------- | ---- |
| PG_VERSION | 主版本号（major）文件 |
| current_logfiles | 记录当前日志文件（们）|
| pg_hba.conf | 客户端鉴权配置 |
| pg_ident.conf | 用户名映射配置 |
| postgresql.conf | 数据库系统参数配置 |
| postgresql.auto.conf | 用于保存 `ALTER SYSTEM` 命令设置的数据库系统参数 |
| postmaster.opts | 记录最近一次数据库启动的命令行参数 |
| base/ | 数据库数据目录，每个数据库一个子目录 |
| global/ | 系统级的表和文件，比如 pg_database, pg_control |
| pg_commit_ts/ | 事务提交时间戳数据 |
| pg_dynshmem/ | 动态共享内存文件 |
| pg_logical/ | 逻辑复制解码（decoding）数据 |
| pg_multixact/ | 多事务状态数据（用于共享行锁 shared row lock）|
| pg_notify/ | `LISTEN/NOTIFY` 状态数据 |
| pg_repslot/ | 流复制槽数据 |
| pg_serial/ | 已提交的可串行化事务数据 |
| pg_snapshots/ | `pg_export` 函数导出的快照 |
| pg_stat/ | 统计子系统存放的永久文件 |
| pg_stat_tmp/ | 统计子系统存放的临时文件 |
| pg_subtrans/ | 子事务状态数据 |
| pg_tblspc/ | 表空间链接 |
| pg_twophase/ | 两阶段事务（prepared transactions）的状态文件 |
| pg_wal/ | WAL (Write Ahead Logging) 段文件 |
| pg_xact/ | 事务提交状态数据 |

### 3.2 数据库布局

每一个数据库都是 `$PGDATA/base/` 下的一个子目录，并且以 OID 命名：

```console
$ cd $PGDATA
$ ls -ld base/16384
drwx------  213 postgres postgres  7242  8 26 16:33 16384
```

### 3.3 表和索引布局

每一个表和索引的数据都是存储在 `$PGDATA/base/DBOID/` 下的一个文件（当不超过 1GB 时），并且以 `relfilenode` 命名：

```console
$ cd $PGDATA
$ ls -la base/16384/18740
-rw------- 1 postgres postgres 8192 Apr 21 10:21 base/16384/18740
```

表和索引的数据文件路径可以通过 [pg_relation_filepath()](https://www.postgresql.org/docs/18/functions-admin.html#FUNCTIONS-ADMIN-DBLOCATION) 函数查询：

```sql
sampledb=# SELECT pg_relation_filepath('sampletbl');
 pg_relation_filepath
----------------------
 base/16384/18740
(1 row)
```

表和索引的 relfilenode 可以通过 `pg_class` 系统表查询：

```sql
sampledb=# SELECT relname, oid, relfilenode FROM pg_class WHERE relname = 'sampletbl';
  relname  |  oid  | relfilenode
-----------+-------+-------------
 sampletbl | 18740 |       18740
(1 row)
```

表和索引在刚被创建时 relfilenode 和 OID 相同，但是 `TRUNCATE`, `REINDEX`, `CLUSTER` 等命令会改变其 relfilenode，比如当对表执行 TRUNCATE 命令后，旧的 relfilenode 命名的数据文件会被移除，然后以新的 relfilenode 创建一个新的文件：

```sql
sampledb=# TRUNCATE sampletbl;
TRUNCATE TABLE

sampledb=# SELECT relname, oid, relfilenode FROM pg_class WHERE relname = 'sampletbl';
  relname  |  oid  | relfilenode
-----------+-------+-------------
 sampletbl | 18740 |       18812
(1 row)
```

当表和索引的数据文件大小超过 1GB 以后，数据库系统会创建一个新的以 `relfilenode.1` 命名的文件，如果新文件满了再创建 `relfilenode.2`，依此类推，每一个数据文件称作一个`段（segment）`，段大小可以在数据库系统被编译时通过 `--with-segsize` 参数（默认 1GB）指定。

```console
$ cd $PGDATA
$ ls -la -h base/16384/19427*
-rw------- 1 postgres postgres 1.0G  Apr  21 11:16 data/base/16384/19427
-rw------- 1 postgres postgres  45M  Apr  21 11:20 data/base/16384/19427.1
```

表除了数据文件之外，还有另外两个文件： *relfilenode*_fsm 和 *relfilenode*_vm。fsm 文件是表的`空闲空间映射（Free Space Map）`，存储着表中每个页（page）的空闲空间信息。vm 文件是表的`可见性映射（Visibility Map）`，存储着表中每个页的可见性状态（并发控制所需）。`unlogged` 表还有第三个文件 *relfilenode*_init，这个比较特殊。

索引只有 fsm 文件，没有 vm 和 init 文件。

```console
$ cd $PGDATA
$ ls -la base/16384/18751*
-rw------- 1 postgres postgres  8192 Apr 21 10:21 base/16384/18751
-rw------- 1 postgres postgres 24576 Apr 21 10:18 base/16384/18751_fsm
-rw------- 1 postgres postgres  8192 Apr 21 10:18 base/16384/18751_vm
```

在数据系统内部，把数据文件、fsm 文件、vm 文件、init 文件称作对应关系（relation）的分支（fork），数据文件是 `fork 0`，fsm 文件是 `fork 1`，vm 文件是 `fork 2`，init 文件是 `fork 3`。和数据文件一样，其他分支文件大小超过编译时指定的段大小时，也会创建新段文件来继续写。

### 3.4 表空间布局

表空间是 PGDATA 以外的额外存储空间，通过 [CREATE TABLESPACE](https://www.postgresql.org/docs/18/sql-createtablespace.html) 命令创建。

![tblspc_files_layout](/assets/img/postgresql/tblspc_files_layout.png)

在 `$PGDATA/pg_tblspc/` 目录下是一个个链接到具体表空间路径的软链接，以表空间 OID 命名。假设有一个表空间的 OID 是 `16386`，存储路径是 `/home/postgres/tblspc`，那么软链接情况如下：

```console
$ ls -l $PGDATA/pg_tblspc/
total 0
lrwxrwxrwx 1 postgres postgres 21 Apr 21 10:08 16386 -> /home/postgres/tblspc
```

表空间被创建时会首先在存储路径下创建一个以 `PG_[Major version]_[Catalogue version number]` 格式命名的子目录（为了便于后续叙述，暂把此目录叫做版本子目录，关于 Catalogue version number 解释可以查看源码 [catversion.h](https://github.com/postgres/postgres/blob/REL_18_STABLE/src/include/catalog/catversion.h)）：

```console
$ ls -l /home/postgres/tblspc/
total 4
drwx------ 2 postgres postgres 4096 Apr 21 10:08 PG_14_202011044
```

表空间的版本子目录下则是各个以数据库 OID 命名的数据目录，再往下的结构则与 PGDATA 中的数据库数据目录一样。假设在表空间下创建了一个新的数据库 OID 为 16387，那么表空间下将创建这么个子目录：

```console
$ ls -l /home/postgres/tblspc/PG_14_202011044/
total 4
drwx------ 2 postgres postgres 4096 Apr 21 10:10 16387
```

如果一个 PGDATA 中已存在的数据库里创建了一个使用表空间的表，假设该数据库 OID 为 16384，那么也会在表空间版本目录下以数据库 OID 创建一个子目录，然后再该子目录下创建表的相关文件：

```console
sampledb=# CREATE TABLE newtbl (.....) TABLESPACE new_tblspc;

sampledb=# SELECT pg_relation_filepath('newtbl');
             pg_relation_filepath
---------------------------------------------
 pg_tblspc/16386/PG_14_202011044/16384/18894
```

### 3.5 表内部布局

#### 3.5.1 内部布局

表和索引的的数据文件、fsm 文件、vm 文件内部都是被分为 8KB 大小的`页（page）`，也叫做`块（block）`，每个页从 0 开始分配编号，叫做`块编号（block number）`，当文件填满的时候，PostgreSQL 会在文件末尾追加一个空页来增长文件。

页的内部布局根据文件的类型的不同而不同，我们这里以表文件内部的页为例进行说明：

![table_page_layout](/assets/img/postgresql/table_page_layout.png)

表文件页内包含 3 种类型的数据：

1. **元组（tuple）**: 一个元组对应表中的一行数据，在页内是从底部开始依次往上堆叠着存。正式因为这种存放方式，所以在 PostgreSQL 中元组又叫做`堆元组（heap tuple）`，表又叫做`堆表（heap table）`。

2. **行指针（line pointer）**: 行指针是一个 4 字节长的数据结构，保存着指向特定元组的指针，也被叫做`项目指针（item pointer）`。页内所有行指针是以数组的形式组织的，数组内的的行指针从 1 开始编号，这个编号也被叫做`偏移号（offset number）`。当向页内插入一个元组时，相应的也会追加一个行指针到行指针数组中。

3. **头部数据（header data）**: 页头部由 [bufpage.h](https://github.com/postgres/postgres/blob/REL_18_STABLE/src/include/storage/bufpage.h) 中的 `PageHeaderData` 数据结构所定义，长度为 24 字节，下面对其主要字段进行说明：
  - **pd_lsn**: 最近一次该页被修改时生成的 WAL 记录的日志序列号（LSN）。
  - **pd_checksum**: 该页的校验和。
  - **pd_lower, pd_upper**: 页内空闲空间的起始位置和结束位置。
  - **pd_special**: 该字段主要在索引页中起作用，指向索引页中特殊空间的起始位置，而在表页中则指向表页的末尾。

页中的空闲空间（free space）也叫做 `hole`。

表文件中使用 TID (tuple identifier) 来表示一个元组（tuple）的具体位置，TID 由两个字段组成：`block number` 表示页编号，`offset number` 表示元组对应行指针在行指针数组中的偏移号。TID 常用于索引。

在计算机科学中，使用这种存储方式的页叫做 `slotted page`，行指针数组叫做 `slotted array`。

#### 3.5.2 元组读写

##### 3.5.2.1 写

![writing_tuples](/assets/img/postgresql/writing_tuples.png)

如上图，假设一张表当前只有一个页，这个页内页只有一个元组 Tuple 1，这时 pd_lower 则指向行指针 1 的末尾，pd_upper 则指向元组 Tuple 1 的开头。当第二个元组 Tuple 2 插入时，则放到第一个元组 Tuple 1 的前面，同时在第一个行指针 1 后面追加一个行指针 2 指向元组 Tuple 2 的开头，pd_lower 改为指向行指针 2 的末尾，pd_upper 改为指向元组 Tuple 2 的开头，同时页头部相应字段（如 pd_lsn, pd_checksum, pd_flags 等）也进行更新。

##### 3.5.2.2 读

![reading_tuples](/assets/img/postgresql/reading_tuples.png)

上图中举了两个比较典型的读取元组的方式：

- **顺序扫描（Sequential scan）**：顺序扫描每页的行指针来顺序读取所有元组。

- **B 树索引扫描（B-tree index scan）**：从索引文件中拿到索引键对应元组的 TID，然后通过 TID 从表文件中直接读取对应元组。

#### 3.5.3 超大属性存储技术

TODO

## 4 参考资料

- [Database Cluster, Databases and Tables] : https://www.interdb.jp/pg/pgsql01/index.html

- [Database Physical Storage] : https://www.postgresql.org/docs/18/storage.html

- [数据库集簇，数据库，数据表] : https://pgint.vonng.com/ch1/
