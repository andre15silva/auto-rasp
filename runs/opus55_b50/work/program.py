
import sys
sys.path.insert(0, '/work')
import importlib, gonet4
importlib.reload(gonet4)
MLP_EXACTNESS = 500000
def program():
    return gonet4.build()
