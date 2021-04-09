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
    def eval_call(self, args):
        return self.apply(args)

    def diff(self,args,diff_args):
        return self.apply(args,diff_args=diff_args)

class PrimitiveProcedure(Procedure):
    def __init__(self, fn, use_env=False, name='primitive'):
        self.name = name
        self.fn = fn
        self.use_env = use_env

    def apply(self, args,diff_args=None):
        return self.fn(args,diff_args)


#class UserDefinedProcedure(Procedure):
#    def apply(self, args,env,diff_args=None):
#        if diff_args
#        self.trees[str(args)]=self.body
#
#
#        new_env = self.make_call_frame(args, env)
#        #return eval_all(self.body, new_env)
#
#
#class LambdaProcedure(UserDefinedProcedure):
#    def __init__(self, formals, body, env):
#        self.formals = formals
#        self.body = body
#        self.env = env
#        self.trees={}
#
#    def make_call_frame(self, args, env):
#        return self.env.make_child_frame(self.formals, args)
#
#    def __repr__(self):
#        return 'LambdaProcedure({0}, {1}, {2})'.format(
#            repr(self.formals), repr(self.body), repr(self.env))



def add_primitives(frame, funcs_and_names):
    for name, fn, proc_name in funcs_and_names:
        frame.define(name, PrimitiveProcedure(fn, name=proc_name))

def check_form(expr, min, max=float('inf')):
    if not scheme_listp(expr):
        raise SchemeError('badly formed expression: ' + str(expr))
    length = len(expr)
    if length < min:
        raise SchemeError('too few operands in form')
    elif length > max:
        raise SchemeError('too many operands in form')


def do_define_form(expressions, env):
     check_form(expressions, 2)
     target = expressions.first
     #如果式定义符号
     if scheme_symbolp(target):
         check_form(expressions, 2, 2)
         #存入表达式树
         value=expressions.second.first

         if isinstance(value,(int,float,bool)):
             env.define(target,value)

         elif isinstance(value,Pair):
             calc(value,env)
             env.define(target,value)
         return None
     #elif isinstance(target, Pair) and scheme_symbolp(target.first):
     #    # BEGIN PROBLEM 10
     #    "*** YOUR CODE HERE ***"
     #    formals = target.second
     #    body = expressions.second
     #    lambda_procedure = LambdaProcedure(formals, body, env)
     #    env.define(target.first, lambda_procedure)
     #    return target.first
     #    # END PROBLEM 10
     else:
         bad_target = target.first if isinstance(target, Pair) else target
         raise SchemeError('non-symbol: {0}'.format(bad_target))

SPECIAL_FORMS = {
    'define': do_define_form,
}


class Frame:
    def __init__(self, parent):
        self.bindings = {}
        self.parent = parent

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



def calc(root:Pair,env:Frame):
    if root.val!=None:
        return root.val
    first, rest =root.first,root.second

    if isinstance(first,(int,float)):
        root.val=first
        return root.val

    if isinstance(first,str):
        if  first in SPECIAL_FORMS:
            root.val=SPECIAL_FORMS[first](rest, env)
            return root.val
        symbol=env.lookup(first)
        if isinstance(symbol,(int,float,bool)):
            root.val=symbol
            return root.val
        if isinstance(symbol,Procedure):
            p=rest
            args=[]
            while p!=nil:
                args.append(calc(p,env))
                p=p.second
            root.val=symbol.eval_call(args)
            return root.val
        if isinstance(symbol,Pair):
            return symbol.val

    elif isinstance(root.first,Pair):
        root.val= calc(root.first,env)
        return root.val

    return root.val


def diff(root:Pair,env):
    first, rest =root.first,root.second

    if isinstance(first,(int,float)):
         return 0

    if isinstance(first,str):
        if  first in SPECIAL_FORMS:
            return None

        symbol=env.lookup(first)
        if first =="x1":
            return 1
        if isinstance(symbol,(int,float,bool)):
            return 0
        if isinstance(symbol,Procedure):
            p=rest
            args=[]
            diff_args=[]
            while p!=nil:
                args.append(calc(p,env))
                diff_args.append(diff(p,env))
                p=p.second
            return symbol.diff(args,diff_args)

        if isinstance(symbol,Pair):
            return diff(symbol,env)

    elif isinstance(first,Pair):
        return diff(first,env)


def primitive(*names):
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
        return diff_val[0]+diff_val[1]

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
        return val[0]*diff_val[1]+val[1]*diff_val[0]

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

@primitive("list")
def scheme_list(*vals):
    result = nil
    if(vals[1]==None):
        for e in reversed(vals[0]):
            result = Pair(e, result)
    else:
        for e in reversed(vals[1]):
            result = Pair(e, result)
    return result
