import importlib
import sys
from types import ModuleType

from docopt import DocoptExit

from .epic_importer import EpicImporter


class EpicRunner:

    def __init__(self, command_dirs: list[str]) -> None:
        self.command_dirs = command_dirs

        for path in self.command_dirs:
            sys.path.append(path)
            EpicImporter.load_paths.add(path)

    def execute_command(self, mod: ModuleType, argv: list):
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
            self.execute_command(mod, argv)
        except Exception:
            pass