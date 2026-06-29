---
title: PostgreSQL 回归测试（regressio tests)
date: 9999-01-01 00:00:00 +0800
categories: [PostgreSQL]
tags: [postgresql, regression]
---

## 1 测试分类

### 1.1 按测试目录分类

- `src/test`: 回归测试主目录。
    - `authentication`: 认证相关测试（ssl 除外，其单独在 src/test/ssl 中）。
    - `examples`: libpq 示例程序，兼作回归测试。
    - `icu`: ICU(International Components for Unicode) 测试。
    - `isolation`: SQL 层面的并发行为（隔离级别）测试。
    - `kerberos`: Kerberos/GSSAPI 认证和加密测试。
    - `ldap`: 基于 LDAP 的认证测试。
    - `locale`: 区域设置数据、编码等的健全性检查。
    - `mb`: 多字节编码（UTF-8）支持测试。
    - `modules`: 主要用于测试目的的扩展。
    - `perl`: 基于 Perl 的 TAP 测试基础库。
    - `recovery`: 恢复和复制（replication）相关测试。
    - `regress`: 核心回归测试脚本和回归测试基础程序（pg_regress）。
    - `ssl`: SSL 证书处理的测试。
    - `subscription`: 逻辑复制测试。
- `contrib`: 扩展的测试。
- `src/bin`: 可执行程序的测试。
- `src/interfaces`: 接口测试（该目录下虽然存在 libpq/test 子目录，但是没有测试脚本，libpq 的测试主要是在 src/test/examples 中）。
- `src/pl`: 过程语言的测试。

### 1.2 按脚本类型分类

#### 1.2.1 `.sql` 脚本

`.sql` 测试脚本由 `pg_regress` (src/test/regress/pg_regress.c) 程序执行，该程序的参数如下：

```console
$ pg_regress --help
PostgreSQL regression test driver

Usage:
  pg_regress [OPTION]... [EXTRA-TEST]...

Options:
      --bindir=BINPATH          use BINPATH for programs that are run;
                                if empty, use PATH from the environment
      --config-auth=DATADIR     update authentication settings for DATADIR
      --create-role=ROLE        create the specified role before testing
      --dbname=DB               use database DB (default "regression")
      --debug                   turn on debug mode in programs that are run
      --dlpath=DIR              look for dynamic libraries in DIR
      --encoding=ENCODING       use ENCODING as the encoding
      --expecteddir=DIR         take expected files from DIR (default ".")
  -h, --help                    show this help, then exit
      --inputdir=DIR            take input files from DIR (default ".")
      --launcher=CMD            use CMD as launcher of psql
      --load-extension=EXT      load the named extension before running the
                                tests; can appear multiple times
      --max-connections=N       maximum number of concurrent connections
                                (default is 0, meaning unlimited)
      --max-concurrent-tests=N  maximum number of concurrent tests in schedule
                                (default is 0, meaning unlimited)
      --outputdir=DIR           place output files in DIR (default ".")
      --schedule=FILE           use test ordering schedule from FILE
                                (can be used multiple times to concatenate)
      --temp-instance=DIR       create a temporary instance in DIR
      --use-existing            use an existing installation
  -V, --version                 output version information, then exit

Options for "temp-instance" mode:
      --no-locale               use C locale
      --port=PORT               start postmaster on PORT
      --temp-config=FILE        append contents of FILE to temporary config

Options for using an existing installation:
      --host=HOST               use postmaster running on HOST
      --port=PORT               use postmaster running at PORT
      --user=USER               connect as USER

The exit status is 0 if all tests passed, 1 if some tests failed, and 2
if the tests could not be run for some reason.
```

#### 1.2.2 `.spec` 脚本

`.spec` 测试脚本由 `pg_isolation_regress` (src/test/isolation/isolation_main.c) 程序执行，该程序是专为测试 `隔离级别` 而设计的，是 `pg_regress` 的一个包装程序。

#### 1.2.3 `.pl` 脚本

#### 1.2.4 `.c` 脚本

## 2 测试执行

## 3 测试结果

## 4 测试覆盖率

## 5 参考资料

- [Regression Tests] : https://www.postgresql.org/docs/current/regress.html
- [src/test/README] : https://github.com/postgres/postgres/blob/REL_17_STABLE/src/test/README
