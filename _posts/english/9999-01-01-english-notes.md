---
title: 英语笔记
date: 9999-01-01 00:00:00 +0800
categories: [English]
tags: [english]
---

## 单词

- dot: 点（`.`）
- comma: 逗号（`,`）
- colon: 冒号（`:`）
- semicolon: 分号（`;`）
- question mark: 问号（`?`）
- ellipsis: 省略号（`...`）
- parentheses: 圆括号（`()`）
- braces: 大括号/花括号（`{}`）
- square brackets: 方括号（`[]`）
- angle brackets: 尖括号（`<>`）
- i.e.: 即，也就是
- e.g.: 比如
- tricky: 棘手

## 句子

- if it did much with shared memory then it would be prone to crashing along with the backends.（如果它对共享内存做了很多工作，那么它就很容易与后端一起崩溃。）
  - 生词: 
    - prone: 易于，倾向于（形容词）
  - 出处: https://github.com/postgres/postgres/blob/fdd82692230a4ffcc6c382a68401dd8c1bed8250/src/backend/postmaster/postmaster.c#L22

- Likewise, the Postmaster should never block on messages from frontend clients.（同样，postmaster 也不应该阻止来自前端客户端的消息。）
  - 生词: 
    - likewise: 同样地
  - 出处: https://github.com/postgres/postgres/blob/fdd82692230a4ffcc6c382a68401dd8c1bed8250/src/backend/postmaster/postmaster.c#L51

- If the same reason is signaled multiple times in quick succession.（如果连续多次发出相同的信号。）
  - 生词:
    - quick succession: 快速连续
  - 出处: https://github.com/postgres/postgres/blob/25505082f0e7aa6dc9cd068b0e5330bb1ca22751/src/include/storage/pmsignal.h#L29

- The postmaster process creates the shared memory and semaphore pools during startup, but as a rule does not touch them itself.（postmaster 进程在启动期间创建共享内存和信号量池，但通常不会自行触及它们。）
  - 生词:
    - as a rule: 通常来说
  - 出处: https://github.com/postgres/postgres/blob/fdd82692230a4ffcc6c382a68401dd8c1bed8250/src/backend/postmaster/postmaster.c#L15

- We can cope with simultaneous signals for different reasons.（我们可以处理由于不同原因而同时发出的信号。）
  - 生词:
    - simultaneous: 同时的
    - cope: 应付，对付
  - 出处: https://github.com/postgres/postgres/blob/25505082f0e7aa6dc9cd068b0e5330bb1ca22751/src/include/storage/pmsignal.h#L28

- as opposed to the crufty "poor man's multitasking" code that used to be needed.（而不是像以前那样需要笨拙的“穷人版多任务”代码。）
  - 生词:
    - as opposed to: 而不是
    - crufty: 笨拙的
    - used to be: 曾经是
  - 概念: 
    - poor man's multitasking（穷人版多任务）: 是一种在 单线程环境 或 资源受限系统（如嵌入式设备、旧版操作系统）中模拟多任务的方法。它通常不依赖操作系统级的线程或进程调度，而是通过 协作式多任务（Cooperative Multitasking） 或 状态机（State Machine） 实现任务的切换。
  - 出处: https://github.com/postgres/postgres/blob/fdd82692230a4ffcc6c382a68401dd8c1bed8250/src/backend/postmaster/postmaster.c#L28

- it ensures that blockages in non-multithreaded libraries like SSL or PAM cannot cause denial of service to other clients.（它确保 SSL 或 PAM 等非多线程库中的阻塞不会导致拒绝对其他客户端提供服务。）
  - 生词: 
    - blockage: 阻塞（名词）
    - denial: 拒绝（名词）
  - 出处: https://github.com/postgres/postgres/blob/fdd82692230a4ffcc6c382a68401dd8c1bed8250/src/backend/postmaster/postmaster.c#L30

- so as not to become stuck if a crashing backend screws up locks or shared memory.（以免因后端崩溃而导致锁或共享内存损坏而陷入困境。）
  - 生词: 
    - so as not: 以免（so as: 以便）
    - screw up: 搞砸

- essentially, bogus arguments on the command line.（本质上，命令行上的虚假参数。）
  - 生词: 
    - essentially: 本质上
    - bogus: 虚假的
  - 出处: https://github.com/postgres/postgres/blob/fdd82692230a4ffcc6c382a68401dd8c1bed8250/src/backend/postmaster/postmaster.c#L60

