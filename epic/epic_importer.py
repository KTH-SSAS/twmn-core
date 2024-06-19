import os
import re
import ast
import sys
import platform
import functools
import subprocess
from typing import List
from types import ModuleType

import docopt
from importlib.machinery import ModuleSpec
from importlib.abc import PathEntryFinder, Loader
from jinja2 import Template, StrictUndefined
from pathlib import Path

class EpicImporter(Loader, PathEntryFinder):
    bash_libs = list()
    help_tokens = dict()
    load_paths = list()

    @staticmethod
    def epic_importer_factory(path: str):
        if Path(path).parts[0] in EpicImporter.load_paths:
            return EpicImporter(path)
        raise ImportError
    
    @staticmethod
    def add_load_path(path: str):
        if not path in EpicImporter.load_paths:
            EpicImporter.load_paths.append(path)

    @staticmethod
    def _resolve_file_interpreter(path):
        if not path.is_file():
            return None

        if not os.access(str(path), os.X_OK):
            return None

        with open(path) as f:
            first_line = f.readline()

        if first_line[0:2] != "#!":
            return None

        return first_line.split("/")[-1].split(" ")[-1].strip()
    
    def __init__(self, path):
        self.path = Path(path)

    def find_spec(self, fullname: str, path: str, target=None):
        unqualified_name = fullname.split(".")[-1]
        
        if path:
            script_path = ".d".join([path, unqualified_name])
        else:
            script_path = self.path / unqualified_name

        if not (interpreter := self._resolve_file_interpreter(script_path)):
            return None
        
        with open(script_path) as f:
            script_contents = f.read()
            docopt_spec = self._get_docopt_string(script_contents, interpreter)

            if not docopt_spec:
                return None
            
        m = ModuleSpec(
            fullname,
            self,
            origin=str(script_path),
            is_package=True,
            loader_state={
                "interpreter": interpreter,
                #"comment_char": comment_char,
                "contents": script_contents,
                "docopt": docopt_spec,
            },
        )
        m.has_location = True
        m.submodule_search_locations = [str(script_path) + ".d"]
        return m

    def create_module(self, spec: ModuleSpec):
        """
        Returning None uses the standard machinery for creating modules, but we want
        to include the documentation for docopt parsing.

        Any import-related module attributes (e.g. __spec__) are automatically set.
        """
        return ModuleType(spec.name, doc=spec.loader_state["docopt"])
    
    def exec_module(self, module: ModuleType) -> None:
        # Extend the module with an attribute to keep check of whether it's being
        # invoked itself or just used to invoke one of its subcommands.
        # module.leaf = True
        # if len(args):
        #     for location in module.__spec__.submodule_search_locations:
        #         if self._resolve_file_interpreter(Path(location + "/" + args[0])):
        #             # Trying to invoke a subcommand, so don't run the parent
        #             module.leaf = False
        #             return

        module._completions = functools.partial(
                self._completions, module
            )
        run = functools.partial(self._run, module)
        module.run = run

    @staticmethod
    def parse_docopt_string(doc):
        options = docopt.parse_defaults(doc)
        pattern = docopt.parse_pattern(docopt.formal_usage(docopt.printable_usage(doc)), options)
        pattern_options = set(pattern.flat(docopt.Option))
        for ao in pattern.flat(docopt.AnyOptions):
            doc_options = docopt.parse_defaults(doc)
            ao.children = list(set(doc_options) - pattern_options)
        return [a.name for a in pattern.flat()]

    @staticmethod
    def _completions(module, text, line, begidx, endidx):
        #print(f'\n Line: {line}\n Text: {text}\n begidx: {begidx}\n endidx: {endidx}\n')

        options = EpicImporter.parse_docopt_string(module.__spec__.loader_state["docopt"])
        # options = {o.lstrip("-").strip("<>") for o in options}
        
        completions = [o for o in options if o.startswith(text)]

        return completions

    @staticmethod
    def _run(module, args: List, main: bool = True):
        kwargs = docopt.docopt(module.__spec__.loader_state["docopt"], args, help=True)
        kwargs = {k.lstrip("-").strip("<>"): v for k, v in kwargs.items()}

        interpreter = module.__spec__.loader_state["interpreter"]
        
        if interpreter == "python":
            source_code = Path(module.__file__).read_text()
            module_name = module.__dict__['__name__']

            if main:
                module.__dict__["__name__"] = "__main__"
            prev_argv = sys.argv
            sys.argv = [module_name] + args

            exec(source_code, module.__dict__)
            
            if main:
                module.__dict__["__name__"] = module_name
            sys.argv = prev_argv
        elif interpreter == "bash":
            for k, v in kwargs.items():
                if isinstance(v, bool):
                    kwargs[k] = str(v).lower()
            kwargs["BASH_ENV"] = os.path.abspath("bash_env")
            if platform.system() == "Windows":
                shell = "C:\\Program Files\\Git\\bin\\bash.exe"
            else:
                shell = "/bin/bash"
            subprocess.run([shell, module.__file__], env=kwargs)
        else:
            raise ImportError("unsupported interpreter")
        
    
    def _get_docopt_string(self, script_contents: str, interpreter: str):
        '''
        If python, attempt to find the docstring in the typical __doc__
        style string.

        Otherwise, parse the script line by line reading the header
        comment section.
        '''
        if interpreter == "python":
            match = re.search(r'"""(.*?)"""', script_contents, re.DOTALL)
            if match:
                docopt_spec = match.group(1)
            else:
                return None
        else:
            script_lines = script_contents.split("\n")
            for line in script_lines[1:]:
                if line.find("Usage:") > 1:
                    comment_char = line[0]
                    break
            else:
                return None

            line_iter = iter(script_lines[1:])

            comment = re.compile(f"{comment_char}")

            docopt_spec = []
            try:
                while comment.match(line := next(line_iter)):
                    docopt_spec.append(line[2:])
            except StopIteration:
                pass

            if not docopt_spec:
                return None
            
            docopt_spec = "\n".join(docopt_spec).lstrip()

        docopt_spec = Template(docopt_spec, undefined=StrictUndefined).render(
            **self.help_tokens
        )

        return docopt_spec

sys.path_hooks.insert(0, EpicImporter.epic_importer_factory)