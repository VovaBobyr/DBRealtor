https://dev.mysql.com/downloads/file/?id=480091 - JDBC driver for connecting to mySQL for example from SQL Developer Ora tool

https://stackoverflow.com/questions/14058453/making-python-loggers-output-all-messages-to-stdout-in-addition-to-log-file

https://web.archive.org/web/20100629172923/http://uswaretech.com/blog/2009/02/automatically-backup-mysql-database-to-amazon-s3-using-django-python-script/

Screen:
    Run:
    screen -ls
    ls -laR /var/run/screen/
    screen -list
    Start:
    screen -S prodej python3 /opt/dbrealtor/WebScraper/SrealityScanner_Byty_Prodej.py
    Re-attache:
    screen -r

Backup:
  mysqldump -u root -p dbrealtor --default-character-set=utf8mb4 --result-file=C:\Tmp\DBBackup\dbrealtor_20190314_extended_columns.sql
  Linux:
    e

Restore form backup DB:
mysql -u root -p < C:\Learning\Python\DBRealtor\SQL\dbrealtor_20190314.sql
mysql -u root -p < C:\Tmp\DBBackup\dbrealtor_20190320.sql
Linux:
mysql -u root -p < /opt/dbrealtor/Backups/dbrealtor_20190314_extended_columns.sql

Usefull tools:
HeidiSQL tool for management MySQL
ConEmu - for cmd and Putty

Logic fo SRealitySceanner:
TBC

Administration:
- if script fails some chrome/chromedriver processes are not closed:
Closing:
pkill chrome

Plan on 2019-03-05
1. Related to history:
+ Adding columns:
Date_Open - date when object added to DB
Date_Update - this column will be updated in next days where script is running in case 'SKIPP'
Date_Close - will be updated on the end of script for these rows where Date_Update is earler than script start.
Active - field with values:
    O - just opened
    U - updated - means that object already at least 2nd day
    C - closed
History statistic than can be calculated by following way:
- TargetDay between Date_Open and Date_Close

2. Create column 'object_id' -> and realize correct inserting
+ updated old rows


3. Update to reflect:
+ Date_Open - date when object added to DB
+ Date_Update - this column will be updated in next days where script is running in case 'SKIPP'
+ Date_Close - will be updated on the end of script for these rows where Date_Update is earler than script start.
+ Final update - all records that were not updated (SKIPPED or new INSERTED) set as CLOSED


4. Fix:
+ fixed all times, covert to one format: %Y-%m-%d %H:%M:%S
+ fix sub-region in case it doesn't exist (not Praha, Brno...)

5. Feature:
+ Byty_Pronajem

6. Check ticks (on some fields are tick, not text)

7. Fix:
- fix reconnect on each new Page for Prodej

8.
+ Add dataloadlogid for each loading
+ Fix closing - to close only not-closed items!

9. Domy:
+ Prodej
+ Pronajem

10. Improvement fails: 
- As sometimes Pages with 20 items fails - need to collect all fails and try to re-load it one more time at the end:

