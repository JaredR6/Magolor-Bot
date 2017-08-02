# !/bin/bash
mv token.txt Webster-Bot/token.txt
cd Webster-Bot
git pull

timestamp() {
        date +"[%T]"
}

((ret_code=0))
while [[ $ret_code == 0 ]]; do
        python3 magolor.py >> output.log
        ret_code=$?
        if [[ ret_code == 0 ]]; then
                echo $(timestamp) "Bot is restarting." >> output.log
                git pull
        else
                echo $(timestamp) "Bot has shut down." >> output.log
        fi
done
