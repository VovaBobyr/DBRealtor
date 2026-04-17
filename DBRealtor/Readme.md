GOAL:
This project covers collecting statistics for different Real Estate portals and reflect statistics in grafs.
Portal exists in time series manner, so it is going to collect statistic time to time and shown it in real time.
Statistic is in accumulative amount.

First phase is to integrate sreality.cz into portal. That includes WebScrapping all types of real estate objects.

# To start using project
## Windows-CentOS VM
Implied having installed Vagrant and VirtulBox (part of install will be later, image based on CentOS65)
Clonning and run VM:
```
git clone https://github.com/VovaBobyr/DBRealtor.git
cd DBRealtor\Envpreparation
vagrant up
vagrant ssh
```
### Install ChromeDriver
```
sudo wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list' \
    && apt-get update && apt-get install -y --no-install-recommends \
      google-chrome-unstable \
    && apt-get purge --auto-remove \
    && rm -rf /tmp/* /var/lib/apt/lists/* \
    && rm -rf /usr/bin/google-chrome* /opt/google/chrome-unstable
```
### Alternative way to install Chrome and chromedriver (
```
LATEST_VERSION=$(curl -s https://chromedriver.storage.googleapis.com/LATEST_RELEASE) && wget -O /tmp/chromedriver.zip https://chromedriver.storage.googleapis.com/$LATEST_VERSION/chromedriver_linux64.zip && sudo unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/
```
### Install Chrome
```
curl https://intoli.com/install-google-chrome.sh | bash
```
### Creation dbrealtor DB
default passwort for root "password"
```
cd DBRealtor/Envpreparation
mysql -u root -p < dbrealtor_inicial_creation.sql
sudo mkdir -p /opt/dbrealtor/Backups
sudo su
echo "password" > /opt/dbrealtor/Backups/info.txt
exit
```
### Install Python modules
```
pip3 install selenium
pip3 install mysql.connector
```
### Run Scrapper
```
python3 ~/DBRealtor/WebScraper/SrealityScanner_Byty_Pronajem.py
```

