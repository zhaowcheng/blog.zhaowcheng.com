---
title: Python 入门 - 5 - 列表与元组
date: 2020-07-15 15:16:00 +0800
categories: [Python 入门]
tags: [python]
---

## 序列（Sequence）

在前面已经介绍过的 `字符串(str)`，以及接下来要学习的 `列表(list)` 和 `元组(tuple)` 都属于 `序列(Sequence)` 类型。  
序列又分为 `可变序列(mutable)` 和 `不可变序列(immutable)`，可变指的是可修改序列的元素，列表属于可变序列，字符串和元组都属于不可变序列。

```python
## 列表使用中括号表示
>>> nums = [1, 2, 3]
>>> type(nums)
<class 'list'>
>>> nums[1] = 0  # 列表是可变序列
>>> nums
[1, 0, 3]

## 元组使用圆括号表示
>>> seqs = (4, 5, 6)
>>> type(seqs)
<class 'tuple'>
>>> seqs[1] = 0  # 元组是不可变序列
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
TypeError: 'tuple' object does not support item assignment
>>> seqs
(4, 5, 6)
```

### 序列操作

序列类型支持的一些通用操作（即可变和不可变序列均支持）如下表：

| Operation | Result |
| --------- | ------ |
| x in s | 如果 s 中的某项等于 x 则结果为 True，否则为 False |
| x not in s | 如果 s 中的某项等于 x 则结果为 False，否则为 True |
| s + t | s 与 t 相拼接 |
| s * n 或 n * s | 相当于 s 与自身进行 n 次拼接 |
| s[i] | s 的第 i 项，起始为 0 |
| s[i:j] | s 从 i 到 j 的切片 |
| s[i:j:k] | s 从 i 到 j 步长为 k 的切片 |
| len(s) | s 的长度 |
| min(s) | s 的最小项 |
| max(s) | s 的最大项 |
| s.index(x[, i[, j]]) | x 在 s 中首次出现项的索引号（索引号在 i 或其后且在 j 之前）|
| s.count(x) | x 在 s 中出现的总次数 |

下面对以上操作进行示例演示：

- x in s

    ```python
    >>> 1 in [1, 2, 3]
    True
    >>> 4 in [1, 2, 3]
    False
    ```

- x not in s
    
    ```python
    >>> 4 not in (1, 2, 3)
    True
    >>> 'a' not in 'abc'
    False
    ```

- s + t

    ```python
    >>> [1, 2] + [3, 4]
    [1, 2, 3, 4]
    >>> (5, 6) + (7, 8)
    (5, 6, 7, 8)
    ```

- s * n 或 n * s

    ```python
    >>> [1, 2] * 2
    [1, 2, 1, 2]
    >>> 3 * 'w'
    'www'
    ```

- s[i]

    ```python
    >>> [1, 2, 3][0]
    1
    >>> 'abc'[-1]
    'c'
    ```

- s[i:j]

    ```python
    >>> [1, 2, 3][0:2]
    [1, 2]
    >>> [1, 2, 3][:2]  # i 可以省略，默认值为 0
    [1, 2]
    >>> [1, 2, 3][1:]  # j 也可以省略，默认值为 len(s)
    [2, 3]
    >>> [1, 2, 3][:]  # i 和 j 同时省略则相当于对 s 进行了一个拷贝
    [1, 2, 3]
    >>> [1, 2, 3][2:1]  # 如果 j <= i，则返回一个空列表
    []
    >>> [1, 2, 3][1:-1]  # i 和 j 也可以是负数，如果是负数则会被转换为 len(s) + i/j
    [2]
    >>> [1, 2, 3][1:2]  # [1:-1] 就相当于 [1:len(s)+(-1)] = [1:3-1] = [1:2]
    [2]
    >>> [1, 2, 3][1:5]  # 如果 i 或 j 大于 len(s)，则被转换为 len(s)
    [2, 3]
    ```

- s[i:j:k]

    ```python
    >>> [1, 2, 3][0:3:2]  # 设定步长 k 为 2，默认为 1
    [1, 3]
    >>> [1, 2, 3][2:0:-1]  # 相当于取 2, 2-1, 2+n*(-1), ...
    [3, 2]

    # k 为负数时 i 或 j 的默认值会倒转
    # k 为正数时，i 和 j 的默认值分别为 0, len(s)
    # k 为负数时，i 和 j 的默认值分别为 len(s)-1, 0，且包含第 0 个元素
    >>> [1, 2, 3][::-1]  
    [3, 2, 1]

    # k 不能为 0
    >>> [1, 2, 3][::0]
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
    ValueError: slice step cannot be zero
    ```

