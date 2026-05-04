# control_client.py
import pygame
import socket
import time

PI_IP = '10.13.132.100'  # your Pi IP
PORT = 5000

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((PI_IP, PORT))

pygame.init()
pygame.joystick.init()

controller = pygame.joystick.Joystick(0)
controller.init()

while True:
    pygame.event.pump()

    throttle = -controller.get_axis(1)  # left stick Y
    steering = controller.get_axis(0)   # left stick X

    command = f"MOTOR {throttle:.2f} STEER {steering:.2f}"
    sock.sendall((command + "\n").encode())

    print(command)
    time.sleep(0.05)