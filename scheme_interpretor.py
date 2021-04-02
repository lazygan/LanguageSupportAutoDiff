
from scheme_primitives import *
from scheme_reader import *


def create_global_frame():
    """Initialize and return a single-frame environment with built-in names."""
    env = Frame(None)
    add_primitives(env, PRIMITIVES)
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
    """Return whether EXPR evaluates to itself."""
    return scheme_atomp(expr) or scheme_stringp(expr) or expr is None


def scheme_apply(procedure, args, env):
    """Apply Scheme PROCEDURE to argument values ARGS (a Scheme list) in
    environment ENV."""
    check_procedure(procedure)
    return procedure.apply(args, env)


def eval_all(expressions, env):
    """Evaluate each expression im the Scheme list EXPRESSIONS in
    environment ENV and return the value of the last."""
    # BEGIN PROBLEM 8
    if expressions is nil:
        return None
    elif expressions.second is nil:  # Tail context
        return scheme_eval(expressions.first, env, True)
    else:
        scheme_eval(expressions.first, env)
        return eval_all(expressions.second, env)
    # END PROBLEM 8


################
# Environments #
################

class Frame:
    """An environment frame binds Scheme symbols to Scheme values."""

    def __init__(self, parent):
        """An empty frame with parent frame PARENT (which may be None)."""
        self.bindings = {}
        self.parent = parent

    def __repr__(self):
        if self.parent is None:
            return '<Global Frame>'
        s = sorted(['{0}: {1}'.format(k, v) for k, v in self.bindings.items()])
        return '<{{{0}}} -> {1}>'.format(', '.join(s), repr(self.parent))

    def define(self, symbol, value):
        """Define Scheme SYMBOL to have VALUE."""
        # BEGIN PROBLEM 3
        "*** YOUR CODE HERE ***"
        self.bindings[symbol] = value
        # END PROBLEM 3

    def lookup(self, symbol):
        """Return the value bound to SYMBOL. Errors if SYMBOL is not found."""
        # BEGIN PROBLEM 3
        "*** YOUR CODE HERE ***"
        if symbol in self.bindings:
            return self.bindings[symbol]
        elif self.parent:
            return self.parent.lookup(symbol)
        # END PROBLEM 3
        raise SchemeError('unknown identifier: {0}'.format(symbol))

    def make_child_frame(self, formals, vals):
        """Return a new local frame whose parent is SELF, in which the symbols
        in a Scheme list of formal parameters FORMALS are bound to the Scheme
        values in the Scheme list VALS. Raise an error if too many or too few
        vals are given.

        >>> env = create_global_frame()
        >>> formals, expressions = read_line('(a b c)'), read_line('(1 2 3)')
        >>> env.make_child_frame(formals, expressions)
        <{a: 1, b: 2, c: 3} -> <Global Frame>>
        """
        child = Frame(self)  # Create a new child with self as the parent
        # BEGIN PROBLEM 11
        "*** YOUR CODE HERE ***"
        if len(vals) > len(formals):
            raise SchemeError("too many vals are given")
        elif len(vals) < len(formals):
            raise SchemeError("too few vals are given")
        while formals is not nil:
            child.define(formals.first, vals.first)
            formals = formals.second
            vals = vals.second
        # END PROBLEM 11
        return child


##############
# Procedures #
##############

class Procedure:
    """The supertype of all Scheme procedures."""

    def eval_call(self, operands, env):
        """Standard function-call evaluation on SELF with OPERANDS as the
        unevaluated actual-parameter expressions and ENV as the environment
        in which the operands are to be evaluated."""
        # BEGIN PROBLEM 5
        "*** YOUR CODE HERE ***"
        eval_operands = lambda expr: scheme_eval(expr, env)
        return scheme_apply(self, operands.map(eval_operands), env)  # Every operands should be evaluated
        # END PROBLEM 5


def scheme_procedurep(x):
    return isinstance(x, Procedure)


class PrimitiveProcedure(Procedure):
    """A Scheme procedure defined as a Python function."""

    def __init__(self, fn, use_env=False, name='primitive'):
        self.name = name
        self.fn = fn
        self.use_env = use_env

    def __str__(self):
        return '#[{0}]'.format(self.name)

    def apply(self, args, env):
        """Apply SELF to ARGS in ENV, where ARGS is a Scheme list.

        >>> env = create_global_frame()
        >>> plus = env.bindings['+']
        >>> twos = Pair(2, Pair(2, nil))
        >>> plus.apply(twos, env)
        4
        """
        if not scheme_listp(args):
            raise SchemeError('arguments are not in a list: {0}'.format(args))
        # Convert a Scheme list to a Python list
        python_args = []
        while args is not nil:
            python_args.append(args.first)
            args = args.second
        # BEGIN PROBLEM 4
        "*** YOUR CODE HERE ***"
        if self.use_env:
            python_args.append(env)
        try:
            return self.fn(*python_args)
        except TypeError:
            raise SchemeError("wrong number of parameters were passed")
        # END PROBLEM 4


class UserDefinedProcedure(Procedure):
    """A procedure defined by an expression."""

    def apply(self, args, env):
        """Apply SELF to argument values ARGS in environment ENV. Applying a
        user-defined procedure evaluates all expressions in the body."""
        new_env = self.make_call_frame(args, env)
        return eval_all(self.body, new_env)


class LambdaProcedure(UserDefinedProcedure):
    """A procedure defined by a lambda expression or a define form."""

    def __init__(self, formals, body, env):
        """A procedure with formal parameter list FORMALS (a Scheme list),
        whose body is the Scheme list BODY, and whose parent environment
        starts with Frame ENV."""
        self.formals = formals
        self.body = body
        self.env = env

    def make_call_frame(self, args, env):
        """Make a frame that binds my formal parameters to ARGS, a Scheme list
        of values, for a lexically-scoped call evaluated in environment ENV."""
        # BEGIN PROBLEM 12
        "*** YOUR CODE HERE ***"
        return self.env.make_child_frame(self.formals, args)
        # END PROBLEM 12

    def __repr__(self):
        return 'LambdaProcedure({0}, {1}, {2})'.format(
            repr(self.formals), repr(self.body), repr(self.env))


def add_primitives(frame, funcs_and_names):
    """Enter bindings in FUNCS_AND_NAMES into FRAME, an environment frame,
    as primitive procedures. Each item in FUNCS_AND_NAMES has the form
    (NAME, PYTHON-FUNCTION, INTERNAL-NAME)."""
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
    """Evaluate a define form."""
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
    """Check EXPR is a proper list whose length is at least MIN and no more
    than MAX (default: no maximum). Raises a SchemeError if this is not the
    case.

    >>> check_form(read_line('(a b)'), 2)
    """
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


def check_procedure(procedure):
    """Check that PROCEDURE is a valid Scheme procedure."""
    if not scheme_procedurep(procedure):
        raise SchemeError('{0} is not callable: {1}'.format(
            type(procedure).__name__.lower(), str(procedure)))