- len(s)

    ```python
    >>> len([1, 2, 3])
    3
    >>> len('abc')
    3
    ```

- min(s)

    ```python
    >>> min([1, 2, 3])
    1
    >>> min('abc')
    'a'
    >>> min([1, 2, 'c'])  # 序列中的元素必须时相同类型的
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
    TypeError: unorderable types: str() < int()
    ```

- max(s)

    ```python
    >>> max([1, 2, 3])
    3
    >>> max('abc')
    'c'
    >>> max((1, 2, 'c'))  # 序列中的元素必须时相同类型的
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
    TypeError: unorderable types: str() > int()
    ```

- s.index(x[, i[, j]])

    ```python
    >>> [1, 2, 3].index(1)
    0
    >>> [1, 2, 3].index(4)  # 未查找到元素报 ValueError
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
    ValueError: 4 is not in list
    ```

- s.count(x)

    ```python
    >>> [1, 2, 1].count(1)
    2
    >>> [1, 2, 1].count(3)
    0
    ```

## 列表（list）

列表属于可变序列（mutable Sequence），列表定义除了用 `中括号([])` 外，还可以使用内置函数 `list()` 把其他序列类型转换为列表：

```python
>>> list('abc')  # 把字符串转换为列表
['a', 'b', 'c']
>>> list((1, 2, 3))  # 把元组转换为列表
[1, 2, 3]
```

### 列表操作

列表除了支持序列类型的通用操作外，还支持以下这些 `可变序列独有的操作`：

| Operation | Result |
| --------- | ------ |
| s[i] = x | 将 s 的第 i 项替换为 x |
| s[i:j] = t | 将 s 从 i 到 j 的切片替换为可迭代对象 t 的内容 |
| del s[i:j] | 等同于 s[i:j] = [] |
| s[i:j:k] = t | 将 s[i:j:k] 的元素替换为 t 的元素 |
| del s[i:j:k] | 从列表中移除 s[i:j:k] 的元素 |
| s.append(x) | 将 x 添加到序列的末尾 (等同于 s[len(s):len(s)] = [x]) |
| s.clear() | 从 s 中移除所有项 (等同于 del s[:]) |
| s.copy() | 创建 s 的浅拷贝 (等同于 s[:]) |
| s.extend(t) 或 s += t | 用 t 的内容扩展 s (基本上等同于 s[len(s):len(s)] = t) |
| s *= n | 使用 s 的内容重复 n 次来对其进行更新 |
| s.insert(i, x) | 在由 i 给出的索引位置将 x 插入 s (等同于 s[i:i] = [x]) |
| s.pop([i]) | 提取在 i 位置上的项，并将其从 s 中移除 |
| s.remove(x) | 删除 s 中第一个等于 x 的项目。 |
| s.reverse() | 就地将列表中的元素逆序。 |

下面对以上操作进行示例演示：

- s[i] = x

    ```python
    >>> nums = [1, 2, 3]
    >>> nums[1] = 0
    >>> nums
    [1, 0, 3]
    ```

- s[i:j] = t

    ```python
    >>> nums = [1, 2, 3]
    >>> nums[1:3] = [0, 0]  # 把第 1 到 3-1 范围的元素替换为 [0, 0]
    >>> nums
    [1, 0, 0]
    >>> nums[1:3] = []  # 把第 1 到 3-1 范围的元素删除
    >>> nums
    [1]
    >>> nums[:] = []  # 清空整个列表
    >>> nums
    []
    ```

- del s[i:j]

    ```python
    >>> nums = [1, 2, 3]
    >>> del nums[1:3]
    >>> nums
    [1]
    ```

- s[i:j:k] = t

    ```python
    >>> nums = [1, 2, 3]
    >>> nums[0:3:2] = [5, 6]  # 把第 0, 0+2 两个元素分别替换为 [5, 6] 中的元素
    >>> nums
    [5, 2, 6]
    >>> nums[0:3:2] = [5]  # t 的元素个数必须和 [i:j:k] 切割出的元素个数相等
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
    ValueError: attempt to assign sequence of size 1 to extended slice of size 2
    ```

- del s[i:j:k]

    ```python
    >>> nums = [1, 2, 3]
    >>> del nums[0:3:2]
    >>> nums
    [2]
    ```

