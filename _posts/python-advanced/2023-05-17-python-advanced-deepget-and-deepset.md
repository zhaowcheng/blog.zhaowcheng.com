---
title: Python 进阶 - deepget 和 deepset
date: 2023-05-17 23:16:00 +0800
categories: [Python 进阶]
tags: [python]
---

实现类似于 `deepcopy` 的 3 个函数 `deepget`, `deepset`, `deeppop`，代码如下：

```python
#!/usr/bin/env python3.10

import re
import operator
import typing as t

from functools import reduce

T = t.TypeVar('T')


def parse_deepkey(deepkey: str, sep: str = '.') -> list:
    """
    深度路径分割

    :param deepkey: 深度路径
    :param sep: 分隔符
    :return: 列表格式的深度路径

    >>> parse_deepkey('a.b1')
    ['a', 'b1']
    >>> parse_deepkey('a.b2[0]')
    ['a', 'b2', 0]
    >>> parse_deepkey('a.b2[0].c2')
    ['a', 'b2', 0, 'c2']
    >>> parse_deepkey('a.b2[x=1].c2')
    ['a', 'b2', {'x': 1}, 'c2']
    >>> parse_deepkey('a.b2[x=1, y="z"].c2')
    ['a', 'b2', {'x': 1, 'y': 'z'}, 'c2']
    """
    keys = []
    for k in re.split(r'%s|\[' % re.escape(sep), deepkey):
        if k.endswith(']'):
            k = k[:-1]
            if k.isdigit():
                keys.append(int(k))
            else:
                try:
                    keys.append(eval(f'dict({k})'))
                except SyntaxError as e:
                    raise SyntaxError(f'Invalid expr `{k}` in deepkey `{deepkey}`: {str(e)}.')
        else:
            keys.append(k)
    return keys


def dump_deepkey(keys: list[str | int | dict], sep: str = '.') -> list:
    """
    深度路径合并

    :param keys: 切割后的深度路径
    :param sep: 分隔符
    :return: 合并后的深度路径

    >>> dump_deepkey(['a', 'b1'])
    'a.b1'
    >>> dump_deepkey(['a', 'b2', 0])
    'a.b2[0]'
    >>> dump_deepkey(['a', 'b2', 0, 'c2'])
    'a.b2[0].c2'
    >>> dump_deepkey(['a', 'b2', {'x': 1}, 'c2'])
    'a.b2[x=1].c2'
    >>> dump_deepkey(['a', 'b2', {'x': 1, 'y': 'z'}, 'c2'])
    'a.b2[x=1, y="z"].c2'
    """
    normkeys = []
    for key in keys:
        if isinstance(key, int):
            normkeys.append(f'[{key}]')
        elif isinstance(key, dict):
            parts = []
            for k, v in key.items():
                if isinstance(v, (int, float)):
                    parts.append(f'{k}={v}')
                else:
                    parts.append(f'{k}="{v}"')
            normkeys.append(f'[{", ".join(parts)}]')
        else:
            normkeys.append(key)
    return sep.join(normkeys).replace('.[', '[')


def deep_getitem(obj: object, key: str) -> t.Any:
    """
    专为 deep* 函数设计的获取对象中的值函数。

    :param obj: 对象
    :param key: 键
    :return: 获取到的值
    """
    if isinstance(key, dict):
        return GetableList(obj).get(musthave=True, **key)
    else:
        return operator.getitem(obj, key)


def deepget(obj: object, deepkey: str, sep: str = '.') -> t.Any:
    """
    深度获取对象中的值

    :param obj: 对象
    :param deepkey: 深度路径
    :param sep: 分隔符
    :return: 获取到的值

    >>> d = {
    ...     'a': {
    ...         'b1': 'c',
    ...         'b2': [1, 2, 3],
    ...         'b3': [{'x': 1, 'y': 'h'}, 
    ...                {'x': 2, 'y': 'i'},
    ...                {'x': 1, 'y': 'j'}]
    ...      }
    ... }
    >>> deepget(d, 'a.b1')
    'c'
    >>> deepget(d, 'a.b2[0]')
    1
    >>> deepget(d, 'a.b3[0].x')
    1
    >>> deepget(d, 'a.b3[x=1]')
    {'x': 1, 'y': 'h'}
    >>> deepget(d, 'a.b3[x=1, y="j"]')
    {'x': 1, 'y': 'j'}
    """
    keys = parse_deepkey(deepkey, sep)
    return reduce(deep_getitem, keys, obj)


def deepset(obj: object, deepkey: str, value: any, sep: str = '.') -> None:
    """
    深度设置对象中的值。
    如果路径不存在则创建（路径中带索引的情况除外，如 a.b[0]）

    :param obj: 对象
    :param deepkey: 深度路径
    :param value: 待设置的值
    :param sep: 分隔符

    >>> from pprint import pprint
    >>> d = {
    ...     'a': {
    ...         'b1': 'c',
    ...         'b2': [1, 2, 3],
    ...         'b3': [{'x': 1, 'y': 'h'}, 
    ...                {'x': 2, 'y': 'i'},
    ...                {'x': 1, 'y': 'j'}]
    ...      }
    ... }
    >>> deepset(d, 'a.b1', 'd')
    >>> pprint(d)
    {'a': {'b1': 'd',
           'b2': [1, 2, 3],
           'b3': [{'x': 1, 'y': 'h'}, {'x': 2, 'y': 'i'}, {'x': 1, 'y': 'j'}]}}
    >>> deepset(d, 'a.b2[0]', '-1')
    >>> pprint(d)
    {'a': {'b1': 'd',
           'b2': ['-1', 2, 3],
           'b3': [{'x': 1, 'y': 'h'}, {'x': 2, 'y': 'i'}, {'x': 1, 'y': 'j'}]}}
    >>> deepset(d, 'i.j', 'x')
    >>> pprint(d)
    {'a': {'b1': 'd',
           'b2': ['-1', 2, 3],
           'b3': [{'x': 1, 'y': 'h'}, {'x': 2, 'y': 'i'}, {'x': 1, 'y': 'j'}]},
     'i': {'j': 'x'}}
    >>> deepset(d, 'a.b2[999]', 4)
    >>> pprint(d)
    {'a': {'b1': 'd',
           'b2': ['-1', 2, 3, 4],
           'b3': [{'x': 1, 'y': 'h'}, {'x': 2, 'y': 'i'}, {'x': 1, 'y': 'j'}]},
     'i': {'j': 'x'}}
    >>> deepset(d, 'a.b4[0].c1[0]', 'x')
    >>> pprint(d)
    {'a': {'b1': 'd',
           'b2': ['-1', 2, 3, 4],
           'b3': [{'x': 1, 'y': 'h'}, {'x': 2, 'y': 'i'}, {'x': 1, 'y': 'j'}],
           'b4': [{'c1': ['x']}]},
     'i': {'j': 'x'}}
    >>> deepset(d, 'a.b3[x=1].y', 'k')
    >>> pprint(d)
    {'a': {'b1': 'd',
           'b2': ['-1', 2, 3, 4],
           'b3': [{'x': 1, 'y': 'k'}, {'x': 2, 'y': 'i'}, {'x': 1, 'y': 'j'}],
           'b4': [{'c1': ['x']}]},
     'i': {'j': 'x'}}
    >>> deepset(d, 'a.b3[x=1, y="j"].y', 'k')
    >>> pprint(d)
    {'a': {'b1': 'd',
           'b2': ['-1', 2, 3, 4],
           'b3': [{'x': 1, 'y': 'k'}, {'x': 2, 'y': 'i'}, {'x': 1, 'y': 'k'}],
           'b4': [{'c1': ['x']}]},
     'i': {'j': 'x'}}
    """
    keys = parse_deepkey(deepkey, sep)
    for i, k in enumerate(keys[:-1]):
        try:
            obj = deep_getitem(obj, k)
        except KeyError:
            obj[k] = [] if isinstance(keys[i+1], int) else {}
            obj = obj[k]
        except IndexError:
            obj.append([] if isinstance(keys[i+1], int) else {})
            obj = obj[-1]
    if isinstance(obj, list) and len(obj) <= keys[-1]:
        obj.append(value)
    else:
        operator.setitem(obj, keys[-1], value)


def deeppop(obj: object, deepkey: str, sep: str = '.') -> t.Any:
    """
    深度删除对象中的值

    :param obj: 对象
    :param deepkey: 深度路径
    :param sep: 分隔符
    :return: deepkey 存在时返回删除的值，否则返回 None。

    >>> d = {
    ...     'a': {
    ...         'b1': 'c',
    ...         'b2': [1, 2, 3],
    ...         'b3': [{'x': 1, 'y': 'h'}, 
    ...                {'x': 2, 'y': 'i'},
    ...                {'x': 1, 'y': 'j'}]
    ...      }
    ... }
    >>> deeppop(d, 'a.b1')
    'c'
    >>> deeppop(d, 'a.b2[0]')
    1
    >>> deeppop(d, 'a.b2[5]') == None
    True
    >>> deeppop(d, 'a.b4') == None
    True
    >>> deeppop(d, 'a.b3[x=1]')
    {'x': 1, 'y': 'h'}
    >>> deeppop(d, 'a.b3[x=1, y="j"].y')
    'j'
    >>> deeppop(d, 'a.b3[x=3]') == None
    True
    """
    keys = parse_deepkey(deepkey, sep)
    if len(keys) == 1:
        return obj.pop(keys[0])
    else:
        v = deepget(obj, dump_deepkey(keys[:-1], sep=sep), sep=sep)
        if v is not None:
            if isinstance(v, list):
                if isinstance(keys[-1], dict):
                    r = GetableList(v).get(musthave=False, **keys[-1])
                    if r:
                        v.remove(r)
                    return r
                else:
                    try:
                        return v.pop(keys[-1])
                    except IndexError:
                        return None
            else:
                return v.pop(keys[-1], None)
            

class GetableList(t.Generic[T], list):
    """
    可自定义获取元素的列表。
    """
    def get(self, musthave=True, **attrs) -> t.Optional[T]:
        """
        获取第一个属性都匹配的元素，否则返回 None 或报错。

        :param musthave: 如果为 True，无匹配的元素时则报错。
        :param attrs: 属性名和属性值。

        >>> class Person:
        ...     def __init__(self, name, age):
        ...         self.name = name
        ...         self.age = age
        ... 
        >>> people = GetableList[Person]([
        ...     Person("Alice", 30),
        ...     Person("Bob", 25),
        ...     Person("Bob", 26),
        ...     Person("Charlie", 35)
        ... ])
        >>> people.get(name='Bob').age
        25
        >>> people.get(name='Tom', musthave=False) == None
        True
        """
        for e in self:
            for k, v in attrs.items():
                if isinstance(e, dict):
                    value = e.get(k)
                else:
                    value = getattr(e, k, None)
                if value != v:
                    break
            else:
                return e
        if musthave:
            raise AttributeError(f'No such element: {attrs}')
        
    def gets(self, **attrs) -> 'GetableList[T]':
        """
        获取所有属性都匹配的元素。

        :param attrs: 属性名和属性值。

        >>> class Person:
        ...     def __init__(self, name, age):
        ...         self.name = name
        ...         self.age = age
        ... 
        >>> people = GetableList[Person]([
        ...     Person("Alice", 30),
        ...     Person("Bob", 25),
        ...     Person("Bob", 26),
        ...     Person("Charlie", 35)
        ... ])
        >>> people.gets(name='Bob')[0].age
        25
        >>> people.gets(name='Tom') == []
        True
        """
        elements = []
        for e in self:
            for k, v in attrs.items():
                if getattr(e, k) != v:
                    break
            else:
                elements.append(e)
        return elements
```
