---
title: Nix 入门 - 1 - 简介
date: 2026-06-29 18:22:00 +0800
categories: [Nix 入门]
tags: [nix]
---

## 1 Nix 是什么

Nix 是一个纯函数式的包管理器。

纯函数式的意思是输入决定输出：比如一个求平方的函数 f，当输入为 1 时输出为 1，当输入为 2 时输出为 4。只要输入不变，输出就不变，输入改变，输出一般也会改变。虽然从理论上来说纯函数式也有可能存在不同的输入得到相同的输出的情况，但是像 Nix 这种输入内容非常多而且使用哈希算法的情况下概率非常小，这个在密码学上叫做哈希碰撞，我们在实际使用中几乎不可能碰到。

Nix 把一个包的源码、依赖、构建脚本、构建参数等作为输入计算出一个 hash 值作为安装路径的一部分，比如：

```plain
/nix/store/b6gvzjyb2pg0kjfwrjmg1vfhh54ad73z-firefox-33.1/
```

一个包的安装路径是`非全局且不可变的（Immutable）`，非全局的意思就是不直接安装到 /usr/bin 这样的系统全局目录中，不可变指的是如果包的源码、依赖、构建脚本、构建参数等发生变化，那么重新构建后的安装路径会是一个新的安装路径，原来的包安装路径始终不变。

## 2 Nix 能解决什么问题

