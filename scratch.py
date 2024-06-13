def load_plugins(self, plugin_dirs):
    for path in plugin_dirs:
        for root, dirs, files in os.walk(path):
            pass

def load_plugins(self, plugin_dirs:List[str]):
    for dir in plugin_dirs:
        if os.path.exists(dir):
            for plugin_file in glob.glob(os.path.join(dir, '*')):
                if os.access(plugin_file, os.X_OK):  # Check if file is executable
                    self.load_plugin(plugin_file)

def load_plugin(self, plugin_file: str):
    with open(plugin_file, 'r') as f:
        first_line = f.readline().strip()
        content = f.read()

    if first_line.startswith('#!/usr/bin/env python'):
        match = re.search(r'"""(.*?)"""', content, re.DOTALL)
        if match:
            docopt_string = match.group(1)
            usage_match = re.search(r'Usage:\n((?:\s+.+\n?)*)', docopt_string, re.DOTALL)
            if usage_match:
                usage = usage_match.group(1).strip()
                command_name = os.path.basename(plugin_file).replace('_', '-').split('.')[0]
                setattr(self.__class__, 'do_' + command_name, lambda self, args, docopt_string=docopt_string: self.execute_python_plugin(command_name, args, docopt_string))
                setattr(self.__class__, 'help_' + command_name, lambda self, docopt_string=docopt_string: print(command_name + ':', docopt_string))
                setattr(self.__class__, 'complete_' + command_name, lambda self, text, line, begidx, endidx, docopt_string=docopt_string: self.complete_plugin_command(text, line, begidx, endidx, docopt_string=docopt_string))
                print(f"Added command: {command_name}")
            else:
                print(f"Error: Could not find usage string in plugin: {plugin_file}")
        else:
            print(f"Error: Could not find docopt string in plugin: {plugin_file}")

    elif first_line.startswith('#!/bin/bash') or first_line.startswith('#!/usr/bin/env bash'):
        command_name = os.path.basename(plugin_file).replace('_', '-').split('.')[0]
        setattr(self, 'do_' + command_name, lambda args: self.execute_bash_plugin(plugin_file, args))
        print(f"Added command: {command_name}")

    else:
        print(f"Error: Unknown script type for plugin: {plugin_file}")

def execute_python_plugin(self, command_name, args, docopt_string):
    try:
        args = docopt(docopt_string, argv=args.split())
    except DocoptExit as de:
        print(de)
        return
    
    module_name = f"libexec.{command_name.replace('-', '_')}"
    spec = importlib.util.spec_from_file_location(module_name, f'libexec/{command_name.replace("-", "_")}.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.main(args)

def complete_plugin_command(self, text, line, begidx, endidx, docopt_string):
    usage_section = re.search(r'Usage:\n(.*?)(\n\n|\n\s*\w+:|$)', docopt_string, re.DOTALL)
    options_section = re.search(r'Options:\n(.*?)(\n\n|\n\s*\w+:|$)', docopt_string, re.DOTALL)
    arg_section = re.search(r'Arguments:\n(.*?)(\n\n|\n\s*\w+:|$)', docopt_string, re.DOTALL)

    commands = re.findall(r'\s+(\S+)', usage_section.group(1))
    options = [s.lstrip('-') for s in re.findall(r'(--\w+)', options_section.group(1))]
    completions = commands + options
    print(completions)
    if not text:
        return completions
    else:
        return [comp for comp in completions if comp.startswith(text)]

def execute_bash_plugin(self, plugin_file, args):
    if self._os_is_windows:
        subprocess.run([self._windows_bash_shell,
                        plugin_file,
                        args])
    else:
        subprocess.run(f"{plugin_file} {args}")