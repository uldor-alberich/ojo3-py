import typing
import collections.abc
import enum

class Tree:
    def __init__(self, node: typing.MutableSequence[typing.Self | str] | None) -> None:
        self.children = node
    
    def visit(self, idx: int) -> str | typing.Self | None:
        if self.children:
            if 0 <= idx < len(self.children):
                return self.children[idx]

    def __str__(self) -> str:
        if self.children is not None:
            return str(self.children)
        return ""

    __repr__ = __str__

class ExpectedKind(enum.Enum):
    Token = enum.auto()
    Rule = enum.auto()
    Regex = enum.auto()

class ParseError(Exception):
    def __init__(self, locate: int, expected: typing.MutableSequence[str], kind: ExpectedKind):
        match kind:
            case ExpectedKind.Token:
                super().__init__(f"Expected token: {expected}")
            case ExpectedKind.Rule:
                super().__init__(f"Expected rule: {expected}")
            case ExpectedKind.Regex:
                super().__init__(f"Expected regex token: {expected}")
        self.locate = locate
        self.expected = expected
        self.kind = kind