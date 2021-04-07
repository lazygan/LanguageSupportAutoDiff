"""This module implements the built-in data types of the Scheme language, along
with a parser for Scheme expressions.

In addition to the types defined in this file, some data types in Scheme are
represented by their corresponding type in Python:
    number:       int or float
    symbol:       string
    boolean:      bool
    unspecified:  None

The __repr__ method of a Scheme value will return a Python expression that
would be evaluated to the value, where possible.

"""

from scheme_tokens import tokenize_lines, DELIMITERS
from buffer import Buffer, LineReader

# Pairs and Scheme lists

class Pair:
    def __init__(self, first, second,val=None):
        self.first = first
        self.second = second
        self.val=val

    def __repr__(self):
        return 'Pair({0}, {1}, {2})'.format(repr(self.first), repr(self.second),self.val)

    def __len__(self):
        n, second = 1, self.second
        while isinstance(second, Pair):
            n += 1
            second = second.second
        if second is not nil:
            raise TypeError('length attempted on improper list')
        return n

    def __eq__(self, p):
        if not isinstance(p, Pair):
            return False
        return self.first == p.first and self.second == p.second

    def map(self, fn):
        """Return a Scheme list after mapping Python function FN to SELF."""
        mapped = fn(self.first)
        if self.second is nil or isinstance(self.second, Pair):
            return Pair(mapped, self.second.map(fn))
        else:
            raise TypeError('ill-formed list')

class nil:
    """The empty list"""

    def __repr__(self):
        return 'nil'

    def __len__(self):
        return 0

    def map(self, fn):
        return self

nil = nil() # Assignment hides the nil class; there is only one instance

# Scheme list parser


def scheme_read(src):
    if src.current() is None:
        raise EOFError
    val = src.remove_front() # Get the first token
    if val == 'nil':
        return nil
    elif val == '(':
        # BEGIN PROBLEM 1
        return read_tail(src)
        # END PROBLEM 1
    elif val not in DELIMITERS:
        return val
    else:
        raise SyntaxError('unexpected token: {0}'.format(val))

def read_tail(src):
    """Return the remainder of a list in SRC, starting before an element or ).

    >>> read_tail(Buffer(tokenize_lines([')'])))
    nil
    >>> read_tail(Buffer(tokenize_lines(['2 3)'])))
    Pair(2, Pair(3, nil))
    >>> read_line('(1 . 2)')
    Pair(1, 2)
    """
    try:
        if src.current() is None:
            raise SyntaxError('unexpected end of file')
        elif src.current() == ')':
            # BEGIN PROBLEM 1
            "*** YOUR CODE HERE ***"
            src.remove_front()  # Remove the closing parenthesis
            return nil
            # END PROBLEM 1
        elif src.current() == '.':
            # BEGIN PROBLEM 2
            "*** YOUR CODE HERE ***"
            src.remove_front()  # Remove the dot
            val = scheme_read(src)  # Read one additional expression
            if src.current() == ')':
                src.remove_front()  # Remove the closing parenthesis
                return val
            else:
                raise SyntaxError("more than one element follow a dot")
            # END PROBLEM 2
        else:
            # BEGIN PROBLEM 1
            "*** YOUR CODE HERE ***"
            first = scheme_read(src)
            rest = read_tail(src)
            return Pair(first, rest)
            # END PROBLEM 1
    except EOFError:
        raise SyntaxError('unexpected end of file')

# Convenience methods


def buffer_lines(lines, prompt='scm> '):
    """Return a Buffer instance iterating through LINES."""
    input_lines = LineReader(lines, prompt)
    return Buffer(tokenize_lines(input_lines))

