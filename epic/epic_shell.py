import os
import re
import sys
import cmd
import shlex
import platform
import subprocess
import importlib.util
from pathlib import Path
from types import ModuleType
from typing import List, Dict
from docopt import docopt, DocoptExit

from .epic_importer import EpicImporter


class EpicShell(cmd.Cmd):
    prompt: str = 'epic> '
    _mods: Dict[str, ModuleType]
    _os_is_windows: bool
    _windows_bash_shell: str

    def __init__(self, plugin_dirs: List[str], 
                 windows_bash_shell="C:\\Program Files\\Git\\bin\\bash.exe") -> None:
        super().__init__()

        self._mods = dict()
        self._os_is_windows = (platform.system() == "Windows")
        self._windows_bash_shell = windows_bash_shell

        for path in plugin_dirs:
            sys.path.append(path)
            EpicImporter.add_load_path(path)
        self.load_plugins(plugin_dirs)
    
    def check_permissions(self, filepath):
        if self._os_is_windows:
            permissions = self.get_file_permissions(filepath)
            owner = self.get_file_owner(filepath)

            # Check if the third character in the permissions string is 'x', indicating execute permission for the owner
            if permissions[2] == 'x' and owner == os.getlogin():
                return True
            # Check if the ninth character in the permissions string is 'x', indicating execute permission for others
            elif permissions[9] == 'x':
                return True
            else:
                return False
        else:
            return os.access(filepath, os.X_OK)
        
    def get_file_permissions(self, filepath):
        try:
            # Run the `stat` command to get file permissions
            result = subprocess.run(['stat', '-c', '%A', filepath], capture_output=True, text=True, check=True)
            return result.stdout.strip()  # Strip any leading/trailing whitespace
        except subprocess.CalledProcessError as e:
            print(f"Error: {e}")
            return None
    
    def get_file_owner(self, filepath):
        try:
            # Run the `stat` command to get file own
            result = subprocess.run(['stat', '-c', '%U', filepath], capture_output=True, text=True, check=True)
            return result.stdout.strip()  # Strip any leading/trailing whitespace
        except subprocess.CalledProcessError as e:
            print(f"Error: {e}")
            return None
        
    def load_plugins(self, plugin_dirs):
        for path in plugin_dirs:
            
        #     for root, dirs, files in os.walk(path):
        #         for f in files:
        #             file_path = os.path.join(root, f)
        #             if self.check_permissions(file_path):
        #                 if root[len(path):]:
        #                     submodule_dirs = root[len(path)+1:].split('\\')
        #                     submod_names = [mod_name[:-2] if mod_name.endswith('.d') else mod_name for mod_name in submodule_dirs]
        #                     package_name = f"{'.'.join(submod_names)}.{f}"
        #                     self.load_plugin(package_name)
        #         pass

            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                if os.path.isfile(item_path) and os.access(item_path, os.X_OK):
                    self.load_plugin(item)
        

    def load_plugin(self, plugin_file: str):
        print(f"Loading {plugin_file}...")
        self._mods[plugin_file] = importlib.import_module(plugin_file)
        command_name = os.path.basename(plugin_file).replace('_', '-').split('.')[0]
        setattr(self.__class__, 'do_' + command_name, lambda self, args: self.execute_plugin(self._mods[plugin_file], args))
        setattr(self.__class__, 'help_' + command_name, lambda self: print(self._mods[plugin_file].__doc__))

    def execute_plugin(self, mod: ModuleType, args):
        argv = shlex.split(args)
        try:
            mod.run(argv)
        except DocoptExit as de:
            print(de)
            return

    def do_exit(self, args):
        """Exit the shell"""
        return True

    def default(self, line: str):
        try:
            cmd, *args = shlex.split(line)
            mod = importlib.import_module(cmd)
            mod.run(args, True)
        except:
            print(f"Error: cmd {cmd} not found.")

    def do_shell(self, line):
        try:
            # Use shlex.split to properly handle quoted strings
            parts = shlex.split(line)
            
            if not parts:
                return  # Handle empty input
            
            if parts[0] == "cd":
                # Join the rest of the parts to get the directory path
                if len(parts) > 1:
                    os.chdir(" ".join(parts[1:]))
                else:
                    print("cd: missing argument")
            else:
                # Use subprocess.run to execute other commands
                subprocess.run(parts, check=True)
        except FileNotFoundError as e:
            print(f'Error: Command {line} not found')
        except OSError as e:
            print(f'Error: OSError when attempting to run {line}. \n{e}')
        except subprocess.CalledProcessError as e:
            print(f'Error: Command {line} failed with return code {e.returncode}')