---
title: PostgreSQL 编码支持（character set/encoding)
date: 2024-12-22 10:23:00 +0800
categories: [PostgreSQL]
tags: [postgresql, encoding, character-set, codeset]
---

## 编码支持

- PostgreSQL 支持的所有编码（包括服务端和客户端）: [PostgreSQL Character Sets](https://www.postgresql.org/docs/17/multibyte.html#CHARSET-TABLE)
  - 客户端支持表中所有编码；
  - 服务端支持表中大部分编码；

- 在服务端，编码设置必须与 locale 设置 `LC_CTYPE` 和 `LC_COLLATE` 兼容：
  - 当 locale 设置为 `C` 或 `POSIX` 时，兼容所有支持的编码；
  - 当 locale 设置为 `libc` 提供程序中的任一个时，只有一个对应的编码是兼容的（有一个例外情况是在 Windows 上，UTF-8 编码兼容所有 locale 设置）；
  - 当 locale 设置为 `icu` 提供程序中的任一个时，可以与服务端支持的大部分编码兼容，详情见 [PostgreSQL Character Sets](https://www.postgresql.org/docs/17/multibyte.html#CHARSET-TABLE)；

- 当编码设置为 `SQL_ASCII` 时，相当于无编码设置，且仅支持 `0-127` 这部分字符；

## 编码设置

- 服务端：
  - `initdb` 时设置整个数据库集簇的默认编码：
    - 可通过 `-E/--encoding` 选项指定编码（优先级高于 `locale` 中的编码设置）：
      - 如果通过该选项指定的编码与 `locale` 设置不兼容时，会报错；
    - 如果未指定则自动从 `locale` 设置中获取：
      - 当 locale 设置为 `C` 或 `POSIX` 时，自动设置编码为 `SQL_ASCII`
      - 当 locale 设置为 `libc` 提供程序中的任一个时，自动设置为对应的兼容编码（有的较老的系统可能不支持）；
      - 当 locale 设置为 `icu` 提供程序中的任一个时，自动设置编码为 `SQL_ASCII`；
  - `CREATE DATABASE` 时可以指定被创建数据库的编码（覆盖 initdb 默认设置）：
    - 只有使用 `template0` 作为模板时才可以，详情见 [Template Databases](https://www.postgresql.org/docs/17/manage-ag-templatedbs.html)；

- 客户端（以下优先级依次递增）：
  - 读取服务端的 `client_encoding` 配置，该配置默认为 `SQL_ASCII`，即无编码，最终效果则是与服务端编码相同；
  - 读取客户端的环境变量 `PGCLIENTENCODING`；
  - 通过 SQL 或 psql 命令修改编码设置：
    - SQL: `ALTER SYSTEM SET client_encoding TO 'VALUE';`
    - SQL: `SET client_encoding TO 'VALUE';`
    - SQL: `SET NAMES TO 'VALUE';`
    - psql: `\encoding VALUE`

## 编码查询

- 服务端：
  - SQL: `SELECT * FROM pg_database;`
  - psql: `psql -l` 或 `\l`；

- 客户端：
  - SQL: `SHOW client_encoding;`
  - psql: `\encoding`

## 编码转换

PostgreSQL 内置支持很多不同编码之间的转换，具体哪些可以查看文档 [All Built-in Character Set Conversions](https://www.postgresql.org/docs/17/multibyte.html#BUILTIN-CONVERSIONS-TABLE)，或者通过 SQL 命令 `SELECT * FROM pg_conversion` 查看。

如果内置的不能满足需求，还可以使用 SQL 命令 [CREATE CONVERSION](https://www.postgresql.org/docs/17/sql-createconversion.html) 命令创建新的转换。

PostgreSQL 支持服务端和客户端之间编码的自动转换，内置支持的所有自动转换可以查看文档 [Built-in Client/Server Character Set Conversions](https://www.postgresql.org/docs/17/multibyte.html#MULTIBYTE-TRANSLATION-TABLE)，如果一个转换被标记为默认时（`CREATE DEFAULT CONVERSION`），就会被用于服务端和客户端之间的编码自动化转换，当服务端和客户端之间的编码不支持转换时，则会报错。

## 参考资料

- [Character Set Support] : https://www.postgresql.org/docs/17/multibyte.html
