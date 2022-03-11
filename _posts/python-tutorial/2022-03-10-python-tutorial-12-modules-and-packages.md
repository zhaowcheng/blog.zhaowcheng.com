---
title: Python 入门-12-模块和包
date: 2022-03-10 09:48:00 +0800
categories: [Python 入门]
tags: []
---

## 模块（module）

一个包含 Python 代码的 `.py` 文件就是一个 `模块（module）`，模块名就是 `不包含 .py 的文件名`，也可以通过模块的 `__name__` 属性获取。

一个模块可以被 `import` 引用，也可以当作脚本直接运行，模块中的 `定义` 和 `语句` 只在被 import 或直接运行的时候 `执行一次`。

例如现在有一个名为 `fibo.py` 的文件，其内容如下：

```python
def fib(n):
    a, b = 0, 1
    while b < n:
        print(b, end=' ')
        a, b = b, a+b
    print()

def fib2(n):
    result = []
    a, b = 0, 1
    while b < n:
        result.append(b)
        a, b = b, a+b
    return result

# 被当作脚本运行时会进入该 if 分支
if __name__ == "__main__":
    import sys
    fib(int(sys.argv[1]))
```

### import 模块

import 方式引用：

```python
>>> import fibo
>>> fibo.fib(1000)
1 1 2 3 5 8 13 21 34 55 89 144 233 377 610 987
>>> fibo.fib2(100)
[1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89]
>>> fibo.__name__
'fibo'
```

from ... import 方式引用：

```python
>>> from fibo import fib, fib2
>>> fib(500)
1 1 2 3 5 8 13 21 34 55 89 144 233 377
>>> from fibo import *  # 为避免名称冲突，建议尽量不要使用这种方式
>>> fib(500)
1 1 2 3 5 8 13 21 34 55 89 144 233 377
```

### 以脚本方式运行模块

```bash
$ python fibo.py 50
1 1 2 3 5 8 13 21 34
```

### 模块搜索路径

## 包（package）

## 引用资料

- [Modules] : https://docs.python.org/3.5/tutorial/modules.html
