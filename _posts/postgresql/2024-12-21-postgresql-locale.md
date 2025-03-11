---
title: PostgreSQL 区域设置（locale）
date: 2024-12-21 17:44:00 +0800
categories: [PostgreSQL]
tags: [postgresql, locale]
---

## locale 分类

| 分类 | 作用 |
| --- | --- |
| LC_COLLATE | 字符顺序 |
| LC_CTYPE |	字符分类（什么是一个字符？它的大写形式是否等效？）|
| LC_MESSAGES |	消息语言 |
| LC_MONETARY |	货币符号 |
| LC_NUMERIC |	数字格式 |
| LC_TIME |	日期和时间格式 |

## locale 查询

可通过 SQL 命令 `SHOW LC_*` 查询对应分类的 locale 设置，如：

```SQL
SHOW LC_COLLATE;
```

## locale 设置

| 分类 | 设置方式 |
| --- | ------- |
| LC_COLLATE | initdb 时生成默认值；`CREATE DATABASE` 时也可以指定其他值（只有使用 `template0` 作为模板时才可以）；也可以使用 [collation](https://www.postgresql.org/docs/17/collation.html) 指定`某一列`或`某一次查询`使用其他值。 |
| LC_CTYPE | 同 `LC_COLLATE` |
| LC_MESSAGES |	initdb 时生成默认值并写入 `postgresql.conf` 中，后续可以随时通过修改配置来改变。 |
| LC_MONETARY |	同 `LC_MESSAGES` |
| LC_NUMERIC |	同 `LC_MESSAGES` |
| LC_TIME |	同 `LC_MESSAGES` |

## initdb 的 locale 选择策略

initdb 时默认从当前环境变量读取 locale 设置，以 `LC_COLLATE` 为例，其读取优先级如下：

```
LC_ALL > LC_COLLATE > LANG
```

如果以上环境变量都没有设置，则设置为 `C`。

也可以通过 initdb 命令的相关参数来指定（优先级大于环境变量），`--locale` 参数为所有 locale 分类设置值，也可以为具体的分类指定值，如 `--lc-collate`（优先级大于 `--locale`）。

通过 initdb 参数指定的 locale 必须是当前操作系统支持的设置，Linux 上可通过以下命令查看当前系统支持的所有 locale：

```sh
locale -a
```

## locale 提供程序（provider）

PostgreSQL 支持选择不同的 locale 提供程序为 `LC_COLLATE` 和 `LC_CTYPE` 分类提供支持，而其他的分类则仍然由操作系统提供支持。

PostgreSQL 提供程序在 `initdb`, `CREATE DATABASE` 和 `CREATE COLLATION` 时均可选择，也就是说可以在不同的维度上进行混用。

| 提供程序 | 说明 |
| ------ | ---- |
| builtin | PostgreSQL 内置，仅支持 `C` 和 `C.UTF-8`。 |
| libc | 操作系统自带 C 语言库，Linux 上即为 `libc` 或 `glibc`。 |
| icu | [ICU](https://unicode-org.github.io/icu/userguide/locale/)(International Components for Unicode)，需要在编译配置 PostgreSQL 时选择编译该库（默认编译，除非指定 `--without-icu` 选项）。 |

## locale 格式说明

| 提供程序 | 格式 |
| ------ | ---- |
| builtin | 仅支持 `C` 和 `C.UTF-8`。 |
| libc | *`language_territory.codeset`* (`codeset` 是可选项，如 `en_US.UTF-8`, `en_US`) |
| icu | *`language-region`* (如 `en-US`) |

## locale 对性能的影响

使用 locale 会对数据库的性能产生一定影响，所以建议在确实需要时才设置，不需要时可设置为 `C` 或 `POSIX`。

## 参考资料

- [Locale Support] : https://www.postgresql.org/docs/17/locale.html