from enum import Enum, auto

class Status(Enum):
    SUCCEED = auto()
    FAILED = auto()


class Node:
    def __init__(self, status, index, value = None):
        self.status = status
        self.index = index
        self.value = value

class OperatorMixin:
    def __rshift__(self, other):
        return Sequence(self, other)
    def __or__(self, other):
        return OrderedChoise(self, other)
    def __invert__(self):
        return ZeroOrMore(self)
    def __invert__(self):
        return ZeroOrMore(self)
    def __pos__(self):
        return OneOrMore(self)
    def __neg__(self):
        return Optional(self)


class Sequence(OperatorMixin):
    def __init__(self, a, b):
        self.a = a
        self.b = b
    def parse(self, target, i):
        resultA = self.a.parse(target, i)
        if resultA.status is Status.SUCCEED:
            resultB = self.b.parse(target, resultA.index)
            return Node(Status.SUCCEED, resultB.index, [resultA.value, resultB.value])
        return Node(Status.FAILED, i)


class OrderedChoise(OperatorMixin):
    def __init__(self, a, b):
        self.a = a
        self.b = b
    def parse(self, target, i):
        resultA = self.a.parse(target, i)
        if resultA.status is Status.SUCCEED:
            return Node(Status.SUCCEED, resuluA.index, resultA.value)
        resultB = self.b.parse(target, resultA.index)
        if resultB.status is Status.SUCCEED:
            return Node(Status.SUCCEED, resultB.index, resultB.value)
        return Node(Status.FAILED, i)


class OneOrMore(OperatorMixin):
    def __init__(self, a):
        self.a = a
    def parse(self, target, i):
        result = (self.a >> ZeroOrMore(self.a)).parse(target, i)
        result.value = [result.value[0], *result.value[1]]
        return result


class ZeroOrMore(OperatorMixin):
    def __init__(self, a):
        self.a = a
    def parse(self, target, i, values = []):
        result = self.a.parse(target, i)
        if result.status is False or result.index == i:
            return Node(Status.SUCCEED, result.index, values)
        values.append(result.value)
        return self.parse(target, result.index, values)


class Optional(OperatorMixin):
    def __init__(self, a):
        self.a = a
    def parse(self, target, i):
        result = self.a.parse(target, i)
        return Node(Status.SUCCEED, result.index, result.value)


class Value(OperatorMixin):
    def __init__(self, val):
        self.val = val
    def parse(self, target, i):
        if target[i:i + len(self.val)] == self.val:
            return Node(Status.SUCCEED, i + len(self.val), self.val)
        return Node(Status.FAILED, i)


class And(OperatorMixin):
    def __init__(self, a):
        self.a = a
    def parse(self, target, i):
        result = self.a.parse(target, i)
        return Node(result.status, i, result.value)


class Not(OperatorMixin):
    def __init__(self, a):
        self.a = a
    def parse(self, target, i):
        result = self.a.parse(target, i)
        if result.status is Status.SUCCEED:
            return Node(Status.FAILED, i, result.value)
        return Node(Status.SUCCEED, i, result.value)


class Parser:
    def parse(self, grammar, string):
        result = grammar.parse(string, 0)
        return Node(Status.SUCCEED if result.index == len(string) else Status.FAILED, result.index, result.value)


grammar = Value("aaa") >> (Value("bbb") | Value("ccc")) >> +Value("eee") >> -Value("f") >> Value("g") # >> Not(Value("hhh"))
# This works
print(vars(Parser().parse(grammar, "aaaccceeeeeeeeeeeefg")))
# ==>
# {'status': <Status.SUCCEED: 1>, 'index': 20, 'value': [[[['aaa', 'ccc'], ['eee', 'eee', 'eee', 'eee']], 'f'], 'g']}