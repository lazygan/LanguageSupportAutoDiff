from scheme_tokens import DELIMITERS,tokenize_line

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
    def copy_pair(self):
        res=Pair(None,None,self.val)
        if isinstance(self.first,Pair):
            res.first=self.first.copy_pair()
        else:
            res.first=self.first

        if isinstance(self.second,Pair):
            res.second=self.second.copy_pair()
        else:
            res.second=self.second
        return res




class nil:
    """The empty list"""

    def __repr__(self):
        return 'nil'

    def __len__(self):
        return 0

    def map(self, fn):
        return self

class Buffer:
    def __init__(self, source):
        self.index = 0
        self.source=[]
        for line in source:
            self.source += line

    def remove_front(self):
        current = self.current()
        self.index += 1
        return current

    def current(self):
        return self.source[self.index]

    @property
    def more_on_line(self):
        return self.index < len(self.source)

nil = nil() # Assignment hides the nil class; there is only one instance

def scheme_read(src):
    if src.current() is None:
        raise EOFError
    val = src.remove_front() # Get the first token
    if val == 'nil':
        return nil
    elif val == '(':
        return read_tail(src)
    elif val not in DELIMITERS:
        return val
    else:
        raise SyntaxError('unexpected token: {0}'.format(val))

def read_tail(src):
    try:
        if src.current() is None:
            raise SyntaxError('unexpected end of file')
        elif src.current() == ')':
            src.remove_front()  # Remove the closing parenthesis
            return nil
        else:
            first = scheme_read(src)
            rest = read_tail(src)
            return Pair(first, rest)
            # END PROBLEM 1
    except EOFError:
        raise SyntaxError('unexpected end of file')


def buffer_lines(lines):
    for i in range(len(lines)):
        lines[i]=lines[i].strip('\n')
        lines[i]=tokenize_line(lines[i])
    return Buffer(lines)

