# !/bin/bash
TOKEN="PLACE TOKEN HERE"
yum -y upgrade
yum -y install python35 python35-pip git
python35 -m pip install -U discord.py mcstaus

# https://stackoverflow.com/a/16811212
git init .
git remote add -t /* -f origin https://github.com/PKAnti/Webster-Bot.git
git checkout master

echo $TOKEN > token.txt

timestamp() {
    date +"[%T]"
}

((ret_code=0))
while [[ $ret_code == 1 ]]; do
    python35 magolor.py > output.log
    ret_code=$?
    if [[ $ret_code == 1 ]]; then
        echo $(timestamp) "Bot is restarting." > output.log
        git pull
    else
        echo $(timestamp) "Bot has shut down." > output.log
    fi
done

sudo halt
