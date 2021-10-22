import serial

class Arduino:
    # Class to control serial ports of the Arduino
    def __init__(self, port, baud_rate=115200):
        self.ser = serial.Serial()
        self.ser.baudrate = baud_rate
        self.ser.port = port

    def write(self, ser_input):
        # Writes to the serial port
        self.ser.write(ser_input)

    def read(self):
        # Reads from the serial port till an EOL
        self.ser.readline()

    def read_bytes(self, ser_bytes):
        # Reads specified number of bytes from the serial port
        return self.ser.read(ser_bytes)

    def close(self):
        # Closes the serial port
        self.ser.close()


class Delays(Arduino):
    # Class to control the delay lines
    def set_delay(self, line, delay_time):
        # Sets the specified delay time to the delay line
        pass


class Counters(Arduino):
    # Class to control the counter chips
    def clear(self):
        # Clears the counter chips
        self.write('c')

    def save(self):
        # Saves the counts to the registers
        self.write('s')

    def measure(self):
        # Measures the counts from the registers
        self.write('m')
        return self.read()

    def save_measure(self):
        # Saves the counts to the registers and immediately measures them
        self.write('sm')
        return self.read()


class Stepper(Arduino):
    # Class to control the stepper motor
    def rotate(self, angle):
        # Rotates the stepper motor to a specified angle
        pass
