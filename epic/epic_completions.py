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
        try:
            # Strip off EpicRunner program name and seperate
            # into cmd and argv
            _, cmd, *argv = shlex.split(line)
        
            if line.endswith(tuple(string.whitespace)):
                # If the full line ended in whitespace, the user
                # Is trying to complete a new word.
                # Appdend the empty string to argv that shlex stripped off.
                argv.append('')

            mod = importlib.import_module(cmd)

            if argv:
                # EpicImporter mod._completion expects the full line, including
                # the current cmd, like sys.argv
                words = [cmd] + argv
                matching_options = mod._completions(words, words[-1], len(words) -1, len(words[-1])-1)
            else:
                matching_options = mod._completions(cmd, '', 0, 0)

            print(*matching_options, sep='\n')

            return
        except (ModuleNotFoundError, ValueError):
            print(*self.get_top_level_cmds(), sep='\n')
