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
    def eval_call(self, args:Pair):
        return self.apply(args)

    def diff(self,args:Pair,diff_args):
        return self.apply(args,diff_args)

    def rdiff(self,args:Pair,rdiff_args,res):
        return self.apply(args,rdiff_args=rdiff_args,res=res)


class PrimitiveProcedure(Procedure):
    def __init__(self, fn, use_env=False, name='primitive'):
        self.name = name
        self.fn = fn
        self.use_env = use_env

    def apply(self, args,diff_args=None,rdiff_args=None,res=None):
        return self.fn(args,diff_args,rdiff_args)


class UserDefinedProcedure(Procedure):
    def apply(self, args:Pair,diff_args=None,rdiff_args=None,res=None):
        if diff_args != None:
            # 如果是calc过程
            if self.evaled_body.get(str(args))==None:
                raise RuntimeError
            new_env = self.make_child_frame(args)
            p = self.evaled_body[str(args)]
            while p.first.first in SPECIAL_FORMS:
                p = p.second
            return diff(p,new_env)

        if rdiff_args != None and res!=None:
            if self.evaled_body.get(str(args))==None:
                raise RuntimeError
            new_env = self.make_child_frame(args)
            p = self.evaled_body[str(args)]
            while p.first.first in SPECIAL_FORMS:
                p = p.second
            reverse_diff(p,new_env,res,rdiff_args[-1])

        else:
            if self.evaled_body.get(str(args))==None:
                self.evaled_body[str(args)]  = self.unevaled_body.copy_pair()
                new_env = self.make_child_frame(args)
                p=self.evaled_body[str(args)]
                while True:
                     q=p.first
                     if isinstance(q,Pair) and q.first in SPECIAL_FORMS:
                         SPECIAL_FORMS[q.first](q.second, new_env)
                     else:
                         break
                     p=p.second
                calc(p,new_env)
                return p.val
            else:
                p = self.evaled_body[str(args)]
                while p.first.first in SPECIAL_FORMS:
                    p = p.second
                return p.val

class LambdaProcedure(UserDefinedProcedure):
    def __init__(self, formals, body, env):
        self.formals = formals
        self.unevaled_body = body
        self.env = env
        self.evaled_body={}

    def make_child_frame(self,args):
        formals=self.formals
        vals=args
        child = Frame(self.env)  # Create a new child with self as the parent
        if len(args) > len(formals):
            raise SchemeError("too many vals are given")
        elif len(args) < len(formals):
            raise SchemeError("too few vals are given")
        while formals is not nil:
            if isinstance(vals.first, (int, float, bool)):
                child.define(formals.first, vals.first)
            if isinstance(vals.first, str):
                child.define(formals.first, vals)
            if isinstance(vals.first, Pair):
                child.define(formals.first, vals.first)
            formals = formals.second
            vals = vals.second
        return child



    def __repr__(self):
        return 'LambdaProcedure({0}, {1}, {2})'.format(
            repr(self.formals), repr(self.unevaled_body), repr(self.env))



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
     elif isinstance(target, Pair) and isinstance(target.first,str):
         formals = target.second
         body = expressions.second
         lambda_procedure = LambdaProcedure(formals, body, env)
         env.define(target.first, lambda_procedure)
         return None
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
        #lookup 只会返回值或者Pair
        symbol=env.lookup(first)

        if isinstance(symbol,(int,float,bool)):
            root.val=symbol
            return root.val
        if isinstance(symbol,Procedure):
            p=rest
            while p!=nil:
                calc(p,env)
                p=p.second
            root.val=symbol.eval_call(rest)
            return root.val

        if isinstance(symbol,Pair):
            root.val=calc(symbol,env)
            return root.val

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
        if first =="x1":
            return 1

        symbol=env.lookup(first)
        if isinstance(symbol,(int,float,bool)):
            return 0
        if isinstance(symbol,Procedure):
            p=rest
            diff_args=[]
            while p!=nil:
                calc(p,env)
                diff_args.append(diff(p,env))
                p=p.second
            return symbol.diff(rest,diff_args)

        if isinstance(symbol,Pair):
            return diff(symbol,env)

    elif isinstance(first,Pair):
        return diff(first,env)

