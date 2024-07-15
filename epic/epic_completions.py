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


    def complete(self, args: list[str]):
        line = args[1]
        epic_completer, *argv = shlex.split(line)

        if line.endswith(tuple(string.whitespace)):
            argv.append('')

        if len(argv) > 0:
            cmd, *argv = argv
            try:
                mod = importlib.import_module(cmd)
                lib_name = cmd
                for i, arg in enumerate(argv):
                    if arg in mod.__spec__.loader_state['subcommands']:
                        lib_name = f'{mod.__name__}.{arg}'
                        mod = importlib.import_module(lib_name)

                if len(argv) > 0:
                    matching_options = mod._completions(argv, argv[-1], len(argv) -1, len(argv[-1])-1)
                else:
                    matching_options = mod._completions(argv, '', 0, 0)

                # Print each matching option on a new line
                for option in matching_options:
                    print(option)
            except ModuleNotFoundError:
                for cmd in self.get_top_level_cmds():
                    print(cmd)
            except ValueError:
                for cmd in self.get_top_level_cmds():
                    print(cmd)
        else:
            for cmd in self.get_top_level_cmds():
                print(cmd)