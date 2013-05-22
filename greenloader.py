import imp
import sys

from eventlet import patcher

__all__ = ['install_patcher', ]


class _Loader(object):
    def __init__(self, packages=None):
        self._packages = packages or []
        self._loading = set()

    def find_module(self, name, path=None):
        if (name.split('.')[0] in self._packages
                and name not in self._loading):
            try:
                # does it exist?
                imp.find_module(name.rpartition('.')[2], path)
            except ImportError:
                return
            return self

    def load_module(self, fullname):
        if fullname in sys.modules:
            return sys.modules[fullname]
        self._loading.add(fullname)
        try:
            mod = sys.modules[fullname] = patcher.import_patched(fullname)
            return mod
        finally:
            self._loading.remove(fullname)

    def add_packages(self, packages):
        self._packages.extend(list(packages))

loader = _Loader()


def install_patcher(packages):
    if loader not in sys.meta_path:
        sys.meta_path.append(loader)
    loader.add_packages(packages)
