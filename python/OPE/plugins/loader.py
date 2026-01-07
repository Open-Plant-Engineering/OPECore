import pkgutil
import importlib

def load_plugins():
    for module in pkgutil.iter_modules():
        if module.name.startswith("OPE_core_engine_"):
            importlib.import_module(module.name)