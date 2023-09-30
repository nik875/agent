# This variable will hold the command to be executed instead of the one the user entered
typeset -g PREPROCESSED_CMD=""
# This variable will hold the original command entered by the user
typeset -g ORIGINAL_CMD=""
# This flag indicates if the command should be suppressed
typeset -g SUPPRESS_CMD=false

_welcome_message() {
    echo "Welcome to IntelliShell!"
    echo -e "\nRun commands like you usually would (ls, cd Home, etc.)"
    echo -e "\nChat with your personal Agent with ? (?Explain how the ls command works in Linux)"
    echo -e "\nInstruct your agent to perform actions with : (:Make a file called test.txt)"
}

if (( ! ${precmd_functions[(Ie)_welcome_message]} )); then
    precmd_functions+=(_welcome_message)
fi

# Redefine the accept-line widget to preprocess the command
_preprocess_cmd_accept_line() {
    local cwd_pth="$HOME/.oh-my-zsh/custom/plugins/intellishell"
    # Capture the current buffer (command)
    local cmd="$BUFFER"

    # Get output of cmd.py
    intelli_out=$($cwd_pth/env/bin/python $cwd_pth/cmd.py "$cmd")
    exit_status=$?

    if [[ $exit_status -eq 0 ]]; then
        echo -e "\n$intelli_out"
        echo "Are you sure you want to execute? (Y/n): "
        read should_exec < /dev/tty
        if [[ "${should_exec:l}" == 'n' ]]; then
            PREPROCESSED_CMD="echo"
            ORIGINAL_CMD=$BUFFER
            BUFFER=""
            SUPPRESS_CMD=true
        else
            SUPPRESS_CMD=false
        fi
    elif [[ $exit_status -eq 1 ]]; then
        echo -e "\n$intelli_out"
        PREPROCESSED_CMD="echo"
        ORIGINAL_CMD=$BUFFER
        BUFFER=""
        SUPPRESS_CMD=true
    elif [[ $exit_status -eq 2 ]]; then
        echo -e "\n$intelli_out\n\n---------------------------"
        echo "This code is the planned action. Are you sure you want to execute? (Y/n): "
        read should_exec < /dev/tty
        if [[ "${should_exec:l}" != 'n' ]]; then
            echo "---------------------------"
            echo $intelli_out > .agent_action.py
            output=$($cwd_pth/env/bin/python .agent_action.py)
            echo $output
            echo "---------------------------"
            echo "Code execution complete."
            rm .agent_action.py
        fi
        PREPROCESSED_CMD="echo"
        ORIGINAL_CMD=$BUFFER
        BUFFER=""
        SUPPRESS_CMD=true
    fi

    zle .accept-line  # Call the original accept-line widget
}

# Use our custom accept-line in place of the default one
zle -N accept-line _preprocess_cmd_accept_line

# Add a hook for executing the preprocessed command just before the command prompt
precmd() {
    if [[ -n "$PREPROCESSED_CMD" ]]; then
        eval "$PREPROCESSED_CMD"
        print -s $ORIGINAL_CMD
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
