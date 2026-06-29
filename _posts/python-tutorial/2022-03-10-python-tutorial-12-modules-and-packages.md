---
title: Python 入门 - 12 - 模块和包
date: 2022-03-10 15:16:00 +0800
categories: [Python 入门]
tags: [python]
---

## 模块（module）

一个包含 Python 代码的 `.py` 文件就是一个 `模块（module）`，文件名去除 `.py` 后缀就是 `模块名`，模块名也可以通过模块的 `__name__` 属性获取。

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

### 导入模块

import 方式导入：

```python
>>> import fibo
>>> fibo.fib(1000)
1 1 2 3 5 8 13 21 34 55 89 144 233 377 610 987
>>> fibo.fib2(100)
[1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89]
>>> fibo.__name__
'fibo'
```

from ... import 方式导入：

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

### 内置模块（标准库）

Python 解释器内置了很多的模块（即标准库），这些库提供了很多的便利性，并且单独提供了文档对这些库进行说明：https://docs.python.org/3.5/library/index.html

### 模块搜索路径

当使用 `import` 导入模块时，Python 搜索这个模块的路径如下：

1. [内置模块列表](https://docs.python.org/3.5/library/index.html)
2. `sys.path` 列表，其包含如下目录（按顺序）：
    1. 包含输入脚本的目录（如果未指定输入脚本直接启动解释器则是当前目录）
    2. [PYTHONPATH](https://docs.python.org/3.5/using/cmdline.html#envvar-PYTHONPATH) 环境变量中的目录
    3. 其他安装时生成的默认路径（如第三方库安装目录 `site-packages`）

### 模块缓存

为了提升模块的 `加载` 速度，Python 在第一次 `import` 时会在模块文件所在目录下创建 `__pycache__` 目录，并将模块编译后的字节码文件（.pyc），以 `modname.version.pyc` 文件名格式缓存在该目录下。

例如一个模块文件名为 `mymod.py`，使用 `CPython 3.5` 在第一次加载后，会在该文件所在目录下生成路径为 `__pycache__/mymod.cpython-35.pyc` 的模块缓存文件，那么在下次加载该模块时，如果模块源文件（.py）没有修改（通过 .pyc 文件和对应 .py 文件的修改日期对比进行判断），则直接加载缓存的模块字节文件，如果有修改则重新生成缓存文件。

如果是在命令行以脚本方式直接执行模块文件，则不会生成缓存文件。

缓存模块字节文件还可以在源文件不存在的时候直接加载使用，例如删除 `mymod.py` 后把 `mymod.cpython-35.pyc` 从 `__pycache__` 中拷贝到上级目录（即原 mymod.py 所在目录），并且去掉文件名中 `version` 字段（即改名为 `mymod.pyc`），然后即可直接 `import mymod` 并使用。这种方式可以方便进行不带源文件分发使用，Python 还提供了 [compileall](https://docs.python.org/3.5/library/compileall.html#module-compileall) 标准库来进行批量编译源文件后分发使用。

需要注意的是缓存模块文件仅仅提升了 `加载` 速度，执行速度还是和源文件执行的方式一样的。

### 查看模块属性

可以使用内置函数 `dir()` 查看模块中定义的所有名称：

```python
>>> import builtins
>>> dir(builtins)  
['ArithmeticError', 'AssertionError', 'AttributeError', 'BaseException',
 'BlockingIOError', 'BrokenPipeError', 'BufferError', 'BytesWarning',
 'ChildProcessError', 'ConnectionAbortedError', 'ConnectionError',
 'ConnectionRefusedError', 'ConnectionResetError', 'DeprecationWarning',
 'EOFError', 'Ellipsis', 'EnvironmentError', 'Exception', 'False',
 'FileExistsError', 'FileNotFoundError', 'FloatingPointError',
 'FutureWarning', 'GeneratorExit', 'IOError', 'ImportError',
 'ImportWarning', 'IndentationError', 'IndexError', 'InterruptedError',
 'IsADirectoryError', 'KeyError', 'KeyboardInterrupt', 'LookupError',
 'MemoryError', 'NameError', 'None', 'NotADirectoryError', 'NotImplemented',
 'NotImplementedError', 'OSError', 'OverflowError',
 'PendingDeprecationWarning', 'PermissionError', 'ProcessLookupError',
 'ReferenceError', 'ResourceWarning', 'RuntimeError', 'RuntimeWarning',
 'StopIteration', 'SyntaxError', 'SyntaxWarning', 'SystemError',
 'SystemExit', 'TabError', 'TimeoutError', 'True', 'TypeError',
 'UnboundLocalError', 'UnicodeDecodeError', 'UnicodeEncodeError',
 'UnicodeError', 'UnicodeTranslateError', 'UnicodeWarning', 'UserWarning',
 'ValueError', 'Warning', 'ZeroDivisionError', '_', '__build_class__',
 '__debug__', '__doc__', '__import__', '__name__', '__package__', 'abs',
 'all', 'any', 'ascii', 'bin', 'bool', 'bytearray', 'bytes', 'callable',
 'chr', 'classmethod', 'compile', 'complex', 'copyright', 'credits',
 'delattr', 'dict', 'dir', 'divmod', 'enumerate', 'eval', 'exec', 'exit',
 'filter', 'float', 'format', 'frozenset', 'getattr', 'globals', 'hasattr',
 'hash', 'help', 'hex', 'id', 'input', 'int', 'isinstance', 'issubclass',
 'iter', 'len', 'license', 'list', 'locals', 'map', 'max', 'memoryview',
 'min', 'next', 'object', 'oct', 'open', 'ord', 'pow', 'print', 'property',
 'quit', 'range', 'repr', 'reversed', 'round', 'set', 'setattr', 'slice',
 'sorted', 'staticmethod', 'str', 'sum', 'super', 'tuple', 'type', 'vars',
 'zip']
```

## 包（package）

### 包的目录结构

Python 中当一个目录包含一个 `__init__.py` 文件（可以是空文件，也可以定义名称）时，这个目录就会被当作一个 `包（package）`，包内可以包含模块文件，也可以包含 `子包`，不同包内的模块名可以相同而互不冲突，这种机制可以方便对模块分类管理，例如一个处理音频文件的包目录结构如下：

```
sound/                          Top-level package
      __init__.py               Initialize the sound package
      formats/                  Subpackage for file format conversions
              __init__.py
              wavread.py
              wavwrite.py
              aiffread.py
              aiffwrite.py
              auread.py
              auwrite.py
              ...
      effects/                  Subpackage for sound effects
              __init__.py
              echo.py
              surround.py
              reverse.py
              ...
      filters/                  Subpackage for filters
              __init__.py
              equalizer.py
              vocoder.py
              karaoke.py
              ...
```

### 包的导入方式

包的用户可以从包中导入单个模块，例如:

```python
import sound.effects.echo
```

这会加载子模块 sound.effects.echo 。但引用它时必须使用它的全名。

```python
sound.effects.echo.echofilter(input, output, delay=0.7, atten=4)
```

导入子模块的另一种方法是

```python
from sound.effects import echo
```

这也会加载子模块 echo ，并使其在没有包前缀的情况下可用，因此可以按如下方式使用:

```python
echo.echofilter(input, output, delay=0.7, atten=4)
```

另一种形式是直接导入所需的函数或变量:

```python
from sound.effects.echo import echofilter
```

同样，这也会加载子模块 echo，但这会使其函数 echofilter() 直接可用:

```python
echofilter(input, output, delay=0.7, atten=4)
```

请注意，当使用 `from package import item` 时，item 可以是包的子模块（或子包），也可以是包中定义的其他名称，如函数，类或变量。 import 语句首先测试是否在包中定义了item，如果没有，它假定它是一个模块并尝试加载它。如果找不到它，则引发 `ImportError` 异常。

相反，当使用 `import item.subitem.subsubitem` 这样的语法时，除了最后一项之外的每一项都必须是一个包，最后一项可以是模块或包，但不能是前一项中定义的类或函数或变量。

### 包的 `__all__` 属性

包的 `__init__.py` 文件中可以定义一个名为 `__all__` 的列表，用来列出 `from package import *` 时导入的模块，假如 `sound/effects/__init__.py` 文件中包含如下定义：

```python
__all__ = ["echo", "surround", "reverse"]
```

那么在使用 `from sound.effects import *` 语句时只会导入 `echo`、`surround` 和 `reverse` 三个子模块。

如果没有定义 `__all__`，当使用 `from sound.effects import *` 语句时，实际上只导入了 `effects` 子包。

### 兄弟包的导入方式

在包中可以使用绝对路径导入兄弟包的模块，比如在上面的 sound 示例包中，在模块 `sound.filters.vocoder` 中导入 `sound.effects.echo` 模块的命令如下：

```python
from sound.effects import echo
```

也可以使用相对路径导入兄弟包的模块，比如在 `sound.effects.surround` 模块使用相对路径导入其他模块：

```python
from . import echo
from .. import formats
from ..filters import equalizer
```

请注意，相对导入是基于当前模块的名称进行导入的。由于主模块的名称总是 `__main__` ，因此用作 Python 应用程序主模块的模块必须始终使用绝对导入。

## 参考资料

- [Modules] : https://docs.python.org/3.5/tutorial/modules.html