Nix 的产生是为了解决 Unix/Linux 平台上的传统的软件部署（Software Deployment）方式（如 rpm, dpkg）所存在的问题，比较典型的一个问题就是`依赖地狱（Dependency Hell）`，依赖地狱是指由于软件之间复杂的依赖关系，导致安装、升级、降级或共存变得困难，而 Nix 的[作者](https://edolstra.github.io/)认为，这一切问题的根源都是由于把软件安装到了 `/usr` 这个`全局可变的`目录中，所以 Nix 借鉴了函数式语言的思想并且把软件都安装到类似 `/nix/store/b6gvzjyb2pg0kjfwrjmg1vfhh54ad73z-firefox-33.1/` 这样的`非全局且不可变的`目录中。

下面将对依赖地狱主要表现的几个方面以及 Nix 是如何解决的进行说明。

### 2.1 多版本共存困难

像 rpm 这样的包管理器通常把一个包安装到系统全局目录中（如 `/usr/bin`, `/usr/lib`），假如有一个名为 hello-1.0.rpm 的包安装后，增加了一个 `/usr/bin/hello` 的可执行程序，如果你想同时再安装一个 hello-2.0.rpm 的包，就会和 hello-1.0 冲突。虽然 rpm 也支持 `--prefix` 这样的选项把包安装到其他路径，或者可以把 2.0 的程序改名为 hello2，但是这些方法都会使得管理和使用变得很麻烦，而且在多个软件依赖同一个库的不同版本的情况下将会变的更麻烦。

前面讲了，Nix 通过会把包的源码、依赖、构建脚本、构建参数等作为输入计算出一个 hash 值作为安装路径的一部分，同一个软件的不同版本最后的安装路径肯定不同，这样自然就不会冲突，安装以后可以通过一条命令就能很方便的切换到包含不同版本的同一程序的 Shell 环境。

### 2.2 依赖声明不精确和完整

依赖分为两种：构建时依赖和运行时依赖。

rpm 以 `.spec` 文件作为构建输入，该文件中用 `BuildRequires` 和 `Requires` 分别声明构建时依赖和运行时依赖，但是只能声明包名和一个版本范围（如 >= 1.0），这种方式不够精确，当一个依赖从 1.0 升级到 2.0 之后如果发生了向下不兼容的改动（比如删掉了一些接口），可能就会导致依赖在上面的软件构建或运行失败，即使是同一个版本的依赖，如果其构建参数不同，也可能导致功能的不同，同样也可能会导致依赖在上面的软件失败。

现代 rpm 会在打包时自动扫描包内程序的依赖然后作为其运行时依赖写入包的元数据中，这样避免了运行时依赖不完整的问题，但是构建时依赖还是需要人为指定，如果指定不完整，就会导致在 A 机器上能构建成功，但是拿到 B 机器上可能就会构建失败。

构建时依赖的不精确和完整会导致构建环境的不可复现性，是对打包工作者的困扰。运行时依赖不精确和完整会导致软件运行失败，是对用户的困扰。

Nix 是一个完全自包含（Closure）的系统，不依赖系统上的任何软件（包括 glibc），所有的都是使用自己的，只有当你完整的指定了所有依赖后，你才可能构建成功一个软件，而且你指定的每个依赖都对应着 /nix/store 中的一个精确的构建产物，可以通过这些指定的内容复现出一个完全一致的构建环境。

Nix 的运行时依赖是在编译阶段通过 gcc 编译参数写入 ELF 文件的 RUNPATH 中的，最后还会在 fixup 阶段使用 patchelf 进行一次修正，保证依赖都是完整精确的。

### 2.3 升级不具有原子性且不可回滚

rpm 升级是直接覆盖原有安装路径，这样会导致两个问题：一是在升级过程中如果有依赖该包的程序启动时，可能会由于同时使用新老版本的文件而导致出错；二是升级后有可能导致依赖该包的其他软件无法工作，并且无法回滚。

Nix 得益于 `/nix/store` 的设计，升级一个包实际上是安装了一个新包，老的包仍然存在，要么安装成功使用新包，要么安装失败仍然使用老包，对用户来说，具有原子性。而且由于老包还在，如果升级后发现新包有问题，随时可以一键切换回老包使用，也就是回滚。

## 3 术语表

下面对一些常见的属于进行说明，完整的术语表请查看[官方文档](https://nix.dev/manual/nix/2.28/glossary.html)。

### 3.1 Nix store

Nix store 是一个抽象概念，表示一个不可变（immutable）文件系统，用来存储构建产物、源码、derivation 等，常见的就是 `/nix/store` 本地目录的实现方式，但是也还有别的方式，详情可见[官方文档](https://nix.dev/manual/nix/2.28/store/index.html)。

### 3.2 Nix expression

Nix 中构建的基本单位被称作`组件（component）`，而 Nix expression 就是用来描述一个组件应该被如何构建，比如它的源码位置、构建时依赖、运行时依赖、编译参数、编译步骤等，通常以 `.nix` 格式的文件来存储。

### 3.3 Nix language

Nix language 是用来编写 Nix expression 的一种声明式语言。

### 3.4 Store derivation

Nix expression 是使用面向人类设计的高级语言 Nix language 编写的，但是对于 Nix 系统而言不够底层，所以在构建包之前，Nix 会先把 Nix expression 翻译为更底层的表达方式，而翻译之后的内容就是 `derivation（派生）`，然后使用 derivation 进行构建。derivation 通常以 `.drv` 文件的格式存储在 Nix store 中，比如 `/nix/store/hashxxx-openssl-1.1.1.drv`。

### 3.5 Nixpkgs

Nixpkgs (Nix Packages collection) 是一个 Nix expression 的集合，包含了几乎所有常见的开源软件，源码地址是 https://github.com/nixos/nixpkgs。

### 3.6 Binary cache

Binary cache 也是一种 Nix store，是用来保存已构建好的包，便于其他 Nix 直接下载而无需重复构建，可以是本地的，也可以通过 HTTP, S3 等方式访问，官方源地址是 https://cache.nixos.org/。

### 3.7 NixOS

NixOS 是一个基于 Nix 的 Linux 发行版，它不仅用 Nix 管理包，还用 Nix 管理系统配置，所以 NixOS 可以随时回滚到之前的任意状态。

## 4 学习资料

- [The Purely Functional Software Deployment Model](https://edolstra.github.io/pubs/phd-thesis.pdf): Nix 论文。

- [nix.dev](https://nix.dev/): 官方手册。

- [Zero to Nix](https://zero-to-nix.com/): 快速了解 Nix 的教程。

- [Nix Pills](https://nixos.org/guides/nix-pills/): 认可度高的非官方 Nix 教程。

- [NixOS & Flakes Book](https://nixos-and-flakes.thiscute.world/zh/): 非官方的 NixOS 与 Flakes 新手指南。

- [NixOS-CN](https://nixos-cn.org/): 非官方的 NixOS 中文文档。

- [Noogle](https://noogle.dev/): Nix 函数库搜索器。

## 5 参考资料

[Introduction] : https://nix.dev/manual/nix/2.28/introduction.html

[Why You Should Give it a Try] : https://nixos.org/guides/nix-pills/01-why-you-should-give-it-a-try.html

[The Purely Functional Software Deployment Model]: https://edolstra.github.io/pubs/phd-thesis.pdf
