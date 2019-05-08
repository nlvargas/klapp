#
# Copyright 2018, Gurobi Optimization, LLC
#
# Interactive shell customization example
#
# Define a set of customizations for the Gurobi shell.
# Type 'from custom import *' to import them into your shell.
#

from gurobipy import *


# custom read command --- change directory as appropriate

def myread(name):
    return read('/home/jones/models/' + name)


# simple termination callback


def mycallback(model, where):
    if where == GRB.Callback.MIP:
        nodecnt = model.cbGet(GRB.Callback.MIP_NODCNT)
        objbst  = model.cbGet(GRB.Callback.MIP_OBJBST)
        objbnd  = model.cbGet(GRB.Callback.MIP_OBJBND)
        solcnt  = model.cbGet(GRB.Callback.MIP_SOLCNT)
        time    = model.cbGet(GRB.Callback.RUNTIME)
        #Esta condicion es el tiempo maximo que tiene Gurobi para resolver 
        if time > 900 and objbst < GRB.INFINITY and solcnt:
            print("Stop early: "+str(time)+" seconds has passed")
            model.terminate()
        #Esta condicion ve el Gap que permite antes de entregar una solucion
        if abs(objbst - objbnd) < 0.05 * (1.0 + abs(objbst)) and solcnt:
            print('Stop early - 5% gap achieved')
            model.terminate()



# custom optimize() function that uses callback

def myopt(model):
    model.optimize(mycallback)
