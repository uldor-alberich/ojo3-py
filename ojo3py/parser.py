import typing
import re

from .common import Tree
from .combinator import *

class Parser:
    def __init__(self) -> None:
        self.parser: Combinator = None
    
    def parse(self, src: str, skip: typing.Self) -> Tree | None:
        return self.parser.parse(src, skipper(src, 0, skip.parser), skip.parser)[0]
    
    def eoi(self) -> typing.Self:
        self.parser = EOI(self.parser)
        return self

    def label(self, name: str) -> typing.Self:
        self.parser = Rule(self.parser, name)
        return self

    @classmethod
    def lit(cls, keyword: str) -> typing.Self:
        root = cls()
        root.parser = Lit(keyword)
        return root
    
    @classmethod
    def regex(cls, pattern: str) -> typing.Self:
        root = cls()
        root.parser = Regex(re.compile(pattern))
        return root
    
    def then(self, after: typing.Self) -> typing.Self:
        self.parser = Then(self.parser, after.parser)
        return self
    
    def alt(self, parser: typing.Self) -> typing.Self:
        self.parser = Alt(self.parser, parser.parser)
        return self
    
    def opt(self) -> typing.Self:
        self.parser = Opt(self.parser)
        return self

    def repeated(self) -> typing.Self:
        self.parser = Repeated(self.parser)
        return self
    
    def map(self, action: typing.Callable[[Tree], Tree]) -> typing.Self:
        self.parser = Map(self.parser, action)
        return self

lit = Parser.lit
regex = Parser.regex
