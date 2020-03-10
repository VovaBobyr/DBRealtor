import datetime
import time

script_date_start_timestamp = datetime.datetime.now()
time.sleep(10)
script_date_finish_timestamp = datetime.datetime.now()

total_time_timestamp = script_date_finish_timestamp - script_date_start_timestamp
print('Total script time running: ' + str(total_time_timestamp)) #.strftime("%Y-%m-%d %H:%M:%S")