- s.append(x)

    ```python
    >>> nums = [1, 2, 3]
    >>> nums.append(4)
    >>> nums
    [1, 2, 3, 4]
    ```

- s.clear()

    ```python
    >>> nums = [1, 2, 3]
    >>> nums.clear()
    >>> nums
    []
    ```

- s.copy()

    ```python
    >>> nums = [1, 2, 3]
    >>> nums_copy = nums.copy()
    >>> nums_copy
    [1, 2, 3]
    ```

- s.extend(t) 或 s += t

    ```python
    >>> nums = [1, 2, 3]
    >>> nums.extend([4, 5])
    >>> nums
    [1, 2, 3, 4, 5]
    >>> nums += [6, 7]
    >>> nums
    [1, 2, 3, 4, 5, 6, 7]
    ```

- s *= n

    ```python
    >>> nums = [1, 2, 3]
    >>> nums *= 2
    >>> nums
    [1, 2, 3, 1, 2, 3]
    >>> nums *= -1  # 如果 n 小于等于 0，则 s 被清空
    >>> nums
    []
    ```

- s.insert(i, x)

    ```python
    >>> nums = [1, 2, 3]
    >>> nums.insert(1, 4)
    >>> nums
    [1, 4, 2, 3]
    >>> nums[1:1] = [5]  # 等同于 nums.insert(1, 5)
    >>> nums
    [1, 5, 4, 2, 3]
    ```

- s.pop([i])

    ```python
    >>> nums = [1, 2, 3]
    >>> nums.pop()  # 参数 i 默认为 -1
    3
    >>> nums
    [1, 2]
    >>> nums.pop(0)  # 也可以 pop 指定位置的元素
    1
    >>> nums
    [2]
    ```

- s.remove(x)

    ```python
    >>> chars = ['a', 'b', 'c']
    >>> chars.remove('b')
    >>> chars
    ['a', 'c']
    >>> chars.remove('f')  # 如果 s 中不存在值为 x 的元素，则报 ValueError
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
    ValueError: list.remove(x): x not in list
    ```

- s.reverse()

    ```python
    >>> nums = [1, 2, 3]
    >>> nums.reverse()
    >>> nums
    [3, 2, 1]
    ```

### 列表排序

列表除了支持 `序列通用操作` 和 `可变序列操作` 外，列表还实现了一个单独的方法 `sort` ：

- list.sort(key=None, reverse=False)

    sort 是一个就地排序方法，默认升序排序，如果 _reverse_ 参数为 `True`，则是进行降序排序。  
    key 可以接受一个函数，对待排序的对象进行预处理后再进行排序。

    ```python
    >>> nums = [2, 3, 1]
    >>> nums.sort()
    >>> nums
    [1, 2, 3]
    >>> nums.sort(reverse=True)  # 降序排序
    >>> nums
    [3, 2, 1]

    >>> ids = ['lily-02', 'tom-01', 'jack-03']
    >>> ids.sort()  # 默认按字母序进行升序排序：j < l < t
    >>> ids
    ['jack-03', 'lily-02', 'tom-01']
    # 只取 - 后两位数字进行排序比较：01 < 02 < 03
    >>> ids.sort(key=lambda s: s.split('-')[-1])
    >>> ids
    ['tom-01', 'lily-02', 'jack-03']
    ```

### 列表推导式

列表推导式提供了一种简洁的方式来创建列表，比如需要创建一个 1~10 的平方数的列表，只需要像这样一行代码即可完成：

```python
>>> [x**2 for x in range(1, 11)]
[1, 4, 9, 16, 25, 36, 49, 64, 81, 100]
```

列表推导式也同时支持在 for 后面添加 if 语句：

```python
>>> [x for x in range(1, 11) if x%2 == 0]  # 1~10 的偶数
[2, 4, 6, 8, 10]
```

列表推导式也支持嵌套：

```python
>>> [(x, y) for x in [1, 2] for y in [3, 4]]
[(1, 3), (1, 4), (2, 3), (2, 4)]

## 上面的推导式与以下嵌套循环作用相同
>>> combs = []
>>> for x in [1, 2]:
...     for y in [3, 4]:
...         combs.append((x, y))
...
>>> combs
[(1, 3), (1, 4), (2, 3), (2, 4)]
```

### 浅拷贝与深拷贝

列表支持嵌套列表或嵌套其他可变对象，对于列表自带的 copy 方法和切片式拷贝，以及 *(repeation)，都只是一个 `浅拷贝`，下面举例对浅拷贝进行说明：

