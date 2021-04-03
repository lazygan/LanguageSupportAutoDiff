
from scipy import optimize

from dsl_eval import *

from scipy.optimize import minimize
from scipy.optimize import fmin
import numpy as np


def P(patch):
    P=[]
    head=patch.acpHead
    p=head.nextAcp
    while p!=head:
        if p.nextBcp!=None:
            P.append([p.nextBcp.x,p.nextBcp.y])
        if p.preBcp != None:
            P.append([p.preBcp.x,p.preBcp.y])
        P.append([p.x,p.y])
        p=p.nextAcp
    p=head
    if p.nextBcp!=None:
        P.append([p.nextBcp.x,p.nextBcp.y])
    if p.preBcp != None:
        P.append([p.preBcp.x,p.preBcp.y])
    P.append([p.x,p.y])

    P=np.asarray(P)
    return P




def optimization(patches,F:Input):

    x0=F.getTheta0()
    print(x0)

    def opfunc(x):
        res=np.sum((P(F.eval_theta(x)[0])-P(patches[0]))**2)
        return res

    e = 0.2
    cons = (
        {'type': 'ineq', 'fun': lambda x: x[0] - e},
        {'type': 'ineq', 'fun': lambda x: x[1] - e},
        {'type': 'ineq', 'fun': lambda x: x[2] - e}
    )
    res = minimize(opfunc, x0,method='SLSQP', constraints=cons)

    patches_ = F.eval_theta(res.x)
    return patches_


