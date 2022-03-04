---
title: Python 入门-11-类
date: 2022-02-24 11:05:00 +0800
categories: [Python 入门]
tags: []
---

Python 类源自于 `C++` 和 `Modula-3` 这两种语言的类机制的结合。

## 作用域和命名空间

`作用域（scope）` 指的是 Python 代码中的一个文本区域，分为以下几类：

- 模块
- 类
- 函数

`命名空间（namespace）` 是一个名字到对象的映射，一个作用域对应会有一个命名空间来保存该作用域中的 `名称（name）`，Python 中按照以下顺序去查找一个名称：

1. `最内部作用域`的命名空间（包含局部名称）
2. 最内部作用域与最近的作用域之间的 `中间作用域` 的命名空间（包含非全局名称 `nonlocal`）
3. 当前模块的命名空间（包含全局名称 `global`）
4. 内置名称模块（builtins）的命名空间

命名空间是动态创建的，不同时刻创建的命名空间具有不同的生存期：

- 包含内置名称的命名空间（builtins）是在 Python 解释器启动时创建的，会持续到解释器退出；
- 模块的全局命名空间在模块被读入时创建，也会持续到解释器退出（）；
- 函数的本地命名空间在函数被调用时创建，当函数返回或者抛出异常时被删除（递归调用的函数每次都有自己的本地命名空间）；

以下是一个作用域和命名空间的示例：

```python
def scope_test():
    def do_local():
        spam = "local spam"

    def do_nonlocal():
        nonlocal spam
        spam = "nonlocal spam"

    def do_global():
        global spam
        spam = "global spam"

    spam = "test spam"
    do_local()
    print("After local assignment:", spam)
    do_nonlocal()
    print("After nonlocal assignment:", spam)
    do_global()
    print("After global assignment:", spam)

scope_test()
print("In global scope:", spam)

# 其输出内容是：
'''
After local assignment: test spam
After nonlocal assignment: nonlocal spam
After global assignment: nonlocal spam
In global scope: global spam
'''
```

## 类定义

__init__
self
访问限制

## 类与实例

类是抽象模板，实例是根据类创建出来的具体的对象
类属性与实例属性

## 类继承

## 获取对象属性

## 类的一些特殊属性

## 引用资料

- [Classes] : https://docs.python.org/3.5/tutorial/classes.html
