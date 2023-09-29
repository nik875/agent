# This variable will hold the command to be executed instead of the one the user entered
typeset -g PREPROCESSED_CMD=""
# This variable will hold the original command entered by the user
typeset -g ORIGINAL_CMD=""
# This flag indicates if the command should be suppressed
typeset -g SUPPRESS_CMD=false

# Redefine the accept-line widget to preprocess the command
_preprocess_cmd_accept_line() {
    # Capture the current buffer (command)
    local cmd="$BUFFER"

    # For demonstration, if user enters "hello", we want to execute "echo Hello, World!" without showing it
    if [[ $cmd == "hello" ]]; then
        PREPROCESSED_CMD="echo Hello, World!"
        ORIGINAL_CMD="$BUFFER"
        # Clear the command buffer to prevent its execution
        BUFFER=""
        SUPPRESS_CMD=true
    else
        SUPPRESS_CMD=false
    fi

    zle .accept-line  # Call the original accept-line widget
}

# Use our custom accept-line in place of the default one
zle -N accept-line _preprocess_cmd_accept_line

# Add a hook for executing the preprocessed command just before the command prompt
precmd() {
    if [[ -n "$PREPROCESSED_CMD" ]]; then
        eval "$PREPROCESSED_CMD"
        # Simulate the user input by printing the prompt and then the original command
        echo -ne "$(print -P "$PS1")"
        echo "$ORIGINAL_CMD"
        PREPROCESSED_CMD=""
        ORIGINAL_CMD=""
    fi
}

# If SUPPRESS_CMD is true, we clear the command just before it executes to suppress it
preexec() {
    if $SUPPRESS_CMD; then
        BUFFER=""
    fi
}
