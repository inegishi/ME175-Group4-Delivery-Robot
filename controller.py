import pygame
import serial
import time

arduino = serial.Serial('COM4', 115200, timeout=1)
time.sleep(2)

pygame.init()
pygame.joystick.init()

controller = pygame.joystick.Joystick(0)
controller.init()

while True:
    pygame.event.pump()
    left_x = -controller.get_axis(0)
    print(f"{left_x:.3f}")
    arduino.write(f"{left_x:.3f}\n".encode())
    time.sleep(0.1)