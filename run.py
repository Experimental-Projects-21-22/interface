from interface import CoincidenceCircuit, Interferometer
from measure.schemes.window_shift_effect import WindowShiftEffect

coincidence_circuit = CoincidenceCircuit(baudrate=115200, port='/dev/cu.usbmodem14301')
interferometer = Interferometer(baudrate=115200, port='/dev/cu.usbmodem14301')

if __name__ == '__main__':
    scheme_A = WindowShiftEffect(coincidence_circuit=coincidence_circuit, interferometer=interferometer)
    scheme_B = WindowShiftEffect(coincidence_circuit=coincidence_circuit, interferometer=interferometer, shift_A=False)

    data = scheme_A()
    scheme_A.analyse(data, scheme_A.metadata)

    data = scheme_B()
    scheme_B.analyse(data, scheme_B.metadata)
    # scheme = SingleRun(coincidence_circuit=coincidence_circuit, interferometer=interferometer)
    # data = scheme()
    # scheme.analyse(data, scheme.metadata)
