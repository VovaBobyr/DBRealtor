#!/usr/bin/env bash

sudo apt -y update

# Install Python PIP
sudo apt -y install python3-pip

#sudo apt -y update
sudo apt -y install mysql-server

# restart mysql
sudo /etc/init.d/mysql restart

### secure the mysql installation

# set root password
sudo /usr/bin/mysqladmin -u root password 'password'

# allow remote access
mysql -u root -ppassword -e "GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' IDENTIFIED BY 'password' WITH GRANT OPTION;"

# drop the anonymous users
mysql -u root -ppassword -e "DROP USER ''@'localhost';"
mysql -u root -ppassword -e "DROP USER ''@'$(hostname)';"

# drop the demo database
mysql -u root -ppassword -e "DROP DATABASE test;"

# flush
mysql -u root -ppassword -e "FLUSH PRIVILEGES;"

# restart
sudo service mysqld restart

# set to autostart
sudo chkconfig mysqld on

#folders creation and provide permisions
mkdir -p "/opt/dbrealtor"
mkdir -p "/opt/dbrealtor/temp/"
mkdir -p "/opt/dbrealtor/Logs/"