from scheme_reader import *
from type_check import *

"""This module implements the primitives of the Scheme language."""

import math
import operator
from type_check import *

PRIMITIVES = []

def create_global_frame():
    """Initialize and return a single-frame environment with built-in names."""
    env = Frame(None)
    add_primitives(env,PRIMITIVES)
    return env

##############
# Eval/Apply #
##############
def scheme_eval(expr, env, _=None):  # Optional third argument is ignored
    if scheme_symbolp(expr):
        return env.lookup(expr)
    elif self_evaluating(expr):
        return expr
    # All non-atomic expressions are lists (combinations)
    if not scheme_listp(expr):
        raise SchemeError('malformed list: {0}'.format(str(expr)))
    first, rest = expr.first, expr.second
    if scheme_symbolp(first) and first in SPECIAL_FORMS:
        return SPECIAL_FORMS[first](rest, env)
    else:
        operator = scheme_eval(first, env)  # Get the operator
        check_procedure(operator)  # Check the operator
        return operator.eval_call(rest, env)



def self_evaluating(expr):
    return scheme_atomp(expr) or scheme_stringp(expr) or expr is None


def scheme_apply(procedure, args, env):
    check_procedure(procedure)
    return procedure.apply(args,env)


def eval_all(expressions, env):
    if expressions is nil:
        return None
    elif expressions.second is nil:  # Tail context
        return scheme_eval(expressions.first, env, True)
    else:
        scheme_eval(expressions.first, env)
        return eval_all(expressions.second, env)




################
# Environments #
################

class Frame:
    def __init__(self, parent):
        self.bindings = {}
        self.parent = parent

    def __repr__(self):
        if self.parent is None:
            return '<Global Frame>'
        s = sorted(['{0}: {1}'.format(k, v) for k, v in self.bindings.items()])
        return '<{{{0}}} -> {1}>'.format(', '.join(s), repr(self.parent))

    def define(self, symbol, value):
        self.bindings[symbol] = value

    def lookup(self, symbol):
        if symbol in self.bindings:
            return self.bindings[symbol]
        elif self.parent:
            return self.parent.lookup(symbol)
        raise SchemeError('unknown identifier: {0}'.format(symbol))

    def make_child_frame(self, formals, vals):
        child = Frame(self)  # Create a new child with self as the parent
        if len(vals) > len(formals):
            raise SchemeError("too many vals are given")
        elif len(vals) < len(formals):
            raise SchemeError("too few vals are given")
        while formals is not nil:
            child.define(formals.first, vals.first)
            formals = formals.second
            vals = vals.second
        return child


##############
# Procedures #
##############

class Procedure:
    def eval_call(self, operands, env):
        eval_operands = lambda expr: scheme_eval(expr, env)
        val=scheme_apply(self, operands.map(eval_operands), env)  # Every operands should be evaluated
        return val




class PrimitiveProcedure(Procedure):
    def __init__(self, fn, use_env=False, name='primitive'):
        self.name = name
        self.fn = fn
        self.use_env = use_env

    def __str__(self):
        return '#[{0}]'.format(self.name)

    def apply(self, args, env):
        if not scheme_listp(args):
            raise SchemeError('arguments are not in a list: {0}'.format(args))
        # Convert a Scheme list to a Python list
        begin=args
        python_args = []
        while args is not nil:
            python_args.append(args.first)
            args = args.second
        if self.use_env:
            python_args.append(env)
        try:
            return self.fn(*python_args)
        except TypeError:
            raise SchemeError("wrong number of parameters were passed")


class UserDefinedProcedure(Procedure):
    def apply(self, args, env):
        new_env = self.make_call_frame(args, env)
        return eval_all(self.body, new_env)


class LambdaProcedure(UserDefinedProcedure):
    def __init__(self, formals, body, env):
        self.formals = formals
        self.body = body
        self.env = env

    def make_call_frame(self, args, env):
        return self.env.make_child_frame(self.formals, args)

    def __repr__(self):
        return 'LambdaProcedure({0}, {1}, {2})'.format(
            repr(self.formals), repr(self.body), repr(self.env))


def add_primitives(frame, funcs_and_names):
    for name, fn, proc_name in funcs_and_names:
        frame.define(name, PrimitiveProcedure(fn, name=proc_name))


#################
# Special Forms #
#################

# Each of the following do_xxx_form functions takes the cdr of a special form as
# its first argument---a Scheme list representing a special form without the
# initial identifying symbol (if, lambda, quote, ...). Its second argument is
# the environment in which the form is to be evaluated.

def do_define_form(expressions, env):
    check_form(expressions, 2)
    target = expressions.first
    if scheme_symbolp(target):
        check_form(expressions, 2, 2)
        value = scheme_eval(expressions.second.first, env)
        env.define(target, value)
        return target
    elif isinstance(target, Pair) and scheme_symbolp(target.first):
        # BEGIN PROBLEM 10
        "*** YOUR CODE HERE ***"
        formals = target.second
        body = expressions.second
        lambda_procedure = LambdaProcedure(formals, body, env)
        env.define(target.first, lambda_procedure)
        return target.first
        # END PROBLEM 10
    else:
        bad_target = target.first if isinstance(target, Pair) else target
        raise SchemeError('non-symbol: {0}'.format(bad_target))


def do_if_form(expressions, env):
    """Evaluate an if form."""
    check_form(expressions, 2, 3)
    if scheme_truep(scheme_eval(expressions.first, env)):
        return scheme_eval(expressions.second.first, env, True)  # Tail context
    elif len(expressions) == 3:
        return scheme_eval(expressions.second.second.first, env, True)  # Tail context


