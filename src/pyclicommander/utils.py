def intersperse(lst, item):
    """ Insert item inbetween each elemt in the list.

    >>> intersperse(["a", "b", "c"], '-')
    ["a", "-", "b", "-", "c"]
    """
    result = [item] * (len(lst) * 2 - 1)
    result[0::2] = lst
    return result


def deep_get(d, keys, default=None):
    """ Get values deep from a nested dict.

    >>> deep_get({'apa': {'bepa': 2}}, ['apa', 'bepa'])
    2
    >>> deep_get({'apa': {'bepa': 2}}, ['apa'])
    {'bepa': 2}
    """
    if d is None:
        return default
    if not keys:
        return d
    return deep_get(d.get(keys[0]), keys[1:], d.get(keys[0]))


def deep_set(d, keys, value):
    """ Set value deep into a nested dict.

    >>> deep_set({}, ["apa", "bepa", "cepa"], 3)
    {'apa': {'bepa': {'cepa': 3}}}
    >>> deep_set({'apa': {'bepa': 1}}, ['apa', 'cepa'], 2)
    {'apa': {'bepa': 1, 'cepa': 2}}
    """
    if len(keys) == 1:
        if keys[0] in d:
            d[keys[0]] = {**d[keys[0]], **value}
        else:
            d[keys[0]] = value
        return d

    if not keys:
        return d

    # dd = d.setdefault(keys[0], {})
    dd = d.get(keys[0], {})
    return dict_set(d, keys[0], deep_set(dd, keys[1:], value))


def dict_set(d, s, v):
    """ Create new dict and set value and return the updated new dict.

    >>> dict_set({'apa': 1}, 'bepa', 2)
    {'apa': 1, 'bepa': 2}
    """
    dd = dict(d)
    dd[s] = v
    return dd


def get_idx(lst, idx, default_value=None):
    """ Get element at idx from list otherwise return None or default_value.

    >>> get_idx([1, 2, 3], 0)
    1
    >>> get_idx([1, 2, 3], 5)
    None
    >>> get_idx([1, 2, 3], 5, "apa")
    "apa"
    """
    return lst[idx] if idx < len(lst) else default_value
