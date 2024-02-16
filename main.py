from typing import Any, Optional
from dataclasses import dataclass

from keyword import iskeyword

from utils import overload, OverloadMeta


class MessageRaw(dict, metaclass=OverloadMeta):
    @overload
    def __init__(self, obj: dict) -> None:
        super().__init__()
        [self.__setitem__(key, value) for key, value in obj.items()]

    @overload
    def __init__(self, obj: list[tuple[Any, Any], tuple[Any, Any]]) -> None:
        super().__init__()
        [self.__setitem__(item[0], item[1]) for item in obj]

    @overload
    def __init__(self, **kwargs) -> None:
        super().__init__()
        [self.__setitem__(key, value) for key, value in kwargs.items()]

    def __setitem__(self, key: str, value: Any) -> None:
        super().__setitem__(f'{key}_' if iskeyword(key) else key, value)

    def __getitem__(self, item: str) -> Any:
        return super().__getitem__(f'{item}_') if iskeyword(item) else super().__getitem__(item)

    def get(self, item: str, default: Optional[Any] = None) -> Any:
        return it if (it := self.__getitem__(item)) else default

    def __repr__(self) -> str:
        return f'MessageRaw({", ".join([f"{key}={value}" for key, value in self.items()])})'


@dataclass()
class User:
    a: Any


@dataclass()
class Message:
    message_id: int
    from_: User

    def __repr__(self) -> str:
        return f'Message({", ".join([f"{key}={value}" for key, value in list(filter(lambda item: item[1] is not None, self.__dict__.items()))])})'

    def __post_init__(self):
        self.from_ = User(self.from_)


print(Message(**MessageRaw([('message_id', 1), ('from', 'iguhregh')])))

print(Message(**MessageRaw(message_id=2, from_='fhufh')))

print(Message(**MessageRaw({'message_id': 2, 'from': 'fgregfde'})))
