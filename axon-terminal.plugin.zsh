# This variable will hold the command to be executed instead of the one the user entered
typeset -g PREPROCESSED_CMD=""
# This variable will hold the original command entered by the user
typeset -g ORIGINAL_CMD=""
# This flag indicates if the command should be suppressed
typeset -g SUPPRESS_CMD=false

typeset -g SESS_ID=""
typeset -g DISABLE_AXON=false
typeset -g DEBUG=false
typeset -g CWD_PATH="${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/plugins/axon-terminal"

alias disable-axon="export DISABLE_AXON=true && echo 'Axon Terminal disabled.'"
alias enable-axon="export DISABLE_AXON=false && echo 'Axon Terminal enabled.'"

local git_response=$(git -C $CWD_PATH pull)
if [[ $git_response == *"Already up to date."* ]]; then :; else echo "Axon Terminal Updated!"; fi

_err() {
    echo -e "\033[1;31mAxon Error:\033[0m"
    echo "SERVER COMMUNICATION FAILED, FALLING BACK TO NORMAL SHELL"
    if [[ $DEBUG == true ]]; then
        echo $1
    fi
}

set_axon_api_key() {
    creds_file="${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/axon-terminal/creds.py"
    if [[ ! -f $creds_file ]]; then
        echo "Enter Axon Terminal API Key: "
        read api_key
        echo "API_KEY = '$api_key'" > $creds_file

        echo -e "\033[1;32mHi, I'm Axon!\033[0m"
        echo -e "Run commands like you usually would (ls, cd Home, etc.)"
        echo -e "Talk to me with ? (?Explain how the ls command works in Linux)"
        echo -e "Ask me to perform actions with : (:Make a file called test.txt)"
        echo -e "Set \$ENABLE_CMDCHK to 'true' to check your commands before you run them"
    fi
    if [[ $PYTHON_PATH ]]; then
        python_path=$PYTHON_PATH
    else
        python_path="python3"
    fi
    SESS_ID=$($python_path $CWD_PATH/cmd.py session_start)
    if [[ $? -ne 0 ]]; then
        _err $SESS_ID
        SESS_ID="No Session ID"
        DISABLE_AXON=true
    fi
}
set_axon_api_key

_suppress_cmd() {
    PREPROCESSED_CMD=":"
    ORIGINAL_CMD=$BUFFER
    BUFFER=""
    SUPPRESS_CMD=true
}

# Redefine the accept-line widget to preprocess the command
_preprocess_cmd_accept_line() {
    if [[ $DISABLE_AXON == true ]]; then
        SUPPRESS_CMD=false
        zle .accept-line
        return
    fi
    if [[ $PYTHON_PATH ]]; then
        python_path=$PYTHON_PATH
    else
        python_path="python3"
    fi
    
    echo ""  # Prevent overwriting of current line

    if [[ $BUFFER == "?"* ]]; then
        # Calls cmd.py on given buffer with first character removed
        response=$($python_path $CWD_PATH/cmd.py "chat" $SESS_ID ${BUFFER[2,${#BUFFER}]})
        if [[ $? -ne 0 ]]; then
            _err $response
            DISABLE_AXON=true
            return
        fi
        echo -e $response
    elif [[ $BUFFER == ":"* ]]; then
        # Calls cmd.py on given buffer with first character removed
        response=$($python_path $CWD_PATH/cmd.py "generate" $SESS_ID ${BUFFER[2,${#BUFFER}]})
        if [[ $? -ne 0 ]]; then
            _err $response
            DISABLE_AXON=true
            return
        fi
        echo -e "$response\n\n---------------------------"
        echo "This code is the planned action. Are you sure you want to execute? (Y/n): "
        read should_exec < /dev/tty
        if [[ "${should_exec:l}" != 'n' ]]; then
            echo "---------------------------"
            echo $response > .agent_action.py
            output=$($python_path .agent_action.py)
            # Send back result of code execution
            $python_path $CWD_PATH/cmd.py "output" $SESS_ID $output
            echo $output
            echo "---------------------------"
            echo "Code execution complete."
            rm .agent_action.py
        fi
    else  # If the command doesn't start with either ? or :, just run as a command
        SUPPRESS_CMD=false
        response=$($python_path $CWD_PATH/cmd.py "command" $SESS_ID "$BUFFER")
        if [[ $? -ne 0 ]]; then
            _err $response
            DISABLE_AXON=true
        fi
        zle .accept-line
        return
    fi

    _suppress_cmd  # Assuming it wasn't just a command, suppress it so that it doesn't run
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
