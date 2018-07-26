# !/bin/bash
mv token.txt Magolor-Bot/token.txt
cd Magolor-Bot
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
                git pull >> output.log
        else
                echo $(timestamp) "Bot has shut down." >> output.log
        fi
done