- Set up timeout handler needed to report startup progress.（设置报告启动进度所需的超时处理程序。）
  - 出处: https://github.com/postgres/postgres/blob/fdd82692230a4ffcc6c382a68401dd8c1bed8250/src/backend/access/transam/xlog.c#L5504

- The pg_wal directory may still include some temporary WAL segments used when creating a new segment, so perform some clean up to not bloat this path.  This is done first as there is no point to sync this temporary data.（pg_wal 目录可能仍包含一些在创建新 WAL 段时使用的临时 WAL 段文件，因此需要执行一些清理操作以避免该路径过度膨胀。此项操作会优先执行，因为同步这些临时数据毫无意义。）
  - 生词:
    - bloat: 膨胀
    - no point: 没有意义

- Installation on Ubuntu derivative distributions, such as Linux Mint, is not officially supported (though it may work).（Ubuntu 衍生发行版（例如 Linux Mint）上的安装不受官方支持（尽管可能有效）。）
  - 生词:
    - derivative: 衍生的，衍生物。
  - 出处: https://docs.docker.com/engine/install/ubuntu/#prerequisites

-  In many cases compilation is only necessary if you want the most bleeding edge versions or you are a package maintainer.（在许多情况下，仅当您想要最前沿的版本或您是软件包维护者时才需要编译。）
  - 生词：
    - bleeding edge: 前沿技术
  - 出处: https://postgis.net/docs/manual-3.5/postgis_installation.html#PGInstall

- The OID of the tablespace to which the relation containing the target page belongs.（目标页所属关系对应的表空间的OID）
  - 解析:
    - 主干结构（名词短语）
      - "The OID of the tablespace"（表空间的OID）这是整个句子的核心，表示“某个表空间的OID”。

    - 定语从句（修饰tablespace）
      - "to which the relation ... belongs"（某个关系所属的表空间）这是一个介词 + 关系代词（to which）引导的定语从句，修饰前面的 "tablespace"，说明是“某个关系所属的表空间”。
      - "the relation"（关系，指数据库中的表或索引等对象）
      - "belongs to the tablespace"（属于该表空间）（原句使用倒装结构 "to which ... belongs"，相当于 "the relation belongs to the tablespace"）

    - 分词短语（修饰relation）
      - "containing the target page"（包含目标页面的）这是一个现在分词短语，修饰 "the relation"，说明这个关系是“包含目标页面的”那个关系。
  - 出处: https://www.interdb.jp/pg/pgsql08/01.html

- This is a workaround for bogus C++ exceptions interaction with older development tools. If you experience weird problems (backend unexpectedly closed or similar things) try this trick. This will require recompiling your PostgreSQL from scratch, of course.（这是解决与旧开发工具交互时出现虚假 C++ 异常的变通方法。如果您遇到奇怪的问题（后端意外关闭或类似情况），请尝试此技巧。当然，这需要从头开始重新编译您的 PostgreSQL。）
  - 生词:
    - workaround: 解决办法
    - from scratch: 从零开始
  - 出处: https://postgis.net/docs/manual-3.5/postgis_installation.html#PGInstall

- A transaction snapshot is a dataset that stores information about whether all transactions are active at a certain point in time for an individual transaction. Here an active transaction means it is in progress or has not yet started.（事务快照是一组数据集，用于存储特定时间点上所有事务对单个事务而言是否处于活动状态的信息。此处"活动事务"指的是正在进行或尚未开始的事务。）
  - 出处: https://www.interdb.jp/pg/pgsql05/05.html

- They don’t interfere with each other.（因此它们彼此之间不会产生干扰）
  - 生词:
    - interfere: 干扰
  - 出处: https://nixos.org/guides/how-nix-works/

- A Nix expression describes everything that goes into a package build action (a “derivation”): other packages, sources, the build script, environment variables for the build script, etc.（Nix表达式完整定义了软件包构建过程（称为"derivation"）的所有要素：依赖的其他软件包、源代码、构建脚本、构建脚本的环境变量等。）
  - 生词:
    - derivation: 推导，派生
  - 出处: https://nixos.org/guides/how-nix-works/

- Nix tries very hard to ensure that Nix expressions are deterministic: building a Nix expression twice should yield the same result.（Nix 系统会严格确保 Nix 表达式的确定性：同一表达式的两次构建必须产生完全相同的结果。）
  - 生词:
    - deterministic: 确定性的

