---
title: Linux 上 ELF 文件依赖库的查找顺序
date: 2022-10-15 13:07:00 +0800
categories: [Linux 打包]
tags: [elf, ld.so, rpath]
---

Linux 上的 2 种 [ELF](https://en.wikipedia.org/wiki/Executable_and_Linkable_Format) 文件类型：`可执行文件`（Executable file）和 `共享对象文件`（Shared object file），它们在执行期间需要通过 `动态库链接器`（[ld.so](https://man7.org/linux/man-pages/man8/ld.so.8.html)）来查找其依赖的动态库文件，然而系统中可能在不同的目录下存在相同的动态库文件，那么执行时到底链接到哪个目录下的呢，本文将描述其在不同目录间的查找顺序。

## 如何识别 ELF 文件类型

Linux 上可通过 `file` 命令来查询文件类型，以 64 位系统为例，`可执行文件` 的查询结果中将包含如下内容

```console
ELF 64-bit LSB executable
```

`共享对象文件` 的查询结果中将包含以下内容：

```console
ELF 64-bit LSB shared object
```

## 如何查询依赖库

Linux 上可通过 `ldd` 命令来查询 `可执行文件` 或 `共享对象文件` 的依赖库，例如查询 `ls` 命令的依赖库：

```console
root@localhost:~# ldd /usr/bin/ls
        linux-vdso.so.1 (0x00007ffff2eff000)
        /$LIB/libonion.so => /lib/x86_64-linux-gnu/libonion.so (0x00007fbea7a43000)
        libselinux.so.1 => /lib/x86_64-linux-gnu/libselinux.so.1 (0x00007fbea7a05000)
        libc.so.6 => /lib/x86_64-linux-gnu/libc.so.6 (0x00007fbea7813000)
        libdl.so.2 => /lib/x86_64-linux-gnu/libdl.so.2 (0x00007fbea780d000)
        libpcre2-8.so.0 => /lib/x86_64-linux-gnu/libpcre2-8.so.0 (0x00007fbea777d000)
        /lib64/ld-linux-x86-64.so.2 (0x00007fbea7b70000)
        libpthread.so.0 => /lib/x86_64-linux-gnu/libpthread.so.0 (0x00007fbea775a000)
```

## 依赖库查找顺序

Linux 上查找依赖库是通过 `ld.so` 程序来完成的，其具体查找顺序如下：

1. ELF 文件头中 `DT_RPATH` 字段配置的目录：该字段是可选的，需要注意的是如果 ELF 文件头中同时包含了 `DT_RUNPATH` 时，则 `DT_RPATH` 将被忽略，可通过 `readelf -d FILENAME` 命令来查看是否包含 DT_RPATH 和 DT_RUNPATH。

2. 环境变量 `LD_LIBRARY_PATH` 中配置的目录。

3. ELF 文件头中 `DT_RUNPATH` 字段配置的目录：该字段也为可选的，需要注意的是该字段只会查找 `直接依赖` 而不查找 `间接依赖`，而 `DT_RPATH` 则会查找间接依赖。

4. 文件 `/etc/ld.so.cache` 中包含的动态库文件列表：该文件是 `ldconfig` 命令将 `/etc/ld.so.conf.d/` 目录下配置的目录列表中的所有动态库搜索后生成的一个缓存列表。

5. 默认系统库目录 `/lib` 和 `/usr/lib`：64 位系统则是 `/lib64` 和 `/usr/lib64`。

## rpath 中的特殊变量

DT_RPATH 和 DT_RUNPATH 统称为 `rpath`，可以通过在编译时通过编译参数编译进去，也可以在编译后通过其他工具（如 [patchelf](https://github.com/NixOS/patchelf)）来添加修改。

在 rpath 中有一些特殊变量及其含义如下：

- `$ORIGIN` : 表示当前 ELF 文件所在的目录。

- `$LIB` : 表示 `/lib` 或 `lib64` (64 位系统)。

## 参考资料

- https://man7.org/linux/man-pages/man8/ld.so.8.html