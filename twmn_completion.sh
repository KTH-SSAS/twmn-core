# Completion function
_my_command_completion() {
    # Get the entire command line being completed
    local command_line="${COMP_WORDS[*]}"
    
    # Call the Python script with the current command line
    local IFS=$'\n'
    COMPREPLY=($("${TWMN_HOME}/twmn_completion.py" "$command_line"))
}

# Register the completion function for the command 'my_command'
complete -F _my_command_completion twmn.py
