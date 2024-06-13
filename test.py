import re

doc = '''
Test.

Usage:
  my_program command1 [options] <arg>
  my_program command2 --option
  my_program command3 | my_program alt_command3
  my_program command4 <arg> [--optional]
  my_program command5 [--opt1 | --opt2]
  my_program command6 (subcommand1 | subcommand2)

Options:
  -h --help     Show this screen.
  --version     Show version.

OtherSection:
  This is another section.
'''

usage_section = re.search(r'Usage:\n(.*?)(\n\n|\n\s*\w+:|$)', doc, re.DOTALL)
arg_section = re.search(r'Arguments:\n(.*?)(\n\n|\n\s*\w+:|$)', doc, re.DOTALL)
options_section = re.search(r'Options:\n(.*?)(\n\n|\n\s*\w+:|$)', doc, re.DOTALL)

print(usage_section.group(1))
print('-' * 20)
print(options_section.group(1))
print('-' * 20)
#print(arg_section.group(1))

commands = []
options = []

if usage_section:
    # Extract commands and arguments from the usage section
    commands = re.findall(r'^\s*(my_program\s+.*?)$', usage_section.group(1), re.MULTILINE)
    cleaned_commands = []
    for command in commands:
        # Split command by '|' to handle alternatives
        variations = re.split(r'\s*\|\s*', command)
        for variation in variations:
            # Remove positional arguments < > and docopt special characters [] | ( )
            cleaned_command = re.sub(r'[\[\]\(\)]', '', variation)  # Remove [], (), and the spaces around them
            cleaned_command = re.sub(r'<[^>]+>', '', cleaned_command)  # Remove positional arguments inside <>
            cleaned_command = re.sub(r'\s+', ' ', cleaned_command).strip()  # Clean up extra spaces and trim
            cleaned_commands.append(cleaned_command)

if options_section:
    # Extract options from the options section
    options = re.findall(r'(--\w+)', options_section.group(1))

completions = commands + options

print(cleaned_commands)
print(options)