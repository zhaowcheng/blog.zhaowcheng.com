---
title: Python 入门 - 1 - 简介
date: 2020-03-04 17:43:50 +0800
categories: [Python 入门]
tags: [python]
---

## Python 简介

Python 是由荷兰人 Guido van Rossum (“龟叔”)于 1989 年圣诞节期间，为了打发时间而编写。Python 这个名字取自作者很喜欢的 BBC 电视剧"Monty Python’s Flying Circus"。

Python 是在另一种编程语言 `ABC` 的基础上发展而来，ABC 是“龟叔”参与设计的一种教学语言，他认为 ABC 非常优美和强大，但是并没有取得成功，他认为是没有开放造成的，所以 Python 进行了开源。Python 还结合了很多 C 语言的使用习惯，比如 Python 中的 open 函数和 C 语言的 open 函数非常类似，Python 里同样也有文件描述符等概念。

Python 是一种 [解释型](https://zh.wikipedia.org/wiki/%E7%9B%B4%E8%AD%AF%E8%AA%9E%E8%A8%80)、[面向对象](https://zh.wikipedia.org/wiki/%E9%9D%A2%E5%90%91%E5%AF%B9%E8%B1%A1%E7%A8%8B%E5%BA%8F%E8%AE%BE%E8%AE%A1) 的语言，相比较而言 C 则是 [编译型](https://zh.wikipedia.org/wiki/%E7%B7%A8%E8%AD%AF%E8%AA%9E%E8%A8%80)、[面向过程](https://zh.wikipedia.org/wiki/%E8%BF%87%E7%A8%8B%E5%BC%8F%E7%BC%96%E7%A8%8B) 的语言。

解释型语言使用解释器在运行期间动态的逐条将语句解释为计算机可识别的机器代码，编译型语言需要提前把源代码编译为机器代码，然后运行。  

解释型语言相比编译型语言的主要缺点是运行速度慢，但是由于很多的应用不需要追求很高的性能，所以使用解释型语言已经完全满足运行速度的要求。  

解释型语言相比编译型语言的主要优点是开发速度快，因为开发过程中可以不用编译就立即运行而得到反馈，另外像 Python 这样的高级语言做了更高程度的抽象和封装，并且把很多常用操作封装为了标准库，所以在代码量上会比 C 语言少很多。而且 Python 可以使用即时编译([JIT](https://zh.wikipedia.org/zh-hans/%E5%8D%B3%E6%99%82%E7%B7%A8%E8%AD%AF))技术提高运行速度  

面向对象和面向过程语言的主要区别是面向对象可以定义类(class)，而面向过程语言只能定义函数，Python 既支持面向过程，也支持面向对象。关于面向对象和面向过程的更多区别请点击对应的链接进行深入了解。

## Python 应用

近些年来 Python 越来越火，应用也越来越广泛，根据编程语言排行榜 [TIOBE](https://www.tiobe.com/tiobe-index/) 2020 年 2 月最新的数据显示，目前 Python 的流行程度排行第 3，居于 Java 和 C 之后。

很多我们所熟知的网站也是使用 Python 开发，比如国外的 Youtube 、Instgram，国内的知乎、豆瓣，还有像 Google 、Yahoo 这样的大公司内部都在大量的使用 Python。

Python 在人工智能领域也非常流行，很多人工智能框架都选择使用 Python 语言，比如大名鼎鼎的 Google 人工智能框架 TensorFlow 就支持 Python。

另外 Python 在自动化测试方面也是应用广泛，比如开源的自动化测试框架 RobotFramework 就是使用 Python 编写的，很多公司在自己开发自动化测试框架时也大多选择使用 Python，比如华为就是在大量的使用 Python 来进行自动化测试。

由于 Python 简单、易学、易用的特点，所以在非编程相关的工作上也可以使用，比如日常办公中需要在大量的文本文件中搜索并替换某些内容，或者需要批量的整理操作大量文件，这个时候可以使用 Python 快速的编写一些小脚本来提升工作效率。相比 shell 或者 bat 等操作系统专用的脚本，Python 的跨平台特性使得使用 Python 编写的脚本使用更方便。而且目前的大多数 Linux 发行版和 OSX 等系统上都内置了 Python。

可以在 Python 官网 https://www.python.org/about/apps/ 上看到 Python 的很多应用列表。

## Python 版本

Python 自诞生以来经历了 2 个主要的大版本，一个是发布于 2000 年的 Python2，另一个是发布于 2008 年的 Python3。Python3 相比 Python2 有了很大的变更，所以 Python2 下编写的代码是不能直接在 Python3 上运行的。而且官方已经于 2020.1.1 停止了对 Python2 的维护，也就是说如果 Python2 出现了重大漏洞也不会再有更新的修复版本发布了，所以建议如果是新写的项目都使用 Python3。

如果由老的 Python2 的应用需要迁移到 Python3，可以参考官方迁移指南：https://docs.python.org/3/howto/pyporting.html  
更多关于 Python2 和 Python3 的区别可以参考：http://python-future.org/compatible_idioms.html

## Python 解释器

通常我们说 Python 是用 C 语言编写的，是因为官方下载的解释器 CPython 是使用 C 语言编写的，其实除了 CPython 之外还有很多其他的解释器。

> *以下内容引用自：https://www.liaoxuefeng.com/wiki/1016959663602400/1016966024263840*
>  
> **IPython**  
> IPython 是基于 CPython 之上的一个交互式解释器，也就是说，IPython 只是在交互方式上有所增强，但是执行 Python 代码的功能和 CPython 是完全一样的。好比很多国产浏览器虽然外观不同，但内核其实都是调用了 IE。  
> CPython 用`>>>`作为提示符，而 IPython 用`In [序号]:`作为提示符。
> 
> **PyPy**  
> PyPy 是另一个 Python 解释器，它的目标是执行速度。PyPy 采用 JIT 技术，对 Python 代码进行动态编译（注意不是解释），所以可以显著提高 Python 代码的执行速度。  
> 绝大部分 Python 代码都可以在 PyPy 下运行，但是 PyPy 和 CPython 有一些是不同的，这就导致相同的 Python 代码在两种解释器下执行可能会有不同的结果。如果你的代码要放到 PyPy 下执行，就需要了解 PyPy 和 CPython 的不同点。
> 
> **Jython**  
> Jython 是运行在 Java 平台上的 Python 解释器，可以直接把 Python 代码编译成 Java 字节码执行。
> 
> **IronPython**  
> IronPython 和 Jython 类似，只不过 IronPython 是运行在微软.Net 平台上的 Python 解释器，可以直接把 Python 代码编译成.Net 的字节码。

## Python 编辑器(IDE)

有很多的编辑器支持编写和调试 Python 程序，以下列出几个比较流行的，可以根据个人喜好进行选择：
* IDLE ：这个 Python 官方的 IDE，Windows 上安装 Python 后就会有，功能较简单，可以用于学习和测试一些语法。
* PyCharm ：这个是由 JetBrains 开发的 Python IDE，功能强大，有专业版和社区版，个人使用可以选择免费的社区版。
* VSCode ：这个是微软的 Visual Studio 的精简版，开源且支持大量的插件，通过安装 Python 插件可以用于 Python 开发。
* Vim ：如果是 Linux 下也可以使用这 Vim 加一些插件进行 Python 开发。

## 参考资料

- [Python 简介] ：https://www.liaoxuefeng.com/wiki/1016959663602400/1016959735620448
- [Whetting Your Appetite] ：https://docs.python.org/3.5/tutorial/appetite.html
- [Python-wikipedia] ：https://zh.wikipedia.org/wiki/Python#cite_note-python_history-3
