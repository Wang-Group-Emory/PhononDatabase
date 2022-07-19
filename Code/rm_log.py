# This program finds all of the "myLog" files and removes them from choosen directory
from options import rootdir
import os

file_to_rm = "mylog"
data_path = f'{rootdir}\\Raw_data'
log_count = 0

for subdir, dirs, files in os.walk(data_path):
    for file in files:
        if file == file_to_rm:
            log_count += 1
            try:
                if os.path.exists(os.path.join(subdir,file)):
                    os.remove(os.path.join(subdir,file))
            except:
                print("fail")

print(f'{log_count} mylogs removed')
