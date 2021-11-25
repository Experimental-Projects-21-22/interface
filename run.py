from interface import CoincidenceCircuit, Interferometer
from measure.schemes.g2 import G2

coincidence_circuit = CoincidenceCircuit(baudrate=115200, port='/dev/cu.usbmodem14301')
interferometer = Interferometer(baudrate=115200, port='/dev/cu.usbmodem14301')

scheme = G2(coincidence_circuit=coincidence_circuit, interferometer=interferometer)

if __name__ == '__main__':
    data = scheme()
    scheme.analyse(data)
