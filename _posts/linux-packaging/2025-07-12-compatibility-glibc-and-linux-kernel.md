---
title: GLIBC 与 Linux 内核的兼容性
date: 2025-07-12 10:19:00 +0800
categories: [Linux 打包]
tags: [glibc, kernel]
---

根据 glibc 的 [release history](https://sourceware.org/glibc/wiki/Glibc%20Timeline) 整理出自 `2.17` 以来的版本与 linux 内核版本的兼容性：

| glibc 版本 | 兼容的 linux 内核版本 |
| --------- | ------------------- |
| 2.17 ~ 2.19 | >= 2.6.16 |
| 2.20 ~ 2.23 | >= 2.6.32 |
| 2.24 ~ 2.25 | 运行时：x86 上要求 >= 2.6.32，其他架构要求 >= 3.2；编译时：所有架构都要求内核头文件版本 >= 3.2 |
| 2.26 ~ 2.41 | >= 3.2 |

对于已编译好的 glibc，可以直接运行 `libc.so.6` 查看兼容的最低内核版本：
```console
$ /lib/x86_64-linux-gnu/libc.so.6 
GNU C Library (Ubuntu GLIBC 2.40-1ubuntu3.1) stable release version 2.40.
Copyright (C) 2024 Free Software Foundation, Inc.
This is free software; see the source for copying conditions.
There is NO warranty; not even for MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.
Compiled by GNU CC version 14.2.0.
libc ABIs: UNIQUE IFUNC ABSOLUTE
Minimum supported kernel: 3.2.0
For bug reporting instructions, please see:
<https://bugs.launchpad.net/ubuntu/+source/glibc/+bugs>.
```