# laptop_test_client.py
import socket

PI_IP = "10.13.132.100"  # replace with your Pi IP
PORT = 5000

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((PI_IP, PORT))

while True:
    msg = input("Send: ")
    sock.sendall((msg + "\n").encode())