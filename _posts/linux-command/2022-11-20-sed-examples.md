---
title: sed 命令使用示例
date: 2022-11-20 17:17:00 +0800
categories: [Linux 命令]
tags: [sed]
---

## 替换

把 `hello` 替换为 `world`

```console
$ sed 's/hello/world/g'
```

把第 2 到 5 行替换为一行 `hello world`

```console
$ sed '2,5c hello world'
```

## 插入

在第 2 行前面插入一行 `hello world`

```console
$ sed '2i hello world'
```

在第 2 行后面插入一行 `hello world`

```console
$ sed '2a hello world'
```

在包含 `hello` 行的前面插入一行 `world`

```console
$ sed '/hello/i world'
```

在包含 `hello` 行的后面插入一行 `world`

```console
$ sed '/hello/a world'
```

## 删除

删除第 2 行

```console
$ sed '2d'
```

删除第 2 到 5 行

```console
$ sed '2,5d'
```

删除第 2 到最后行

```console
$ sed '2,$d'
```

删除包含 `hello world` 的行

```console
$ sed '/hello world/d'
```

## 打印

打印第 2 行

```console
$ sed '2p'
```

打印第 2 到 5 行

```console
$ sed '2,5p'
```

打印第 2 到最后行

```console
$ sed '2,$p'
```

## 参考资料

- https://www.gnu.org/software/sed/manual/sed.html#Joining-lines

- https://www.twle.cn/l/yufei/man/man-basic-sed.html