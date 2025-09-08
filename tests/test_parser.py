import sys
import os

sys.path.insert(0, os.path.abspath("."))

from ojo3py import lit, regex

try:
    tree = lit("Hello,").then(lit("World!").opt()).repeated().eoi().parse("Hello, Hello, Hello, World!", regex("\\s*"))
except Exception as e:
    print(e)
else:
    print(tree)