# This variable will hold the command to be executed instead of the one the user entered
typeset -g PREPROCESSED_CMD=""
# This variable will hold the original command entered by the user
typeset -g ORIGINAL_CMD=""
# This flag indicates if the command should be suppressed
typeset -g SUPPRESS_CMD=false
# This var stores the current chat history
typeset -g CUR_CHAT_HISTORY=""

echo -e "\033[1;32mHi, I'm Axon!\033[0m"
echo -e "Run commands like you usually would (ls, cd Home, etc.)"
echo -e "Talk to me with ? (?Explain how the ls command works in Linux)"
echo -e "Ask me to perform actions with : (:Make a file called test.txt)"
echo -e "Set \$ENABLE_CMDCHK to 'true' to check your commands before you run them"

# Redefine the accept-line widget to preprocess the command
_preprocess_cmd_accept_line() {
    local cwd_pth="${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/plugins/axon-terminal"
    if [[ $PYTHON_PATH ]]; then
        python_pth=$PYTHON_PATH
    else
        python_pth="python3"
    fi

    case "$BUFFER" in
        "?"*|":"* ) 
          :
          ;;
      *)
        SUPPRESS_CMD=false
        zle .accept-line
        return
        ;;
    esac

    # Capture the current buffer (command)
    local cmd="$BUFFER"
    echo ""

    # Get output of cmd.py
    intelli_out=$($python_pth $cwd_pth/cmd.py "$cmd" 2>&1 > >(cat -))
    exit_status=$?

    if [[ $intelli_out == *"Traceback"* ]]; then
        echo -e "\033[1;31mAxon Error:\033[0m"
        echo $intelli_out
        echo "\033[1;31mFalling back to normal shell! (Disable Axon with 'omz plugin disable axon-terminal')\033[0m"
        echo "---------------------------"
        SUPPRESS_CMD=false
        zle .accept-line
        return
    fi

    if [[ $exit_status -eq 0 ]]; then
        if [[ $ENABLE_CMDCHK == 'true' ]]; then
            echo -e "$intelli_out"
            echo "Are you sure you want to execute? (Y/n): "
            read should_exec < /dev/tty
        else
            should_exec='y'
        fi
        if [[ "${should_exec:l}" == 'n' ]]; then
            PREPROCESSED_CMD="echo"
            ORIGINAL_CMD=$BUFFER
            BUFFER=""
            SUPPRESS_CMD=true
        else
            PREPROCESSED_CMD=$cmd
            ORIGINAL_CMD=$cmd
            BUFFER=""
            SUPPRESS_CMD=true
        fi
    elif [[ $exit_status -eq 1 ]]; then
        CUR_CHAT_HISTORY="$CUR_CHAT_HISTORY!!!<>?user"$'\n'"$cmd"
        CUR_CHAT_HISTORY=$($python_pth $cwd_pth/cmd.py --chat "$CUR_CHAT_HISTORY")
        parts=("${(@s/!!!<>?assistant/)CUR_CHAT_HISTORY}")
        last_part="${parts[-1]}"
        echo -e "$last_part"
        PREPROCESSED_CMD="echo"
        ORIGINAL_CMD=$BUFFER
        BUFFER=""
        SUPPRESS_CMD=true
    elif [[ $exit_status -eq 2 ]]; then
        echo -e "$intelli_out\n\n---------------------------"
        echo "This code is the planned action. Are you sure you want to execute? (Y/n): "
        read should_exec < /dev/tty
        if [[ "${should_exec:l}" != 'n' ]]; then
            echo "---------------------------"
            echo $intelli_out > .agent_action.py
            output=$($python_pth .agent_action.py)
            echo $output
            echo "---------------------------"
            echo "Code execution complete."
            rm .agent_action.py
        fi
        PREPROCESSED_CMD="echo"
        ORIGINAL_CMD=$BUFFER
        BUFFER=""
        SUPPRESS_CMD=true
    else
        echo "Invalid exit status! PYTHON_PATH could be incorrect."
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
