---
title: PostgreSQL 命令 - MERGE
date: 2026-11-03 23:26:00 +0800
categories: [PostgreSQL 命令]
tags: [postgresql, sql, merge]
---

## 1 语法概要

先说明记号：`[ ]` 表示可选，`{ }` 表示必须从中选一项，`|` 表示或者，`...` 表示可重复。

```
[ WITH with_query [, ...] ]
MERGE INTO [ ONLY ] target_table_name [ * ] [ [ AS ] target_alias ]
USING data_source ON join_condition
when_clause [...]
[ RETURNING [ WITH ( { OLD | NEW } AS output_alias [, ...] ) ]
{ * | output_expression [ [ AS ] output_name ] } [, ...] ]

其中 data_source 为：

{ [ ONLY ] source_table_name [ * ] | ( source_query ) } [ [ AS ] source_alias ]

而 when_clause 为：

{ WHEN MATCHED [ AND condition ] THEN { merge_update | merge_delete | DO NOTHING } |
WHEN NOT MATCHED BY SOURCE [ AND condition ] THEN { merge_update | merge_delete | DO NOTHING } |
WHEN NOT MATCHED [ BY TARGET ] [ AND condition ] THEN { merge_insert | DO NOTHING } }

而 merge_insert 为：

INSERT [( column_name [, ...] )]
[ OVERRIDING { SYSTEM | USER } VALUE ]
{ VALUES ( { expression | DEFAULT } [, ...] ) | DEFAULT VALUES }

而 merge_update 为：

UPDATE SET { column_name = { expression | DEFAULT } |
( column_name [, ...] ) = [ ROW ] ( { expression | DEFAULT } [, ...] ) |
( column_name [, ...] ) = ( sub-SELECT )
} [, ...]

而 merge_delete 为：

DELETE
```

## 2 语法概要逐字解释

### 2.1 顶层骨架

```sql
[ WITH with_query [, ...] ]                 -- 可选 CTE，给后面的查询起名字引用；不支持 WITH RECURSIVE
MERGE INTO [ ONLY ] target_table_name [ * ] [ [ AS ] target_alias ]
                                            -- INTO 只是固定写法；ONLY 表示只针对该表、不含继承/分区子表，
                                            -- 表名后的 * 显式表示连后代表一起处理（两者都不影响 INSERT，
                                            -- INSERT 永远只插进所命名的这张表）；AS 可省，给了别名就完全隐藏原名
USING data_source ON join_condition         -- 源数据 + 匹配条件，返回 boolean，语义同 WHERE
when_clause [...]                           -- 至少一个 WHEN 子句，可写多个，按书写顺序求值
[ RETURNING [ WITH ( { OLD | NEW } AS output_alias [, ...] ) ]
{ * | output_expression [ [ AS ] output_name ] } [, ...] ]
                                            -- 只返回本次 INSERT/UPDATE/DELETE 影响的行；
                                            -- WITH (...) 是 PG 18 新增，给 OLD/NEW 起别名，起了别名就只能用别名
```

### 2.2 data_source

```
{ [ ONLY ] source_table_name [ * ] | ( source_query ) } [ [ AS ] source_alias ]
```

源只能是「表/视图/过渡表」或「括号里的 SELECT/VALUES」二选一，`ONLY`、`*` 的作用与目标表侧一致，且可起别名。

### 2.3 when_clause

```
{ WHEN MATCHED [ AND condition ] THEN { merge_update | merge_delete | DO NOTHING } |
  WHEN NOT MATCHED BY SOURCE [ AND condition ] THEN { merge_update | merge_delete | DO NOTHING } |
  WHEN NOT MATCHED [ BY TARGET ] [ AND condition ] THEN { merge_insert | DO NOTHING } }
```

`MATCHED` 表示源行与目标行匹配上；`NOT MATCHED BY SOURCE` 表示目标表有某行在源里没有对应项（PG 扩展，语义是「目标多出来的行」）；`NOT MATCHED [BY TARGET]` 表示源行在目标表里没有匹配项（即标准里的 NOT MATCHED，`BY TARGET` 可省略）。

