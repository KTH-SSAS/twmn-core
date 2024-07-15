#!/usr/bin/env python3
import importlib
import os
import shlex
import string
import sys
from pkgutil import iter_modules

from .epic_importer import EpicImporter

command_dirs=['libexec']

class EpicCompletion():
    def __init__(self, command_dirs: list[str]) -> None:
        self.command_dirs = command_dirs

        for path in self.command_dirs:
            sys.path.append(path)
            EpicImporter.load_paths.add(path)


    def get_top_level_cmds(self):
        return [mod.name for mod in iter_modules(self.command_dirs)]


    def complete(self, line: str):
        if line.endswith(tuple(string.whitespace)):
            line += "''"

        _, cmd, *argv = shlex.split(line)

        try:
            mod = importlib.import_module(cmd)

            if argv:
                matching_options = mod._completions(argv, argv[-1], len(argv) -1, len(argv[-1])-1)
            else:
                matching_options = mod._completions(argv, '', 0, 0)

            print(*matching_options, sep='\n')

            return
        except (ModuleNotFoundError, ValueError):
            print(*self.get_top_level_cmds(), sep='\n')
