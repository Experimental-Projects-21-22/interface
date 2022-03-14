"""
Written by:
    Julian van Doorn <j.c.b.van.doorn@umail.leidenuniv.nl>
"""

import numpy as np

from utils.delays import DelayLines

# Load the last/best file of the WindowShift
file = '/Users/douweremmelts/PycharmProjects/interface_new/data/WindowShiftEffect/2022-01-18-10:04:02.npz'

a = np.load(file)
data = a['data']

index_max = np.argmax(data[4])

if a['shift_A']:
    shift_C = 'CA'
    shift_W = 'WA'
    fixed_C = 'CB'
    fixed_W = 'WB'
else:
    shift_C = 'CB'
    shift_W = 'WB'
    fixed_C = 'CA'
    fixed_W = 'WA'

print(f'Max coincidence counts at index = {index_max}')
print(f'Optimal steps for {shift_C} = {data[0, index_max]}')
print(f'Optimal steps for {shift_W} = {data[1, index_max]}')
print(f'Optimal steps for {fixed_C} = {a["fixed_delay_C"]}')
print(f'Optimal steps for {fixed_W} ='
      f' {DelayLines.WB.calculate_steps(DelayLines.CB.calculate_delays(a["fixed_delay_C"]) + a["window_size"])}')
