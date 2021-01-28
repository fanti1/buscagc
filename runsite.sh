sudo chmod 775 -R /etc/letsencrypt/archive
sleep 5
sudo python3 /home/gamersclub/redirect.py &
sleep 5
sudo python3 /home/gamersclub/app.py > errorlog.txt 2>&1 &
