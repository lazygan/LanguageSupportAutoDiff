from scheme_reader import *
from type_check import *
import math
################
# Environments #
################

PRIMITIVES = []

def create_global_frame():
    """Initialize and return a single-frame environment with built-in names."""
    env = Frame(None)
    add_primitives(env,PRIMITIVES)
    return env


##############
# Procedures #
##############

class Procedure:
    """The supertype of all Scheme procedures."""
    def eval_call(self, args):
        return self.apply(args)

    def diff(self,args,diff_args):
        return self.apply(args,diff_args)

class PrimitiveProcedure(Procedure):
    def __init__(self, fn, use_env=False, name='primitive'):
        self.name = name
        self.fn = fn
        self.use_env = use_env

    def __str__(self):
        return '#[{0}]'.format(self.name)

    def apply(self, args,diff_args=None):
        return self.fn(args,diff_args)



def add_primitives(frame, funcs_and_names):
    for name, fn, proc_name in funcs_and_names:
        frame.define(name, PrimitiveProcedure(fn, name=proc_name))


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
        """Define Scheme SYMBOL to have VALUE."""
        # BEGIN PROBLEM 3
        "*** YOUR CODE HERE ***"
        self.bindings[symbol] = value
        # END PROBLEM 3

    def lookup(self, symbol):
        if symbol in self.bindings:
            return self.bindings[symbol]
        elif self.parent:
            return self.parent.lookup(symbol)
        # END PROBLEM 3
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


def calc(root:Pair,env):
    if root.first=="x1":
        root.val=2
        return root.val
    if root.first=="x2":
        root.val=5
        return root.val
    p=root.second

    args=[]
    while p!=nil:
        args.append(calc(p,env))
        p=p.second

    if isinstance(root.first,str):
        proc:Procedure=env.lookup(root.first)
        if isinstance(proc,Procedure):
            root.val=proc.eval_call(args)
    else:
        root.val= calc(root.first,env)
    return root.val


def diff(root:Pair,env):
    if root.first=="x1":
        return 1
    if root.first=="x2":
        return 0
    p=root.second
    args=[]
    diff_args=[]
    while p!=nil:
        args.append(p.val)
        diff_args.append(diff(p,env))
        p=p.second
    if isinstance(root.first,str):
        proc:Procedure=env.lookup(root.first)
        if isinstance(proc,Procedure):
            return proc.diff(args,diff_args)
    else:
        return diff(root.first,env)




def primitive(*names):
    """An annotation to convert a Python function into a PrimitiveProcedure."""
    def add(fn):
        for name in names:
            PRIMITIVES.append((name, fn, names[0]))
        return fn
    return add

@primitive("+")
def scheme_add(val,diff_val=None):
    if diff_val==None:
        return val[0]+val[1]
    else:
        return diff_val[0]+diff_val[0]

@primitive("-")
def scheme_sub(val,diff_val=None):
    if diff_val==None:
        if len(val) == 1:
            return -val[0]
        return val[0]-val[1]
    else:
        if len(val) == 1:
            return -diff_val[0]
        return diff_val[0]-diff_val[1]

@primitive("*")
def scheme_mul(val,diff_val=None):
    if diff_val==None:
        return val[0]*val[1]
    else:
        return val[0]*diff_val[1]+val[0]*diff_val[1]

@primitive("/")
def scheme_div(val,diff_val=None):
    if diff_val==None:
        try:
            return val[0]/val[1]
        except ZeroDivisionError as err:
            raise SchemeError(err)
    else:
        try:
            return (diff_val[0]*val[1]-diff_val[1]*val[0])/((val[1]*val[1]))
        except ZeroDivisionError as err:
            raise SchemeError(err)

@primitive("ln")
def scheme_ln(val,diff_val=None):
    if diff_val==None:
        return math.log(val[0],math.e)
    else:
        return diff_val[0]/val[0]

@primitive("sin")
def scheme_sin(val,diff_val=None):
    if diff_val==None:
        return math.sin(val[0])
    else:
        return diff_val[0]*math.cos(val[0])

