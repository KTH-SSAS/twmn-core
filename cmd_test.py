import cmd

class MyCLI(cmd.Cmd):
    intro = 'Welcome to MyCLI. Type help or ? to list commands.\n'
    prompt = '(mycli) '
    use_rawinput = True

    def do_greet(self, person):
        """Greet a person."""
        if person:
            print(f"Hello, {person}!")
        else:
            print("Hello!")

    def complete_greet(self, text, line, begidx, endidx):
        """Auto-completion for the greet command."""
        # List of people to greet for demonstration purposes
        people = ['Alice', 'Bob', 'Charlie', 'Diana']
        print(f"\n{text}\n")
        if not text:
            completions = people[:]
        else:
            completions = [p for p in people if p.startswith(text)]
        return completions

    def do_exit(self, arg):
        """Exit the CLI."""
        print("Goodbye!")
        return True

if __name__ == '__main__':
    MyCLI().cmdloop()
