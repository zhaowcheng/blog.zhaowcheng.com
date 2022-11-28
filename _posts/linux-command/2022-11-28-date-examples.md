---
title: date 命令使用示例
date: 2022-11-28 22:24:00 +0800
categories: [Linux 命令]
tags: [date]
---

## 显示

显示当前日期和时间

```console
$ date
Mon 28 Nov 2022 10:50:05 PM CST
```

显示指定格式的当前日期和时间

```console
$ date +"%Y-%m-%d %H:%M:%S"
2022-11-28 22:51:10

$ date +"%y-%m-%d"
22-11-28

$ date +"%s"  # seconds since 1970-01-01 00:00:00 UTC
1669647899
```

显示指定日期和时间

```console
$ date --date="1 day ago"
Sun 27 Nov 2022 10:59:30 PM CST

$ date --date="1 day"
Tue 29 Nov 2022 10:59:33 PM CST

# 年 月 日 时 分 秒 -> year month day hour minute second
```

显示指定格式的指定日期和时间

```console
$ date --date="1 day ago" +"%Y-%m-%d %H:%M:%S"
2022-11-27 23:02:43

$ date --date="1 day" +"%Y-%m-%d %H:%M:%S"
2022-11-29 23:02:47
```