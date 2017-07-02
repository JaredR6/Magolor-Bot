# !/bin/bash

timestamp() {
    date +"[%T]"
}

((ret_code=0))
> output.log
while [[ $ret_code == 0 ]]; do
    python magolor.py > output.log
    ret_code=$?
    if [[ $ret_code == 0 ]]; then
        echo $(timestamp) "Bot is restarting." > output.log
    else
        echo $(timestamp) "Bot has shut down." > output.log
    fi
done

