# **π robot main program**
Deploy that on your raspberry, then install requirements and launch main.py  
To connect to DualShock use the ds4drv  
You can add main.py to startup via crontab:  
```
crontab -e
```
Then choose your editor and add several lines to the end of a file  
```
@reboot ds4drv
@reboot /usr/bin/python3 path_to_file/main.py
```