---
title: Python 入门-11-类
date: 2022-02-24 11:05:00 +0800
categories: [Python 入门]
tags: []
---

Python 类源自于 `C++` 和 `Modula-3` 这两种语言的类机制的结合。  
Python 中一切皆 `对象（Object）`，类里边又引入了 3 种对象：`类对象（Class）`、`实例对象（Instance）` 和 `方法对象（Method）`

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

### 语法格式

类定义语法格式如下：

```python
class ClassName:
    <statement-1>
    .
    .
    .
    <statement-N>
```

通常类定义内的语句都是 `函数定义`，但也可以是其他语句（如属性定义等）。  
在进入类定义时，将创建一个 `命名空间`，用于保存类中的名称。  
当（从结尾处）正常离开类定义时，将创建一个 `类对象`。

类对象支持两种操作：`属性引用` 和 `实例化`。

```python
class MyClass:
    """A simple example class"""
    i = 12345

    def f(self):
        return 'hello world'
```

例如以上示例中定义的 MyClass 类，那么 MyClass.i 和 MyClass.f 就是有效的属性引用，将分别返回一个整数和一个函数对象。  
类的 `实例化` 使用函数表示法：

```python
# 创建类的新 实例 并将此对象分配给局部变量 x
x = MyClass()
```

### 初始化方法

类中可以定义一个 `__init__()` 方法，用于自定义类的初始化操作：

```python
class MyClass:
    def __init__(self):
        self.data = []
```

`__init__()` 方法定义时还可以有额外的参数：

```python
>>> class Complex:
...     def __init__(self, realpart, imagpart):
...         self.r = realpart
...         self.i = imagpart
...
>>> x = Complex(3.0, -4.5)
>>> x.r, x.i
(3.0, -4.5)
```

### self 参数

类中定义的方法的第一个参数固定被当作类初始化后的 `实例本身`，通常写作 `self`，可在方法中使用该变量引用其他 `实例属性`：

```python
class Complex:
    def __init__(self, realpart, imagpart):
        self.r = realpart
        self.i = imagpart

    def get_realpart(self):
        return self.r

    def get_imagpart(self):
        return self.i

    # 也可以不定义参数，只是这样就不能在该方法中访问实例属性 r 和 i 了
    def get_nothing():
        return None
```

### 访问限制

如果类中定义的 `属性（包括变量和方法）` 是以 `双下划线（__）` 开头，并且以 `最多一个下划线结尾`，那么即表示该属性是 `私有的（Private）`，不能从外部访问：

```python
>>> class Student(object):
...     def __init__(self, name, score):
...         self.__name = name
...         self.__score = score
... 
>>> bart = Student('Bart Simpson', 59)
>>> bart.__name
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
AttributeError: 'Student' object has no attribute '__name'
```

实际上 Python 并没有机制严格的限制对私有属性的访问，只是简单的对私有属性进行了 `改名（加上了下划线开头的类名前缀）` 而已：

```python
>>> class Student(object):
...     def __init__(self, name, score):
...         self.__name = name
...         self.__score = score
... 
>>> bart = Student('Bart Simpson', 59)
>>  # 虽然通过下面这种方式可以访问私有属性，但强烈不建议这样做
>>> bart._Student__name
'Bart Simpson' 
```

`双下划线开头` 并且 `双下划线结尾` 的名称是 Python 类的一些特殊属性，比如 `__name__` 表示类名，`__doc__` 表示类注释，还有用于初始化实例的 `__init__()` 方法等，所以建议也不要自定义这样的属性：

```python
>>> class MyClass(object):
...     """my class"""
...     pass
...
>>> MyClass.__name__
'MyClass'
>>> MyClass.__doc__
'my class'
>>>
```

`单下划线` 开头的属性也可以直接访问，但是约定俗成的规范是这样的属性表示 `保护属性`，即能在子类中访问，但不建议从外部访问。

`数据属性` 会覆盖掉同名的 `方法属性`，为了避免这种情况发生，建议数据属性使用名词，方法属性使用动词。

## 类与实例

类是抽象模板，实例是根据类创建出来的具体的对象，每个实例都拥有相同的方法，但各自的数据可能不同。

```python
>>> class Student(object):
...     def __init__(self, name):
...         self.name = name
...
>>> student1 = Student('tom')
>>> student2 = Student('jack')
>>> student1.name
'tom'
>>> student2.name
'jack'
>>>
```

在类中直接定义的属性为 `类属性`，而绑定到实例上的属性是 `实例属性`，类属性是所有实例 `共有` 的，实例属性是每个实例 `独有` 的。

```python
>>> class Student(object):
...     # 类属性
...     clsname = 'Student'
...     def __init__(self, instname):
...         # 实例属性
...         self.instname = instname
...
>>> student1 = Student('tom')
>>> student2 = Student('jack')
>>> student1.clsname
'Student'
>>> student1.instname
'tom'
>>> student2.clsname
'Student'
>>> student2.instname
'jack'
>>>
```

## 类继承

### 单继承

单继承的语法格式如下：

```python
class DerivedClassName(BaseClassName):
    <statement-1>
    .
    .
    .
    <statement-N>
```

其中 `BaseClassName` 叫做 `DerivedClassName` 的 `基类`，也可叫做 `父类` 或 `超类`，DerivedClassName 则叫做 BaseClassName 的 `子类`。

通过继承的方式，子类可以拥有父类的所有属性（包括数据属性和方法属性），当引用类的属性时，搜索顺序是先搜索子类，再搜索父类，然后是父类的父类，依次往上，所以子类如果定义了和父类同名的属性，就相当于覆盖了父类的同名属性。

### 多重继承

多种继承的语法格式如下：

```python
class DerivedClassName(Base1, Base2, Base3):
    <statement-1>
    .
    .
    .
    <statement-N>
```

