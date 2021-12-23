---
title: Python入门教程-9-输入输出
date: 2021-02-24 20:44:30 +0800
categories: [Python入门教程]
tags: []
---

# 终端的输入输出

## input

Python 提供了一个 `input` 函数供终端的输入使用，当程序执行到 `input` 处时会暂停并等待用户输入，用户输入完成并敲击回车后才会继续执行后续的代码。`input` 的返回值就是读取到的用户输入内容，还可以在调用 `input` 时传入一个字符串参数作为等待输入的提示信息显示。

```python
# 用 var 保存用户输入内容
>>> var = input()
'hello, world'
>>> var
'hello, world'
>>> 

# 等待输入时显示提示信息
>>> name = input('Please input your name:')
Please input your name:'tom'
>>> name
'tom'
>>> 
```

## print

Python 提供一个 `print` 函数，可用于向终端打印内容，`print` 函数的定义如下：

```python
print(*objects, sep=' ', end='\n', file=sys.stdout, flush=False)
```

根据定义：`print` 会把任意多个 `object` 使用 `str()` 方法转换为字符串，并且在多个 object 之间使用 `sep` 进行分割，并且在最后增加 `end`，`sep` 和 `end` 必须是字符串，然后将这些内容输出到 `file` 参数所指定的对象，`file` 参数指定的对象必须要有 `write(string)` 方法，默认 file 参数为 `sys.stdout`，即当前终端。

```python
# 向终端输出两个字符 a 和 b
>>> print('a', 'b')
a b
# 向终端输出 a 和 b，并且将 a 和 b 使用 - 进行分割
>>> print('a', 'b', sep='-')
a-b
# 向终端输出 a 和 b，并且在最后输出两个换行(\n)
>>> print('a', 'b', end='\n\n')
a b

>>>
```

需要注意的是 print 函数的 `sep`、`end`、`file` 和 `flush` 参数必须使用关键字参数的方式传入(即使用 name=value 的形式)，否则会被当作待打印的 `object` 对象。

# 文件的输入输出

# 引用资料