def reverse_diff(root:Pair,env:Frame,res:dict,pass_val):
    first, rest =root.first,root.second
    if isinstance(first,(int,float)):
         return

    if isinstance(first,str):
        if  first in SPECIAL_FORMS:
            return
        if first =="x2" or first=="x1":
            res[first]+=pass_val
            return
        if first=="list":
            p=rest
            while p!=nil:
                reverse_diff(p.first,env,res,pass_val)
                p=p.second
            return


        symbol=env.lookup(first)

        if isinstance(symbol,(int,float,bool)):
            return

        if isinstance(symbol,Procedure):
            p=rest
            rdiff_args=[]
            rdiff_res=[]
            while p!=nil:
                rdiff_args.append(0)
                p=p.second

            count=0
            p=rest
            rdiff_args.append(pass_val)
            if isinstance(symbol,UserDefinedProcedure):
                symbol.rdiff(rest,rdiff_args,res)
                return

            while p!=nil:
                rdiff_args[count]=1
                rdiff_res.append(symbol.rdiff(rest,rdiff_args,res))
                rdiff_args[count]=0
                count+=1
                p=p.second
            p=rest
            count=0
            while p!=nil:
                reverse_diff(p,env,res,rdiff_res[count])
                count+=1
                p=p.second
            return

        if isinstance(symbol,Pair):
            reverse_diff(symbol,env,res,pass_val)
            return

    elif isinstance(first,Pair):
        reverse_diff(first, env, res, pass_val)
        return


def primitive(*names):
    def add(fn):
        for name in names:
            PRIMITIVES.append((name, fn, names[0]))
        return fn
    return add

@primitive("+")
def scheme_add(p,diff_val=None,rdiff_val=None):
    if diff_val!=None:
        return diff_val[0]+diff_val[1]
    elif rdiff_val != None:
        pass_val = rdiff_val[-1]
        return pass_val*(rdiff_val[0]+rdiff_val[1])
    else :
        check_nums(2,2)
        return p.val+p.second.val

@primitive("-")
def scheme_sub(p,diff_val=None,rdiff_val=None):
    if diff_val!=None:
        if len(p) == 1:
            return -diff_val[0]
        return diff_val[0]-diff_val[1]
    elif rdiff_val!=None:
        pass_val=rdiff_val[-1]
        if len(p) == 1:
            return -pass_val
        return pass_val*(rdiff_val[0]-rdiff_val[1])
    else:
        if len(p) == 1:
            return -p.val
        return p.val-p.second.val

@primitive("*")
def scheme_mul(p,diff_val=None,rdiff_val=None):
    if diff_val!=None:
        return p.val * diff_val[1] + p.second.val * diff_val[0]
    elif rdiff_val != None:
        pass_val=rdiff_val[-1]
        return pass_val*(rdiff_val[0]*p.second.val+rdiff_val[1]*p.val)
    else:
        return p.val*p.second.val

#@primitive("/")
#def scheme_div(p,diff_val=None):
#    if diff_val==None:
#        try:
#            return p.val/p.second.val
#        except ZeroDivisionError as err:
#            raise SchemeError(err)
#    else:
#        try:
#            return (diff_val[0]*p.second.val-diff_val[1]*p.val)/((p.second.val*p.second.val))
#        except ZeroDivisionError as err:
#            raise SchemeError(err)

@primitive("ln")
def scheme_ln(p,diff_val=None,rdiff_val=None):
    if diff_val!=None:
        return diff_val[0]/p.val
    elif rdiff_val!=None:
        pass_val=rdiff_val[-1]
        return pass_val/p.val
    else:
        return math.log(p.val, math.e)


@primitive("sin")
def scheme_sin(p,diff_val=None,rdiff_val=None):
    if diff_val!=None:
        return diff_val[0]*math.cos(p.val)
    elif rdiff_val!=None:
        pass_val=rdiff_val[-1]
        return pass_val*math.cos(p.val)
    else:
        return math.sin(p.val)

@primitive("list")
def scheme_list(p,diff_val=None,rdiff_val=None):
    result = nil
    if diff_val!=None:
        for e in reversed(diff_val):
            result = Pair(e, result)
    elif rdiff_val!=None:
        return
    else:
        args=[]
        while p!=nil:
            args.append(p.val)
            p=p.second
        for e in reversed(args):
            result = Pair(e, result)
    return result