子类 `DerivedClassName` 同时从父类 `Base1`、`Base2` 和 `Base3` 继承，这种情况下搜索一个属性的顺序是 `深度优先、从左至右、同一个类只搜索一次`，比如以上示例中先搜索 `DerivedClassName`，然后搜索 `Base1`，然后搜索 Base1 的父类一直搜索到顶，然后再搜索 `Base2` 依次到顶，依此类推。

关于更详细的搜索顺序见：https://www.python.org/download/releases/2.3/mro/

## 获取对象信息

### type()

使用 `type()` 函数可以判断一个对象的类型：

```python
>>> type(123)
<class 'int'>
>>> type('hello')
<class 'str'>
>>> type(True)
<class 'bool'>
>>> type(int)  # 类的类型都是 type
<class 'type'>
>>> type(str)
<class 'type'>
>>> type(bool)
<class 'type'>
>>>
```

`types` 模块中定义了各种类型，可以方便直观的用于类型判断和比较：

```python
>>> import types
>>> def fn():
...     pass
...
>>> type(fn)==types.FunctionType
True
>>> type(abs)==types.BuiltinFunctionType
True
>>> type(lambda x: x)==types.LambdaType
True
>>> type((x for x in range(10)))==types.GeneratorType
True
```

### isinstance()

`isinstance()` 函数可以判断一个实例是否为某个 `类或其子类` 的实例：

```python
>>> isinstance('a', str)
True
>>> isinstance(123, int)
True
>>> isinstance(b'a', bytes)
True
>>> isinstance([1, 2, 3], (list, tuple))  # 判断是否某些类型中的一种
True
>>> isinstance((1, 2, 3), (list, tuple))
True
>>> isinstance(True, int)  # bool 是 int 的子类
True
```

### issubclass()

`issubclass()` 函数可以判断某个类是否是另一个类的子类：

```python
>>> issubclass(bool, int)  # bool 是 int 的子类
True
>>> issubclass(str, int)
False
```

### dir()

`dir()` 函数可以获取一个对象的所有 `属性` 和 `方法`:

```python
>>> dir('hello')
['__add__', '__class__', '__contains__', '__delattr__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', '__getitem__', '__getnewargs__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__iter__', '__le__', '__len__', '__lt__', '__mod__', '__mul__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__rmod__', '__rmul__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', 'capitalize', 'casefold', 'center', 'count', 'encode', 'endswith', 'expandtabs', 'find', 'format', 'format_map', 'index', 'isalnum', 'isalpha', 'isascii', 'isdecimal', 'isdigit', 'isidentifier', 'islower', 'isnumeric', 'isprintable', 'isspace', 'istitle', 'isupper', 'join', 'ljust', 'lower', 'lstrip', 'maketrans', 'partition', 'replace', 'rfind', 'rindex', 'rjust', 'rpartition', 'rsplit', 'rstrip', 'split', 'splitlines', 'startswith', 'strip', 'swapcase', 'title', 'translate', 'upper', 'zfill']
```

### getattr(), setattr(), hasattr()

使用 getattr(), setattr(), hasattr() 这三个函数可以操作对象的属性：

```python
>>> class MyObject(object):
...     def __init__(self):
...         self.x = 9
...     def power(self):
...         return self.x * self.x
...
>>> obj = MyObject()
>>> hasattr(obj, 'x') # 有属性'x'吗？
True
>>> obj.x
9
>>> hasattr(obj, 'y') # 有属性'y'吗？
False
>>> setattr(obj, 'y', 19) # 设置一个属性'y'
>>> hasattr(obj, 'y') # 有属性'y'吗？
True
>>> getattr(obj, 'y') # 获取属性'y'
19
>>> obj.y # 获取属性'y'
19
```

## 类的一些特殊属性

下面只简单介绍一些特殊属性，完整的特性属性详见：https://docs.python.org/3/reference/datamodel.html#special-method-names

### `__iter__()`

如果一个类想被用于 `for ... in` 循环，类似 list 或 tuple 那样，就必须实现一个 `__iter__()` 方法，该方法返回一个迭代对象，然后，Python 的 for 循环就会不断调用该迭代对象的 `__next__()` 方法拿到循环的下一个值，直到遇到 StopIteration 错误时退出循环。

我们以斐波那契数列为例，写一个 Fib 类，可以作用于 for 循环：

```python
class Fib(object):
    def __init__(self):
        self.a, self.b = 0, 1 # 初始化两个计数器a，b

    def __iter__(self):
        return self # 实例本身就是迭代对象，故返回自己

    def __next__(self):
        self.a, self.b = self.b, self.a + self.b # 计算下一个值
        if self.a > 100000: # 退出循环的条件
            raise StopIteration()
        return self.a # 返回下一个值
```

现在，试试把 Fib 实例作用于 for 循环：

```python
>>> for n in Fib():
...     print(n)
...
1
1
2
3
5
...
46368
75025
```

### `__len__`

如果想要让对象适用于 `len()` 函数，即像 list 或 tuple 那样，可以自定义一个 `__len__()` 方法：

```python
>>> class MyList(object):
...     def __init__(self, datas):
...         self.datas = datas
...     def __len__(self):
...         return len(self.datas)
...
>>> mylist = MyList([1, 2, 3])
>>> len(mylist)
3
```

## 引用资料

- [Classes] : https://docs.python.org/3.5/tutorial/classes.html
- [Special method names] : https://docs.python.org/3/reference/datamodel.html#special-method-names
- [面向对象编程] : https://www.liaoxuefeng.com/wiki/1016959663602400/1017495723838528
- [面向对象高级编程] : https://www.liaoxuefeng.com/wiki/1016959663602400/1017501628721248
