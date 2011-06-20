import sys
from types import ModuleType

class MagicModule(ModuleType):

    @property
    def git_hash(self):
        fn = __file__ + '/../.git/refs/heads/master'
        with open(fn) as f:
            return f.read().strip()


old_mod = sys.modules[__name__]
sys.modules[__name__] = mod = MagicModule(__name__)
mod.__dict__.update(old_mod.__dict__)


if __name__ == '__main__':
    import os
    os.system('python -c "import magicmodule as x; print x.git_hash')
