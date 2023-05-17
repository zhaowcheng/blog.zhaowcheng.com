---
title: Python 杂项 - deepget 和 deepset
date: 2023-05-17 23:16:00 +0800
categories: [Python 杂项]
tags: [python]
---

实现类似于 `deepcopy` 的两个函数 `deepget` 和 `deepset`，代码如下：

```python
from functools import reduce


def parse_deepkey(deepkey: str, sep: str = '/') -> list:
    """
    深度路径分割

    examples:
        >>> parse_deepkey('a/b1')
        ['a', 'b1']
        >>> parse_deepkey('a/b2[0]')
        ['a', 'b2', 0]
        >>> parse_deepkey('a/b2[0]/c2')
        ['a', 'b2', 0, 'c2']

    :param deepkey: 深度路径
    :param sep: 分隔符
    :return: 列表格式的深度路径
    """
    keys = []
    for k in re.split(r'%s|\[' % sep, deepkey):
        if k.endswith(']') and k[:-1].isdigit():
            keys.append(int(k[:-1]))
        else:
            keys.append(k)
    return keys


def deepget(obj: object, deepkey: str, sep: str = '/') -> any:
    """
    深度获取对象中的值

    examples:
        >>> d = {
        ...     'a': {
        ...         'b1': 'c',
        ...         'b2': [1, 2, 3]
        ...      }
        ... }
        >>> deepget(d, 'a/b1')
        'c'
        >>> deepget(d, 'a/b2[0]')
        1

    :param obj: 对象
    :param deepkey: 深度路径
    :param sep: 分隔符
    :return: 获取到的值
    """
    keys = parse_deepkey(deepkey, sep)
    return reduce(operator.getitem, keys, obj)


def deepset(obj: object, deepkey: str, value: any, sep: str = '/') -> None:
    """
    深度设置对象中的值

    examples:
        >>> d = {
        ...     'a': {
        ...         'b1': 'c',
        ...         'b2': [1, 2, 3]
        ...      }
        ... }
        >>> deepset(d, 'a/b1', 'd')
        >>> d
        {'a': {'b1': 'd', 'b2': [1, 2, 3]}}
        >>> deepset(d, 'a/b2[0]', '-1')
        >>> d
        {'a': {'b1': 'd', 'b2': ['-1', 2, 3]}}

    :param obj: 对象
    :param deepkey: 深度路径
    :param value: 待设置的值
    :param sep: 分隔符
    """
    keys = parse_deepkey(deepkey, sep)
    reduce(operator.getitem, keys[:-1], obj)[keys[-1]] = value

```
