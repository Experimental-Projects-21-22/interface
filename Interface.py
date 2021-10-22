import serial


class Arduino:
    # Class to control serial ports of the Arduino
    def __init__(self, port, baud_rate=115200):
        self.ser = serial.Serial()
        self.ser.baudrate = baud_rate
        self.ser.port = port

    def write_serial(self, ser_input):
        # Writes to the serial port
        self.ser.write(ser_input)

    def read_serial(self):
        # Reads from the serial port till an EOL
        self.ser.readline()

    def read_bytes(self, ser_bytes):
        # Reads specified number of bytes from the serial port
        return self.ser.read(ser_bytes)

    def __del__(self):
        # Closes the serial port
        self.ser.close()


class Coincidence(Arduino):
    # Class to control the chips on the coincidence circuit
    def clear(self):
        # Clears the counter chips
        self.write_serial('CLEAR')

    def save(self):
        # Saves the counts to the registers
        self.write_serial('SAVE')

    def read(self):
        # Measures the counts from the registers
        self.write_serial('READ')
        return self.read_serial()

    def save_measure(self):
        # Saves the counts to the registers and immediately measures them
        self.save()
        self.read()
        return self.read_serial()


class Stepper(Arduino):
    # Class to control the stepper motor
    def rotate(self, angle):
        # Rotates the stepper motor to a specified angle
        pass
