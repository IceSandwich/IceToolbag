import importlib, os, inspect
from .base import EffectBase

ICETB_EFFECTS_CLASSES = []

excludeList = [ '__init__.py', 'base.py' ]
for fn in [ x for x in os.listdir(os.path.split(__file__)[0]) if x not in excludeList and x[-3:] == '.py' and not os.path.isdir(x) ]: # ignore items in excludeList, non-py file and dirs
    module = importlib.import_module("." + fn[:-3], __package__)
    classes = [ x for x in inspect.getmembers(module, inspect.isclass) if x[1] != EffectBase and issubclass(x[1], EffectBase) ] # select classes based on EffectBase
    if len(classes) == 0:
        raise Exception("Can't load %s cause no class based on EffectBased detected."%fn)
    for clazz in classes:
        if clazz not in ICETB_EFFECTS_CLASSES:
            print("icetb load effect module:", clazz[0])
            ICETB_EFFECTS_CLASSES.append(clazz[1])
    

ICETB_EFFECTS_NAMES = [ x.getName() for x in ICETB_EFFECTS_CLASSES ]
ICETB_EFFECTS_DICTS = { x.getName(): x for x in ICETB_EFFECTS_CLASSES }