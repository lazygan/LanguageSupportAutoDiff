from scheme_reader import Pair, nil


class SchemeError(Exception):
    """Exception indicating an error in a Scheme program."""

def check_type(val, predicate, k, name):
    """Returns VAL.  Raises a SchemeError if not PREDICATE(VAL)
    using "argument K of NAME" to describe the offending value."""
    if not predicate(val):
        msg = "argument {0} of {1} has wrong type ({2})"
        raise SchemeError(msg.format(k, name, type(val).__name__))
    return val


def scheme_booleanp(x):
    return x is True or x is False

def scheme_truep(val):
    """All values in Scheme are true except False."""
    return val is not False

def scheme_falsep(val):
    """Only False is false in Scheme."""
    return val is False


def scheme_nullp(x):
    return x is nil

def scheme_listp(x):
    """Return whether x is a well-formed list. Assumes no cycles."""
    while x is not nil:
        if not isinstance(x, Pair):
            return False
        x = x.second
    return True

def scheme_stringp(x):
    return isinstance(x, str) and x.startswith('"')

def scheme_symbolp(x):
    return isinstance(x, str) and not scheme_stringp(x)

def scheme_numberp(x):
    return isinstance(x, (int, float)) and not scheme_booleanp(x)

def scheme_integerp(x):
    return scheme_numberp(x) and (isinstance(x, int) or round(x) == x)

def scheme_atomp(x):
    return (scheme_booleanp(x) or scheme_numberp(x) or
            scheme_symbolp(x) or scheme_nullp(x))

def check_nums(*vals):
    """Check that all arguments in VALS are numbers."""
    for i, v in enumerate(vals):
        if not scheme_numberp(v):
            msg = "operand {0} ({1}) is not a number"
            raise SchemeError(msg.format(i, v))