每个分支都能带 `AND condition`。一旦某个分支不带 condition，它就是该类型的最后一个可达分支，再写同类型的分支会报错。条件的可引用范围：`MATCHED` 可引用源和目标两侧，`NOT MATCHED BY SOURCE` 只能引用目标的列，`NOT MATCHED [BY TARGET]` 只能引用源的列。每行只执行第一个为真的分支，`DO NOTHING` 表示跳过该行。

### 2.4 merge_insert

```sql
INSERT [( column_name [, ...] )]            -- 列顺序随意；不写就是全部列按声明顺序；列不能重复、不能带子查询
[ OVERRIDING { SYSTEM | USER } VALUE ]      -- 针对 GENERATED ALWAYS(用 SYSTEM 才能写显式值) / BY DEFAULT(用 USER 忽略给的值)
{ VALUES ( { expression | DEFAULT } [, ...] ) | DEFAULT VALUES }
                                            -- VALUES 只能引用源列；DEFAULT VALUES 则全部取默认值，且此时不能写 OVERRIDING
```

### 2.5 merge_update

```
UPDATE SET { column_name = { expression | DEFAULT } |
             ( column_name [, ...] ) = [ ROW ] ( { expression | DEFAULT } [, ...] ) |
             ( column_name [, ...] ) = ( sub-SELECT ) } [, ...]
```

无表名、无 WHERE。三种写法：

- 单列赋值；
- 多列一起赋（`ROW` 可省）；
- 多列等于子查询（列数须对齐，最多返回一行，返回零行则赋 NULL）。

### 2.6 merge_delete

就是单个 `DELETE`，不带表名和其它子句。

一句话概括：先用 `USING` 的源和 `ON` 条件把数据连起来生成候选变更行，每行只判定一次自己是 `MATCHED`、`NOT MATCHED BY SOURCE` 还是 `NOT MATCHED BY TARGET`，然后按顺序检查各 `WHEN` 子句，执行第一个条件成立的。

## 3 MATCHED、NOT MATCHED BY SOURCE、NOT MATCHED BY TARGET

假设目标表 `wines` 与源表 `new_wine_list` 的数据如下：

| winename | wines.stock | new_wine_list.stock |
| -------- | ----------- | ------------------- |
| a        | 10          | 10                  |
| b        | 20          | 30                  |
| c        | 0           | —                   |
| d        | —           | 5                   |

以 `ON s.winename = w.winename` 连接后，这四行分别落在三种状态上：

- a、b：两侧都有，属于 **MATCHED**。注意「匹配上」只由 `ON` 决定，与后面 `AND condition` 是否成立无关；a 的库存没变，最终可能什么动作都不做。
- c：目标有、源里没有，属于 **NOT MATCHED BY SOURCE**，即「目标多出来的行」。
- d：源里有、目标没有，属于 **NOT MATCHED BY TARGET**，即「源多出来的行」（标准里的 NOT MATCHED）。

把三种情况都写进一条 MERGE：

```sql
MERGE INTO wines w
USING new_wine_list s
ON s.winename = w.winename
WHEN MATCHED AND w.stock <> s.stock THEN      -- a 不满足，b 满足
  UPDATE SET stock = s.stock
WHEN NOT MATCHED BY TARGET THEN               -- d
  INSERT VALUES (s.winename, s.stock)
WHEN NOT MATCHED BY SOURCE THEN               -- c
  DELETE;
```

结果：b 更新成 30，d 插入，c 删除，a 因为条件不成立、且没有其它兜底分支，什么都不做。

补充几点：

- `WHEN NOT MATCHED` 与 `WHEN NOT MATCHED BY TARGET` 同义，`BY TARGET` 只是为了和 `BY SOURCE` 对称、写清楚。
- 一行只判定一次归属，然后按书写顺序找第一个为真的 WHEN 执行，后面的分支不再看；某类型分支若写在无条件的同类分支之后，就是不可达的，直接报错。
- 若一行在源里对应多行（连接后产生多个候选行），只有其中一个会用来修改目标行，后续再次修改同一行会报错（`INSERT` 报唯一性违例，`UPDATE`/`DELETE` 报基数违规）。

## 4 参考资料

- [MERGE] : https://pgsql.cc/wiki/sql/merge/?v=18