# laptop_controller.py
import pygame
import socket
import time

PI_IP = "10.13.132.100"  
PORT = 5000

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((PI_IP, PORT))

pygame.init()
pygame.joystick.init()

controller = pygame.joystick.Joystick(0)
controller.init()
print("Controller connected.")
for i in range(controller.get_numaxes()):
    print(i, controller.get_axis(i))

while True:
    pygame.event.pump()

    throttle = -controller.get_axis(1)  # LEFT stick Y (frwdtoback: 1 to -1)
    steering = controller.get_axis(2)   # RIGHT stick X-axis (lefttoright:-1 to 1)
    command = f"MOTOR {throttle:.2f} STEER {steering:.2f}"
    sock.sendall((command + "\n").encode())

    print(command)
    time.sleep(0.1)