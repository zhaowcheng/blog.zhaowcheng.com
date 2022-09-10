---
title: 一种让 Linux 上的 C/C++ 程序自带依赖库的打包方式
date: 2022-09-03 15:34:00 +0800
categories: [杂七杂八]
tags: [linux]
---

Linux 上的 `C/C++` 程序编译打包后拿到 `同 CPU 架构` 的其他 Linux 系统上运行时，通常会由于目标系统上缺少该程序所需的库而无法运行。

这个问题在一个连接上互联网的 Linux 系统上可以很容易的通过 `yum` 或 `apt` 安装缺少的依赖库来解决，但是如果是在一个无法使用 `yum` 和 `apt` 的内网系统上，则非常麻烦。

本文介绍一种打包方式，让打包后的程序即使在目标系统上没有该程序所需的库时，也能正常运行。

## 步骤

以下为该方式的详细步骤：

### 第一步：编译平台的选择

选择一个 `libc` 版本 `小于等于` 该程序需要适配的所有系统中 libc 版本最小的系统。

比如该程序需要适配 2 个系统，这两个系统的 libc 版本分别为 `2.23` 和 `2.28`，则选择一个 libc 版本 `小于等于 2.23` 的系统作为编译平台。

### 第二步：拷贝依赖库

在编译完成后，打包之前，通过 `ldd` 命令查询该程序中所有 `ELF` 文件的依赖库，并将查询到的 `除 libc` 以外的所有依赖库拷贝到该程序的安装目录中（通常是安装目录下的 lib 目录），然后再进行打包。  

如果打包方式为 `rpm`，建议在 `spec` 文件中添加 `AutoReqProv: no` 选项。

### 第三步(可选)：添加 RPATH

在打包之前，给所有该程序中的 `ELF` 文件添加 `RPATH` 指向其自带的 `lib` 目录，让程序在运行时自动优先查找自己的 lib 目录中的库文件，这样程序运行时就不需要目标系统上安装有其依赖库了。

当然也可以不添加 RPATH，而是在使用时配置 `LD_LIBRARY_PATH` 环境变量指向其自带的 `lib` 目录达到同样的效果。

## 示例

下面以 `postgresql` 为例对该打包方式进行演示：

### 第一步：编译平台的选择

选择 `CentOS 6` 作为编译平台，其 `libc` 版本为 `2.12`：

```console
[root@el6-x86_64 ~]# ls -l /lib64/libc.so.6
lrwxrwxrwx 1 root root 12 Jul  8 13:13 /lib64/libc.so.6 -> libc-2.12.so
[root@el6-x86_64 ~]# tar xf postgresql-9.6.24.tar.gz
[root@el6-x86_64 ~]# cd postgresql-9.6.24/
[root@el6-x86_64 postgresql-9.6.24]# ./configure --prefix=/usr/local/pg9
...
[root@el6-x86_64 postgresql-9.6.24]# make -j`nproc` && make install
...
[root@el6-x86_64 postgresql-9.6.24]# cd /usr/local/pg9
[root@el6-x86_64 pg9]# ls
bin include lib share
[root@el6-x86_64 pg9]# 
```

### 第二步：拷贝依赖库

```console
[root@el6-x86_64 ~]# ./copy_deps.sh /usr/local/pg9/ /usr/local/pg9/lib
...
Processing /lib64/libc.so.6
Processing /lib64/libdl.so.2 
Processing /lib64/1ibm.so.6
Processing /lib64/libpthread.so.0 
Processing /lib64/libreadline.so.6
`/lib64/libreadline.so.6' -> `/usr/local/pg9/1ib/libreadline.so.6' 
Processing /lib64/1ibrt.so.1
Processing/lib64/libtinfo.so.5
`/lib64/libtinfo.so.5' -> `/usr/local/pg9/1ib/libtinfo.so.5' 
Processing /lib64/1ibz.so.1
`/lib64/libz.so.1' -> `/usr/local/pg9/1ib/libz.so.1' 
Processing /usr/local/pg9/lib/libecpg.so.6
Processing /usr/local/pg9/1ib/libpgtypes.so.3 
Processing /usr/local/pg9/lib/libpq.so.5 
[root@el6-x86_64 ~]# 
```

以下为 `copy_deps.sh` 脚本内容：

```sh
#/bin/bash -e
# Copy the deps of all elf files in `ELFDIR` to `LIBDIR`.

