---
title: Python 入门-10-异常
date: 2022-02-11 14:12:00 +0800
categories: [Python 入门]
tags: []
---

## 异常简介

`异常（Exception）` 即程序执行过程中产生的预期以外的错误，例如有一个脚本 `test.py`，其内容如下：

```python
#!/bin/python3

print('2' + 2)
```

当执行该脚本时会产生如下异常：

```bash
[root@localhost ~] python3 test.py 
Traceback (most recent call last):
  File "test.py", line 3, in <module>
    print('2' + 2)
TypeError: can only concatenate str (not "int") to str
```

上面打印的内容称为 `异常栈`，以 File 开头的那一行指明了产生异常的位置（即 test.py 的第 3 行），接下来一行即产生异常的语句（即 print('2' + 2)），最后一行为异常类型以及异常消息，通过查看异常栈可以准确定位到产生异常的代码位置并进行修复。

## 异常处理

### try

Python 中使用 `try` 语句进行异常处理，其语法定义如下：

```
try_stmt  ::=  try1_stmt | try2_stmt
try1_stmt ::=  "try" ":" suite
               ("except" [expression ["as" identifier]] ":" suite)+
               ["else" ":" suite]
               ["finally" ":" suite]
try2_stmt ::=  "try" ":" suite
               "finally" ":" suite
```

以下是一个简单的示例，该示例会一直等到用户输入一个整数为止，如果输入的不是整数，就会进入到 except 子句中执行 print 打印错误提示：

```python
>>> while True:
...     try:
...         x = int(input("Please enter a number: "))
...         break
...     except ValueError:
...         print("Oops!  That was no valid number.  Try again...")
...
```

### except

except 后面的异常类型可以是多个，使用圆括号括起来，表示捕获其中任一异常类型：

```python
except (RuntimeError, TypeError, NameError):
```

except 后面也可以不接异常类型，表示捕获任意异常：

```python
except:
    print("Some error occurred.")
```

except 后面还可以接一个 `as` 子句来保存异常实例，以便后续进行处理：

```python
except OSError as err:
    print("OS error: {0}".format(err))
```

try 后面也可以同时接多个 except 子句，当发生异常时会按照顺序从上往下匹配，如果其中某个 except 子句匹配上了，后面的 except 子句就会跳过:

```python
import sys

try:
    f = open('myfile.txt')
    s = f.readline()
    i = int(s.strip())
except OSError as err:
    print("OS error: {0}".format(err))
except ValueError:
    print("Could not convert data to an integer.")
except:
    print("Unexpected error:", sys.exc_info()[0])
    raise
```

当产生的异常属于某个 except 子句后面的异常类的子类时，也会被捕获，比如以下示例中由于 C 和 D 都是 B 的子类，所以最终打印结果将是 `B B B`：

```python
class B(Exception):
    pass

class C(B):
    pass

class D(C):
    pass

for cls in [B, C, D]:
    try:
        raise cls()
    except B:
        print("B")
    except C:
        print("C")
    except D:
        print("D")
```

### else

在 except 子句后面还可以接一个 `else` 子句（如果有多个 except，else 必须放在所有 except 后面），当没有异常发生时，才会进入到 else 子句：

```python
try:
    print('hello, world')
except:
    print('error')
else:
    print('no error')
```

### finally

在 try 语句的最后（即 except 和 else 后面）还可以接一个 `finally` 子句，无论是否发生异常，最终都会进入 finally 子句，所以通常可以在 `finally` 子句中进行一些清理工作：

```python
try:
    print('hello, world')
except:
    print('error')
else:
    print('no error')
finally:
    print('finished')
```

## 抛出异常

`raise` 语句可以主动抛出异常：

```python
>>> raise NameError('HiThere')
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
NameError: HiThere
```

`raise` 后面可以是一个异常类或者一个异常实例，如果接的是一个异常类则相当于无参数的异常类实例：

```python
raise ValueError  # 相当于 'raise ValueError()'
```

在 `except` 子句中还可以使用不接任何参数的 `raise` 语句，这样表示直接将 except 捕获的异常再次原样抛出：

```python
>>> try:
...     raise NameError('HiThere')
... except NameError:
...     print('An exception flew by!')
...     raise
...
An exception flew by!
Traceback (most recent call last):
  File "<stdin>", line 2, in <module>
NameError: HiThere
```

## 自定义异常

Python 提供了很多了内置异常类，其继承关系如下：

```
BaseException
 +-- SystemExit
 +-- KeyboardInterrupt
 +-- GeneratorExit
 +-- Exception
      +-- StopIteration
      +-- StopAsyncIteration
      +-- ArithmeticError
      |    +-- FloatingPointError
      |    +-- OverflowError
      |    +-- ZeroDivisionError
      +-- AssertionError
      +-- AttributeError
      +-- BufferError
      +-- EOFError
      +-- ImportError
      +-- LookupError
      |    +-- IndexError
      |    +-- KeyError
      +-- MemoryError
      +-- NameError
      |    +-- UnboundLocalError
      +-- OSError
      |    +-- BlockingIOError
      |    +-- ChildProcessError
      |    +-- ConnectionError
      |    |    +-- BrokenPipeError
      |    |    +-- ConnectionAbortedError
      |    |    +-- ConnectionRefusedError
      |    |    +-- ConnectionResetError
      |    +-- FileExistsError
      |    +-- FileNotFoundError
      |    +-- InterruptedError
      |    +-- IsADirectoryError
      |    +-- NotADirectoryError
      |    +-- PermissionError
      |    +-- ProcessLookupError
      |    +-- TimeoutError
      +-- ReferenceError
      +-- RuntimeError
      |    +-- NotImplementedError
      |    +-- RecursionError
      +-- SyntaxError
      |    +-- IndentationError
      |         +-- TabError
      +-- SystemError
      +-- TypeError
      +-- ValueError
      |    +-- UnicodeError
      |         +-- UnicodeDecodeError
      |         +-- UnicodeEncodeError
      |         +-- UnicodeTranslateError
      +-- Warning
           +-- DeprecationWarning
           +-- PendingDeprecationWarning
           +-- RuntimeWarning
           +-- SyntaxWarning
           +-- UserWarning
           +-- FutureWarning
           +-- ImportWarning
           +-- UnicodeWarning
           +-- BytesWarning
           +-- ResourceWarning
```

但是用户也可以自定义异常类，自定义异常类必须直接或间接的继承自 `Exception`，通常一个异常类里边什么都不做，或者最多定义几个属性用于保存异常相关的信息：

```python
class Error(Exception):
    """Base class for exceptions in this module."""
    pass

class InputError(Error):
    """Exception raised for errors in the input.

    Attributes:
        expression -- input expression in which the error occurred
        message -- explanation of the error
    """

    def __init__(self, expression, message):
        self.expression = expression
        self.message = message

class TransitionError(Error):
    """Raised when an operation attempts a state transition that's not
    allowed.

    Attributes:
        previous -- state at beginning of transition
        next -- attempted new state
        message -- explanation of why the specific transition is not allowed
    """

    def __init__(self, previous, next, message):
        self.previous = previous
        self.next = next
        self.message = message
```

## 引用资料

- [Errors and Exceptions] : https://docs.python.org/3.5/tutorial/errors.html
- [Exception hierarchy] : https://docs.python.org/3.5/library/exceptions.html#bltin-exceptions
