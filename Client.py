"""
TCP client porgram to request operations from the server (GUI_Main.py).
Once the connection is built:
    if the client send 'light on' and the light brightness(0~255), the GUI will turn on the light;
    if the client send 'light off', the GUI will turn off the light;
    if the client sends 'compute', the GUI will compute the dof6;
    if the client sends 'save', the GUI will save the log file;
    if the client sends 'disconnect', the GUI will disconnect from the client.

Author: Siqi Dai
"""


import socket


def Client():
    HOST = 'localhost'  # server's hostname or IP address (currently we use localhost)
    PORT = 65432        # port used by the server
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((HOST, PORT))
        except:
            pass
        message = input("\nMessage to server? (light on/light off/compute/save/disconnect) ")
        s.send(message.encode())
        if message.encode() == b'disconnect':
            print("Client exits.")
            data = s.recv(1024)
            print(data.decode())
            exit()
        elif message.encode() == b'light on':
            while True:
                message2 = input("Brightness (0~255): ")  # let the user set light brightness
                if 0 <= int(message2.encode()) <= 255: break  # check if the user input is valid
            s.send(message2.encode())
            data = s.recv(1024)
            print(data.decode())
            s.close()
            Client()
        elif message.encode() == b'light off':
            data = s.recv(1024)
            print(data.decode())
            s.close()
            Client()
        elif message.encode() == b'compute':
            message2 = input("Which car model? ")
            s.send(message2.encode())
            data = s.recv(1024)
            print(data.decode())
            s.close()
            Client()
        elif message.encode() == b'save':
            data = s.recv(1024)
            print(data.decode())
            s.close()
            Client()
        else:
            print('Invalid input. Enter again.')
            Client()


Client()