```python
>>> nested_nums = [1, [2, 3], 4]
>>> copy_nested_nums = nested_nums.copy()  # 浅拷贝，等同于 nested_nums[:]

## 修改原始列表中非嵌套元素，拷贝列表不受影响
>>> nested_nums[0] = 9
>>> nested_nums
[9, [2, 3], 4]
>>> copy_nested_nums
[1, [2, 3], 4]

## 修改原始列表中嵌套列表的元素，拷贝列表受影响
>>> nested_nums[1][0] = 9
>>> nested_nums
[9, [9, 3], 4]
>>> copy_nested_nums
[1, [9, 3], 4]
```

如果想要避免上面的浅拷贝的情况，可以使用 copy.deepcopy 函数进行深拷贝：

```python
>>> nested_nums = [1, [2, 3], 4]
>>> import copy
>>> copy_nested_nums = copy.deepcopy(nested_nums)
>>> nested_nums[1][0] = 9
>>> nested_nums
[1, [9, 3], 4]
>>> copy_nested_nums  # 深拷贝的列表不受影响
[1, [2, 3], 4]
```

## range

range 是一个 `内置类型`，可以用来创建一个 `不可变序列(immutable)`，定义如下：

```python
class range(stop)
class range(start, stop[, step])

# 在 start 到 stop 范围内（不包含 stop），以步长为 step，产生一个序列。
```

_start_, _stop_, _step_ 均为 int 类型，如果只传入一个参数，这个参数会被当作 _stop_ ：

```python
>>> [i for i in range(3)]
[0, 1, 2]
```

也可以传入 2 个参数，则分别会被当作 _start_ 和 _stop_ ：

```python
>>> [i for i in range(1, 3)]
[1, 2]
```

还可以设定步长（step），步长默认值是 1 ：

```python
>>> [i for i in range(1, 10, 2)]
[1, 3, 5, 7, 9]
```

如果步长 _step_ 为负数，那么应该满足 _start_ >= _stop_ ：

```python
>>> [i for i in range(3, 0, -1)]
[3, 2, 1]
```

和 list 相比，range 类型更节约内存，因为 list 占用内存大小是根据元素的多少而变化，而 range 生成的实例只是记录了一下计算方法，不管范围多大，都占用固定大小的内存，在每一次 for 循环时才实时计算出当前的元素内容：

```python
>>> nums = [1, 2, 3]
>>> import sys
>>> sys.getsizeof(nums)
88
>>> r = range(1, 4)
>>> sys.getsizeof(r)
48
>>> nums = [1, 2, 3, 4] 
>>> sys.getsizeof(nums)  # 增加一个元素后，大小也增加了 8
96
>>> r = range(1, 5)
>>> r
range(1, 5)
>>> sys.getsizeof(r)  # 扩大范围后，占用大小仍然不变
48
```

## 元组（tuple）

元组和列表类似，都是序列，不同的是元组是 `不可变序列(immutable Sequence)`，元组的定义使用 `圆括号`，也可以使用内置关键字 `tuple`，将其他序列转换为元组：

```python
>>> t = (1, 2, 3)
>>> t
(1, 2, 3)
>>> t = 1, 2, 3  # 如果元素个数超过 1 个，也可以不使用圆括号
>>> t
(1, 2, 3)
## 只有 1 个元素的元组需要用圆括号括起来，并且在末尾添加一个逗号(,)
## 这样做是为了和数学符号的圆括号进行区分
>>> t = (1,)  
>>> t
(1,)
>>> tuple([1, 2, 3])  # 把列表转换为元组
(1, 2, 3)
```

元组作为不可变序列，一旦定义后，其中的元素不能被修改：

```python
>>> t = (1, 2, 3)
>>> t[0] = 5
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
TypeError: 'tuple' object does not support item assignment
```

但是元组里的可变类型的内容的是可以被修改的：

```python
>>> t = (1, [2, 3], 4)
>>> t[1][0] = 3
>>> t
(1, [3, 3], 4)
```

## 参考资料

- [More on Lists] : https://docs.python.org/3.5/tutorial/datastructures.html#more-on-lists
- [Tuples and Sequences] : https://docs.python.org/3.5/tutorial/datastructures.html#tuples-and-sequences
- [Sequence Types — list, tuple, range] : https://docs.python.org/3.5/library/stdtypes.html#sequence-types-list-tuple-range