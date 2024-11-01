GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[0;33m'
NC='\033[0m'

printf """
${BLUE}

░█████╗░██████╗░██╗███╗░░░███╗███████╗████████╗░██████╗░
██╔══██╗██╔══██╗██║████╗░████║██╔════╝╚══██╔══╝██╔════╝░
██║░░╚═╝██████╔╝██║██╔████╔██║█████╗░░░░░██║░░░██║░░██╗░
██║░░██╗██╔══██╗██║██║╚██╔╝██║██╔══╝░░░░░██║░░░██║░░╚██╗
╚█████╔╝██║░░██║██║██║░╚═╝░██║███████╗░░░██║░░░╚██████╔╝
░╚════╝░╚═╝░░╚═╝╚═╝╚═╝░░░░░╚═╝╚══════╝░░░╚═╝░░░░╚═════╝░

		    Установка...${NC}
"""


apt update
apt upgrade -y

apt install -y htop git nginx build-essential libssl-dev libffi-dev
apt install -y python3-pip python3-dev python3-setuptools python3-venv
apt install -y screenfetch neofetch python-is-python3
pip install "uvicorn[standard]"
pip install gunicorn uvicorn
pip install -r requirements.txt


python -m venv .venv
source .venv/bin/activate
pip install wheel
pip install gunicorn uvicorn
pip install -r requirements.txt
deactivate

printf """
${GREEN}
Дополнения установлены!
Установка SSL сертификата...
${NC}
"""

set "$(hostname -i)"
read -p "Введите ваш домен (пр. telegram.com): " SITE
touch /etc/nginx/conf.d/CrimeTG.conf
echo """
server {
    server_name $SITE $1;
    listen 80;

    location / {
        proxy_pass http://127.0.0.1:8000;
    }
}
""" > /etc/nginx/conf.d/CrimeTG.conf

sudo apt install snapd
sudo snap install core; sudo snap refresh core
sudo snap install --classic certbot
sudo ln -s /snap/bin/certbot /usr/bin/certbot
sudo certbot --nginx
nginx -s reload

printf "${YELLOW}Если выше ошибка (красный текст) останови процесс: CTRL+C${NC} \n"

read -p "Если ошибок нет и SSL получен, нажми Enter чтобы продолжить"

printf """
${GREEN}
Добавляю и запускаю скрипт в фоновом процессе...
${NC}
"""


touch /lib/systemd/system/crimetg.service
echo """
[Unit]
Description=CrimeTG
After=network.target

[Service]
Type=idle
Restart=always
RestartSec=5
User=root
WorkingDirectory=/var/www/html
ExecStart=/usr/local/bin/uvicorn main:app --reload

[Install]
WantedBy=multi-user.target
""" > /lib/systemd/system/crimetg.service

touch /lib/systemd/system/dashboard.service
echo """
[Unit]
Description=Dashboard
After=network.target

[Service]
Type=idle
Restart=always
RestartSec=5
User=root
WorkingDirectory=/var/www/html
ExecStart=/var/www/html/.venv/bin/python /var/www/html/dashboard.py
""" > /lib/systemd/system/dashboard.service

touch /lib/systemd/system/hello.service
echo """
[Unit]
Description=Hello
After=network.target

[Service]
Type=idle
Restart=always
RestartSec=5
User=root
WorkingDirectory=/var/www/html
ExecStart=/var/www/html/.venv/bin/python /var/www/html/hello.py
""" > /lib/systemd/system/hello.service


sudo systemctl daemon-reload 
sudo systemctl enable crimetg.service
sudo systemctl start crimetg.service
sudo systemctl enable dashboard.service 
sudo systemctl start dashboard.service 
sudo systemctl enable hello.service 
sudo systemctl start hello.service

printf """
${BLUE}

░█████╗░██████╗░██╗███╗░░░███╗███████╗████████╗░██████╗░
██╔══██╗██╔══██╗██║████╗░████║██╔════╝╚══██╔══╝██╔════╝░
██║░░╚═╝██████╔╝██║██╔████╔██║█████╗░░░░░██║░░░██║░░██╗░
██║░░██╗██╔══██╗██║██║╚██╔╝██║██╔══╝░░░░░██║░░░██║░░╚██╗
╚█████╔╝██║░░██║██║██║░╚═╝░██║███████╗░░░██║░░░╚██████╔╝
░╚════╝░╚═╝░░╚═╝╚═╝╚═╝░░░░░╚═╝╚══════╝░░░╚═╝░░░░╚═════╝░
${NC}
		  ${GREEN}Установлен и запущен!${NC}
	 ${GREEN}Убедись что конфиг правильно заполнен!${NC}
	          ${GREEN}ᴡɪᴛʜ ♥ ʙʏ ɪɴᴛᴇʀᴘᴏʟ${NC}
"""
