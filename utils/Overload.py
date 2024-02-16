from typing import Self, Callable, Any, Iterable

from difflib import Differ
from re import finditer, search, Match


__all__ = [
    'overload',
    'OverloadMeta'
]


class OverloadDict(dict):
    overload_instances = {}

    def __setitem__(self, key, value) -> None:
        if hasattr(value, '__overload__'):
            if overloaded := self.overload_instances.get(key):
                overloaded += value
            else:
                overloaded = Overload()
                overloaded += value
                self.overload_instances[key] = overloaded
            super().__setitem__(key, overloaded)
            return None
        super().__setitem__(key, value)


class Overload:
    def __init__(self) -> None:
        self.func_dict = {}
        self.instance = None
        self.class_ = None

    def __repr__(self) -> str:
        return f'Overloaded({list(self.func_dict.values())})'

    def __get__(self, instance, owner) -> Self:
        self.instance = instance
        self.class_ = owner
        return self

    def __call__(self, *args, **kwargs) -> Any:
        string = str(list(map(annotate, (args if not kwargs else [*args, *kwargs.values()]) if args else kwargs.values())))
        func_name = ''
        for key in self.func_dict.keys():
            if compare(string, key) == string:
                func_name = key
                break
        if isinstance(func := self.func_dict.get(func_name), classmethod):
            return func(self.class_, *args, **kwargs)
        elif isinstance(func, staticmethod):
            return func(*args, **kwargs)
        else:
            return func(self.instance, *args, **kwargs)

    def __iadd__(self, func) -> Self:
        if 'return' in (annotations := func.__annotations__):
            annotations.pop('return')
        if annotations:
            self.func_dict["['" + (search("'(.+?)'", a).groups()[0] if (a := str(list(annotations.values())[0])).startswith('<class') else a) + "']"] = func
        else:
            self.func_dict[''] = func
        return self


class OverloadMeta(type):
    def __new__(mcs, name, bases, attrs):
        return super().__new__(mcs, name, bases, attrs)

    @classmethod
    def __prepare__(mcs, name, bases) -> OverloadDict:
        return OverloadDict()


def overload(func) -> Callable:
    func.__overload__ = True
    return func


def annotate(obj: Any) -> str:
    if type(obj).__name__ in ('list', 'tuple'):
        annotations = []
        [annotations.append(annotate(item)) for item in obj]
        return f"{type(obj).__name__}[{', '.join(annotations)}]"
    else:
        return type(obj).__name__


def sort(element: Match) -> int:
    if hasattr(sort, '__count__'):
        sort.__count__ += 1
        return element.start() - len('typing.Any') * sort.__count__
    else:
        sort.__count__ = 0
        return element.start()


def get_empty_pos(string: str) -> Iterable:
    return map(sort, finditer('typing\.Any', string)) if 'typing.Any' in string else []


def strings_difference(string1: str, string2: str, string='') -> list:
    for i in Differ().compare(string1, string2):
        string = string + i.replace('-', '').strip() if i.startswith('-') else string + ' '
    return string.split()


def compare(string1: str, string2: str) -> str:
    ln = ''
    for cord, elem in zip(get_empty_pos(string2), strings_difference(string1, string := string2.replace('typing.Any', ''))):
        try:
            string = string[:cord + (len(ln) if ln else 0)] + elem + string[cord + (len(ln) if ln else 0):]
        except IndexError:
            break
        ln += elem
    return string