PROGNAME=$(basename $0)
if [[ $# != 2 ]]; then
    echo "Usage: $PROGNAME ELFDIR LIBDIR" >&2
    exit 1
fi

ELFDIR=$1
LIBDIR=$2

for elf in `find $ELFDIR -type f -exec file {} + | grep ELF | cut -d: -f1`; do 
    echo "Analysing $elf"
    ldd $elf
    for sopath in `ldd $elf | grep -E '.+.so.* => /.+.so.* \(θx.+\)' | awk '{print $3}'`; do 
        sopaths+=($sopath)
    done
done

sopaths=(`for i in ${sopaths[*]}; do echo $i; done | sort -u`) 

for sopath in ${sopaths[*]}; do
    echo "Processing $sopath" 
    soname=`basename $sopath`
    if [[ (! -e $LIBDIR/$soname) ]]; then
        if [[ `which dpkg 2> /dev/null` ]]; then
            owninfo=`dpkg -S $sopath 2> /dev/null ||:`
        else
            owninfo=`rpm -qf $sopath 2> /dev/null ||:`
        fi
        if [[ ! $owninfo =~ ^glibc|^libc6 ]]; then 
            cp -v $sopath $LIBDIR
        fi
    fi
done
```

### 第三步(可选)：添加 RPATH

```console
[root@el6-x86_64 ~]# ./set_relative_rpath.sh /usr/local/pg9/ /usr/local/pg9/lib
Set the rpath of /usr/local/pg9/lib/libz.so.1 to $ORIGIN
Set the rpath of /usr/local/pg9/1ib/libecpg_compat.so.3.8 to $ORIGIN
Set the rpath of /usr/local/pg9/1ib/libreadline.so.6 to $ORIGIN
Set the rpath of /usr/local/pg9/1ib/libtinfo.so.5 to $ORIGIN
Set the rpath of /usr/local/pg9/1ib/libecpg.so.6.8 to $ORIGIN
Set the rpath of/usr/local/pg9/1ib/postgresq1/utf8_and_uhc.so to $ORIGIN/..
Set the rpath of/usr/local/pg9/1ib/postgresq1/latin2_and_win1250.so to $ORIGIN/..
...
Set the rpath of/usr/local/pg9/bin/clusterdb to $ORIGIN/../lib
Set the rpath of /usr/local/pg9/bin/postgres to $ORIGIN/../1ib
Set the rpath of/usr/local/pg9/bin/pg_restore to $ORIGIN/../1ib
Set the rpath of/usr/local/pg9/bin/ecpg to $ORIGIN/../lib 
[root@el6-x86_64 ~]# 
```

以下为 `set_relative_rpath.sh` 脚本内容：

```sh
#/bin/bash -e
# Set the rpath of all elf files in `ELFDIR` to relative paths to `LIBDIR`.

PROGNAME=$(basename $0)
if [[ $# != 2 ]]; then
    echo "Usage: $PROGNAME ELFDIR LIBDIR" >&2
    exit 1
fi

ELFDIR=$1
LIBDIR=$2

for elf in $(find $ELFDIR -type f -exec file {} + | grep ELF | cut -d: -f1); do
    elf_parentdir=$(dirname $elf)
    relative_path=$(realpath --relative-to=$elf_parentdir $LIBDIR)
    if [[ $relative_path == '.' ]]; then
        relative_rpath="$ORIGIN"
    else
        relative_rpath="$ORIGIN/$relative_path"
    fi
    if [[ $(patchelf --print-rpath $elf) != $relative_rpath ]]; then
        echo "Set the rpath of $elf to $relative_rpath"
        patchelf --set-rpath $relative_rpath $elf
    fi  
done
```

### 第四步：验证

将 `Centos 6` 上的 `postgresql` 安装目录打包:

```console
[root@el6-x86_64 ~]# cd /usr/local/
[root@el6-x86_64 local]# tar cf pg9.tar ./pg9/
[root@el6-x86_64 local]# ls
bin doc etc games include lib lib64 libexec patchelf pg9 pg9.tar pgsql sbin share src ssl
[root@el6-x86_64 local]#
```

将打包的 `postgresql` 放到另外一个 `Ubuntu 20` 系统上，该系统 `libc` 版本为 `2.31`，验证程序是否可正常使用：

```console
root@ubt20-x86-64:~# ls -l /lib/x86_64-linux-gnu/libc.so.6
lrwxrwxrwx 1 root root 12 Dec 16 2020 /lib/x86_64-linux-gnu/libc.so.6 -> libc-2.31.so
root@ubt20-x86-64:~# tar xf pg9.tar
root@ubt20-x86-64:~# cd pg9/
root@ubt20-x86-64:~/pg9# ldd ./bin/psql
        linux-vdso.so.1 (0x00097ffe0ace7000)
        libpq.so.5 => /root/pg9/./bin/../lib/libpq.so.5 (0x00007f374e68a000)
        libreadline.so.6 => /root/pg9/./bin/../lib/libreadline.so.6 (0x0000003fd9200000)
        libm.so.6 => /lib/x86_64-linux-gnu/libm.so.6 (0x00007f374e52f000)
        libc.so.6 => /lib/x86_64-linux-gnu/libc.so.6 (0x00007f374e33d090)
        libpthread.so.Q => /lib/x86_64-linux-gnu/libpthread.so.0 (0x00007f374e31a000)
        libtinfo.so.5 => /root/pg9/./bin/../lib/libtinfo.so.5 (0x0000603fdaa00000)
        /lib64/ld-linux-x86-64.so.2 (0x00007f374e8b5000)
root@ubt20-x86-64:~/pg9# ./bin/psql -V
psql (PostgreSQL) 9.6.24
root@ubt20-x86-64:~/pg9# 
```