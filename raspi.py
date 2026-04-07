import serial
import time

ser = serial.Serial('dev/ttyACM0', 115200, timeoout = 1.0)
time.sleep(3.0)
ser.reset_input_buffer()
print("serial okay.")