---
title: PostgreSQL 版本策略（versioning policy)
date: 2025-03-11 21:52:00 +0800
categories: [PostgreSQL]
tags: [postgresql, versioning]
---

## 版本号

| 时期 | 格式 | major | minor |
|------|------|-------|-------|
| V10 以前 | `X`.`Y`.`Z` | `X`.`Y` | `Z` |
| V10 及以后 | `X`.`Y` | `X` | `Y` |

## 周期

| 版本类型 | 发布周期 | 改动范围 | 生命周期 |
|------|------|-------|-------|
| major | 1 年 | 不向后兼容的重大改动和新特性等 | 5 年 |
| minor | 3 个月（除此外如有紧急修复，也以 minor 发布，如 17.2） | 向后兼容的 bug 修复、安全修复和小幅改进等 | - |

## 升级

| 升级路径 | 升级方式 |
|------|-------|
| 跨 major 版本 | 使用 `pg_dumpall`、`pg_upgrade`、`logical replication` 等工具或方式，详情见 [官方文档](https://www.postgresql.org/developer/roadmap/) |
| 跨 minor 版本 | 可以通过直接替换安装目录的方式实现 |

## 参考资料

- [Versioning Policy] : https://www.postgresql.org/support/versioning/
- [Roadmap] : https://www.postgresql.org/developer/roadmap/