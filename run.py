from matplotlib import pyplot as plt

from interface import CoincidenceCircuit, Interferometer
from measure.g2 import G2

coincidence_circuit = CoincidenceCircuit(baudrate=115200, port='/dev/cu.usbmodem14301')
interferometer = Interferometer(baudrate=115200, port='/dev/cu.usbmodem14301')

scheme = G2(coincidence_circuit=coincidence_circuit, interferometer=interferometer)

if __name__ == '__main__':
    data = scheme.run()

    delay = data[0]
    counts1 = data[1]
    counts2 = data[2]
    coincidences = data[3]

    g2 = coincidences / (counts1 * counts2)

    plt.plot(delay, g2)
    plt.ylabel('g2')
    plt.xlabel('delay')
    plt.show()