def do_and_form(expressions, env):
    """Evaluate a (short-circuited) and form."""
    # BEGIN PROBLEM 13
    "*** YOUR CODE HERE ***"
    if expressions is nil:
        return True
    elif expressions.second is nil:  # Tail context
        return scheme_eval(expressions.first, env, True)
    else:
        first_expr = scheme_eval(expressions.first, env)
        if scheme_falsep(first_expr):  # The first expression is False
            return False
        elif scheme_truep(first_expr):  # The first expression is True
            return do_and_form(expressions.second, env)
    # END PROBLEM 13


def do_or_form(expressions, env):
    """Evaluate a (short-circuited) or form."""
    # BEGIN PROBLEM 13
    "*** YOUR CODE HERE ***"
    if expressions is nil:
        return False
    elif expressions.second is nil:  # Tail context
        return scheme_eval(expressions.first, env, True)
    else:
        first_expr = scheme_eval(expressions.first, env)
        if scheme_falsep(first_expr):  # The first expression is False
            return do_or_form(expressions.second, env)
        else:  # The first expression is True
            return first_expr
    # END PROBLEM 13


SPECIAL_FORMS = {
    'and': do_and_form,
    'define': do_define_form,
    'if': do_if_form,
    'or': do_or_form,
}


# Utility methods for checking the structure of Scheme programs

def check_form(expr, min, max=float('inf')):
    if not scheme_listp(expr):
        raise SchemeError('badly formed expression: ' + str(expr))
    length = len(expr)
    if length < min:
        raise SchemeError('too few operands in form')
    elif length > max:
        raise SchemeError('too many operands in form')


def check_formals(formals):
    """Check that FORMALS is a valid parameter list, a Scheme list of symbols
    in which each symbol is distinct. Raise a SchemeError if the list of
    formals is not a well-formed list of symbols or if any symbol is repeated.

    >>> check_formals(read_line('(a b c)'))
    """
    symbols = set()

    def check_and_add(symbol):
        if not scheme_symbolp(symbol):
            raise SchemeError('non-symbol: {0}'.format(symbol))
        if symbol in symbols:
            raise SchemeError('duplicate symbol: {0}'.format(symbol))
        symbols.add(symbol)

    while isinstance(formals, Pair):
        check_and_add(formals.first)
        formals = formals.second


def scheme_procedurep(x):
    return isinstance(x, Procedure)

def check_procedure(procedure):
    """Check that PROCEDURE is a valid Scheme procedure."""
    if not scheme_procedurep(procedure):
        raise SchemeError('{0} is not callable: {1}'.format(
            type(procedure).__name__.lower(), str(procedure)))


def primitive(*names):
    """An annotation to convert a Python function into a PrimitiveProcedure."""
    def add(fn):
        for name in names:
            PRIMITIVES.append((name, fn, names[0]))
        return fn
    return add

@primitive("list")
def scheme_list(*vals):
    result = nil
    for e in reversed(vals):
        result = Pair(e, result)
    return result

def _numcomp(op, x, y):
    check_nums(x, y)
    return op(x, y)

@primitive("=")
def scheme_eq(x, y):
    return _numcomp(operator.eq, x, y)

@primitive("<")
def scheme_lt(x, y):
    return _numcomp(operator.lt, x, y)

@primitive(">")
def scheme_gt(x, y):
    return _numcomp(operator.gt, x, y)

@primitive("<=")
def scheme_le(x, y):
    return _numcomp(operator.le, x, y)

@primitive(">=")
def scheme_ge(x, y):
    return _numcomp(operator.ge, x, y)


@primitive("+")
def scheme_add(val0,val1):
    check_nums(val0,val1)
    return val0+val1

@primitive("-")
def scheme_sub(val0, *vals):
    check_nums(val0, *vals) # fixes off-by-one error
    if len(vals) == 0:
        return -val0
    return val0-vals[0]

@primitive("*")
def scheme_mul(val0,val1):
    check_nums(val0,val1) # fixes off-by-one error
    return val0*val1

@primitive("/")
def scheme_div(val0, val1):
    check_nums(val0, val1) # fixes off-by-one error
    try:
        return val0/val1
    except ZeroDivisionError as err:
        raise SchemeError(err)

@primitive("expt")
def scheme_expt(val0, val1):
    check_nums(val0, val1)
    return pow(val0, val1)

@primitive("ln")
def scheme_ln(val):
    check_nums(val)
    return math.log(val,math.e)

@primitive("abs")
def scheme_abs(val0):
    return abs(val0)

@primitive("sin")
def scheme_sin(val0):
    return math.sin(val0)

#def number_fn(module, name):
#    """A Scheme primitive that calls the numeric Python function named
#    MODULE.FN."""
#    py_fn = getattr(module, name)
#    def scheme_fn(*vals):
#        check_nums(*vals)
#        return py_fn(*vals)
#    return scheme_fn

# Add number functions in the math module as Scheme primitives
#for _name in ["acos", "acosh", "asin", "asinh", "atan", "atan2", "atanh",
#              "ceil", "copysign", "cos", "cosh", "degrees", "floor", "log",
#              "log10", "log1p", "log2", "radians", "sin", "sinh", "sqrt",
#              "tan", "tanh", "trunc"]:
#    primitive(_name)(number_fn(math, _name))

