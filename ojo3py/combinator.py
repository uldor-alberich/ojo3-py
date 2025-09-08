import abc
import typing
import dataclasses
import re

from .common import Tree, ParseError, ExpectedKind

Result: typing.TypeAlias = tuple[Tree | None, int]

class Combinator(abc.ABC):
    @abc.abstractmethod
    def parse(self, input: str, locate: int, skip: typing.Self | None) -> Result:
        pass

def skipper(input: str, locate: int, skip: Combinator | None) -> int:
    if not skip:
        return locate
    try:
        _, _locate = skip.parse(input, locate, None)
    except ParseError:
        return locate
    return _locate

@dataclasses.dataclass
class EOI(Combinator):
    parser: Combinator

    def parse(self, input: str, locate: int, skip: Combinator | None) -> Result:
        tree, _locate = self.parser.parse(input, locate, skip)
        _locate = skipper(input, _locate, skip)
        if _locate == len(input):
            return (tree, _locate)
        raise ParseError(_locate, ["eoi"], ExpectedKind.Rule)

@dataclasses.dataclass
class Rule(Combinator):
    parser: Combinator
    name: str

    def parse(self, input: str, locate: int, skip: Combinator | None) -> Result:
        try:
            tree, _locate = self.parser.parse(input, locate, skip)
        except ParseError:
            raise ParseError(locate, [self.name], ExpectedKind.Rule)
        return (tree, skipper(input, _locate, skip))

@dataclasses.dataclass
class Lit(Combinator):
    keyword: str

    def parse(self, input: str, locate: int, skip: Combinator | None) -> Result:
        if not input[locate:].startswith(self.keyword):
            raise ParseError(locate, [self.keyword], ExpectedKind.Token)
        _locate = locate+len(self.keyword)
        return (Tree([self.keyword]), skipper(input, _locate, skip))

@dataclasses.dataclass
class Regex(Combinator):
    regex: re.Pattern

    def parse(self, input: str, locate: int, skip: Combinator | None) -> Result:
        m = self.regex.match(input[locate:])
        if not m:
            raise ParseError(locate, [self.regex], ExpectedKind.Regex)
        return (Tree([m.group()]), skipper(input, locate + m.end(), skip))

@dataclasses.dataclass
class Then(Combinator):
    before: Combinator
    after: Combinator

    def parse(self, input: str, locate: int, skip: Combinator | None) -> Result:
        tree_b, _locate = self.before.parse(input, locate, skip)
        tree_a, _locate = self.after.parse(input, skipper(input, _locate, skip), skip)
        if tree_b and tree_b.children is not None:
            if tree_a and tree_a.children is not None:
                tree_b.children.extend(tree_a.children)
            return (tree_b, skipper(input, _locate, skip))
        return (tree_a, skipper(input, _locate, skip))

@dataclasses.dataclass
class Alt(Combinator):
    parser_a: Combinator
    parser_b: Combinator

    def parse(self, input: str, locate: int, skip: Combinator | None) -> Result:
        try:
            tree_a, _locate = self.parser_a.parse(input, locate, skip)
        except ParseError as err_a:
            try:
                tree_b, __locate = self.parser_b.parse(input, locate, skip)
            except ParseError as err_b:
                raise ParseError(__locate, [err_a.expected, err_b.expected], ExpectedKind.Rule)
            return (tree_b, skipper(input, __locate, skip))
        return (tree_a, skipper(input, _locate, skip))

@dataclasses.dataclass
class Opt(Combinator):
    option: Combinator

    def parse(self, input: str, locate: int, skip: Combinator | None) -> Result:
        try:
            tree, _locate = self.option.parse(input, locate, skip)
        except ParseError:
            return (Tree(None), locate)
        return (tree, _locate)

@dataclasses.dataclass
class Repeated(Combinator):
    parser: Combinator

    def parse(self, input: str, locate: int, skip: Combinator | None) -> Result:
        _locate = locate
        trees = list()
        while True:
            try:
                tree, _locate = self.parser.parse(input, _locate, skip)
            except ParseError:
                return (Tree(trees), _locate)
            if tree:
                trees.append(tree)

@dataclasses.dataclass
class Map(Combinator):
    parser: Combinator
    action: typing.Callable[[Tree], Tree]

    def parse(self, input: str, locate: int, skip: Combinator | None) -> Result:
        tree, _locate = self.parser.parse(input, locate, skip)
        if tree:
            tree = self.action(tree)
        return (tree, skipper(input, _locate, skip))
