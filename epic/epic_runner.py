import importlib
import sys
from types import ModuleType

from docopt import DocoptExit

from .epic_importer import EpicImporter


class EpicRunner:

    def __init__(self, plugin_dirs: list[str]) -> None:
        self.plugin_dirs = plugin_dirs

        for path in self.plugin_dirs:
            sys.path.append(path)
            EpicImporter.load_paths.add(path)

    def execute_plugin(self, mod: ModuleType, argv: list):
        try:
            mod.run(argv)
        except DocoptExit as de:
            print(de)
            return
        except SystemExit as se:
            print(se)
            return

    def run(self, argv: list):
        try:
            cmd, *argv = argv
            mod = importlib.import_module(cmd)
            self.execute_plugin(mod, argv)
        except Exception:
            pass