- Nix expressions generally describe how to build a package from source, so an installation action like `nix-env --install firefox` could cause quite a bit of build activity, as not only Firefox but also all its dependencies (all the way up to the C library and the compiler) would have to be built, at least if they are not already in the Nix store.（Nix 表达式通常定义了如何从源码构建软件包，因此执行诸如 `nix-env --install firefox` 这样的安装命令时，可能会引发大规模的构建过程——不仅需要构建 Firefox 本身，还包括其完整的依赖链（从最底层的 C 语言库到编译器），至少在这些组件尚未存入 Nix 存储仓库的情况下需要如此。）
  - 生词:
    - all the way up to: 一直到
  - 出处: https://nixos.org/guides/how-nix-works/

- In this section you will run two exotic programs called `cowsay` and `lolcat`.（在本节中，您将运行两个有趣的程序，分别名为 cowsay 和 lolcat。）
  - 生词:
    - exotic: 异国情调的，奇特的
  - 出处: https://nix.dev/tutorials/first-steps/ad-hoc-shell-environments

- What can you put in a shell environment? If you can think of it, there’s probably a Nix package of it.（你可以在 shell 环境中放些什么？只要你能想到，Nix 里应该都有相应的包。）
  - 出处: https://nix.dev/tutorials/first-steps/ad-hoc-shell-environments

- As with any programming language, the required amount of Nix language code closely matches the complexity of the problem it is supposed to solve, and reflects how well the problem – and its solution – is understood.（和其他编程语言类似，Nix 语言的代码量完全取决于问题的复杂程度，以及开发者对问题和解决方案的掌握深度。）
  - 出处: https://nix.dev/tutorials/nix-language

- Building software is a complex undertaking, and Nix both exposes and allows managing this complexity with the Nix language.（构建软件是一项复杂的任务，而 Nix 通过其独特的语言设计，既揭示了这种复杂性，又提供了管理这种复杂性的有效手段。）
  - 生词:
    - undertaking: 承诺，事业（undertake: 承诺做，答应做，从事）
    - expose: 揭示
  - 出处: https://nix.dev/tutorials/nix-language

- Equal amounts of prepended white space are trimmed from the result.（从结果中修剪掉等量的前置空白。）
  - 生词:
    - trim: 修剪
  - 出处: https://nix.dev/tutorials/nix-language#indented-strings

- Leaving out or passing additional attributes is an error.（遗漏或传递额外的属性是错误的。）
  - 生词:
    - leave out: 遗漏

- We recommend to at least skim them to familiarise yourself with what is available.（我们建议您至少浏览一下这些内容，以熟悉其中可用的内容。）
  - 生词:
    - skim: 浏览，撇
  - 出处: https://nix.dev/tutorials/nix-language#function-libraries

- One of Nix’s primary use-cases is in addressing common difficulties encountered with packaging software.（Nix 的主要用途之一是解决软件打包过程中遇到的常见问题。）
  - 出处: https://nix.dev/tutorials/packaging-existing-software

- In the long term, Nix helps tremendously with alleviating such problems.（从长远来看，Nix 对于缓解此类问题有极大帮助。）
  - 生词:
    - tremendously: 极大地
    - alleviate: 缓解
  - 出处: https://nix.dev/tutorials/packaging-existing-software

- But when first packaging existing software with Nix, it’s common to encounter errors that seem inscrutable.（但是，当第一次使用 Nix 打包现有软件时，经常会遇到一些难以理解的错误。）
  - 生词:
    - inscrutable: 难以理解的
  - 出处: https://nix.dev/tutorials/packaging-existing-software

- In case all else fails, it helps to become familiar with searching the Nixpkgs source code for keywords.（如果其他方法都失败了，熟悉在 Nixpkgs 源代码中搜索关键字会有所帮助。）
  - 出处: https://nix.dev/tutorials/packaging-existing-software

- This comes in handy for package sets where the recipes depend on each other.（这对于配方相互依赖的包集非常有用。）
  - 生词:
    - handy: 便利
    - comes in handy: 派上用场
  - 出处: https://nix.dev/tutorials/callpackage#interdependent-package-sets

- Coercion of paths to strings.（强制把路径转换为字符串）
  - 生词:
    - coercion: 胁迫（n）
  - 出处: https://nix.dev/tutorials/working-with-local-files#working-with-local-files

- The BufMappingLock is split into partitions to reduce contention in the buffer table (the default is 128 partitions). Each BufMappingLock partition guards a portion of the corresponding hash bucket slots.（BufMappingLock 被拆分成多个分区，以减少缓冲表的争用（默认为 128 个分区）。每个 BufMappingLock 分区守护着相应哈希桶槽的一部分。）
  - 生词:
    - contention: 争论
    - portion: 部分
