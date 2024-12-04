from typing import List
from epic.epic_shell import EpicShell

class TwmnShell(EpicShell):
    def __init__(self, command_dirs: List[str]) -> None:
        super().__init__(command_dirs)
        self.prompt = 'twmn> '

if __name__ == '__main__':
    shell = TwmnShell(command_dirs=['libexec'])
    shell.cmdloop()
