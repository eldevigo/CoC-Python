from coc import Immutable
from coc.exceptions import *


class Expr(Immutable):
    """ 
    """
    def __init__(self, expr):
        super().__init__()
        try:
            filters = [Filter(f) for f in expr.split('|')[1:]]
        except AttributeError as e:
            raise ParseError("conditional expression expected but "
                             "received ``{0}`` instead".format(type(expr)))
        self.tokens = condition.split(expr.split('|')[0])
        self.arity = len(tokens - 1)
        try:
            if arity == 0:
                self.test = lambda x, _: bool(x)
                args = [tokens[0]]
            elif arity == 1:
                try:
                    self.test = unary[tokens[0]]
                    args = [tokens[1]]
                except:
                    pass
            elif arity == 2:
                try:
                    self.test = binary[tokens[1]]
                    args = [tokens[0], tokens[2]]
                except KeyError:
                    self.test = funcs[tokens[0]]
                    args = tokens[1:]
            else:
                self.test = funcs[tokens[0]]
                args = tokens[1:]
        except KeyError:
            raise ParseError("no recognized operator or function in "
                             "conditional expression ``{0}``".format(expr),
                             expr=expr)
        self.initialized = True

    def test(self, state_func):
        args = list()
        for arg in self.args:
            if type(arg) == str:
                try:
                    args.append(state_func(arg))
                except StateNotFoundError:
                    args.append(arg)
            else:
                args.append(arg)
        return self.test(args)


class All(Immutable):
    """
    """
    def __init__(self, exprs):
        super().__init__()
        self.elements = [parse(item) for item in exprs]
        self.initialized = True

    def test(self, state_func):
        for element in self.elements:
            if not element.test(state_func):
                return False
        return True


class Any(Immutable):
    """
    """
    def __init__(self, exprs):
        super().__init__()
        self.elements = [parse(item) for item in exprs]
        self.initialized = True

    def test(self, state_func):
        for element in self.elements:
            if element.test(state_func):
                return True
        return False


def parse(schema):
    if type(schema) == str:
        return Expr(schema)
    elif type(schema) == list:
        return All(schema)
    elif type(schema) == dict:
        try:
            return Any(schema['any'])
        except KeyError:
            return All(schema['all'])
    else:
        raise SchemaError("conditional schema tree is of an unrecognized type",
                          schema=schema)


unary = {
        '!': lambda x: not x[0]
        }

binary = {
        '=': lambda x: x[0] == x[1],
        '!=': lambda x: x[0] != x[1],
        '>': lambda x: x[0] > x[1],
        '>=': lambda x: x[0] >= x[1],
        '<': lambda x: x[0] < x[1],
        '<=': lambda x: x[0] <= x[1],
        '': lambda x: x[0] > x[1],
        }

funcs = {
        'largest': lambda x: sorted(x, reverse=True)[0],
        'secondLargest': lambda x: sorted(x, reverse=True)[1],
        'smallest': lambda x: sorted(x)[0],
        'secondSmallest': lambda x: sorted(x)[1],
        }
