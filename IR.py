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
nil = nil() # Assignment hides the nil class; there is only one instance
