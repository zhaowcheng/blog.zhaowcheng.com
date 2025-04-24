---
title: "fpm: 一个跨平台且支持多种包格式的打包工具"
date: 2022-09-04 20:42:00 +0800
categories: [Linux 打包]
tags: [fpm]
---

通过《[一种让 Linux 上的 C/C++ 程序自带依赖库的打包方式](/posts/a-packaging-method-with-its-own-deps/)》和《[国产操作系统和 CPU 分类](/posts/classification-of-chinese-os-and-cpu/)》两篇文章，介绍了一种针对 Linux 上的 C/C++ 程序的简化打包数量的方式，从一次打需要适配的操作系统和 CPU 组合数量的包，简化为 `CPU 架构数 * 2` 的数量，那么在准备编译环境的时候也就需要准备 `CPU 架构数 * 2` 个。

现在介绍一个打包工具 [fpm](https://github.com/jordansissel/fpm) ，这是一个 `跨平台` 且 `支持多种包格式` 的打包工具，通过它可以在一个系统上同时打出 `rpm` 和 `deb` 的包，这样就可以把编译环境的数量从 `CPU 架构数 * 2` 减少到 `CPU 架构数`，进一步提高打包效率。

fpm 相比 rpm 和 deb 原生的打包方式更简单，且打包时间更短，下面演示使用 fpm 打包 `postgresql`：

```console
[root@el6-x86_64 fpm_example]# ls
pg9
[root@el6-x86_64 fpm_examplej# ls pg9/
bin include lib share
[root@el6-x86_64 fpm_example]# fpm -s dir -t rpm -n postgresql -v 9.6.24 --prefix /usr/local ./pg9
Created package {:path=>"postgresql-9.6.24-1.x86_64.rpm")
[root@el6-x86_64 fpm_example]# fpm -s dir -t deb -n postgresql -v 9.6.24 --prefix /usr/local ./pg9
Created package {:path=>"postgresql_9.6.24_amd64.deb")
[root@el6-x86_64 fpm_example]# ls
pg9 postgresql-9.6.24-1.x86_64.rpm postgresql_9.6.24_and64.deb
[root@el6-x86_64 fpm_example]# rpm -ivh postgresql-9.6.24-1.x86_64.rpm
Preparing...           ########################################### [100%]
    1:postgresql       ########################################### [100%]
[root@el6-x86_64 fpm_example]# ls /usr/local/pg9/
bin include lib share
[root@el6-x86_64 fpm_example]# 
```

更多关于 fpm 的说明请参考其 [官方文档](https://fpm.readthedocs.io/en/v1.14.2/)