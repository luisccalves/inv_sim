
from numpy import genfromtxt
import numba
import numpy as np

from distributions import *
import matplotlib.pyplot as plt


@numba.njit
def one_item_process(mean_lead_time, std_lead_time, mean_demand, std_demand, rol, roq, time_run):

    num_ordered = 0
    inventory_level_list = []
    time_level = []
    inventory_level = rol + roq
    while time_run > 0:
        inventory_level_list.append(inventory_level)
        time_level.append(time_run)

        demand = normal_distribution(mean_demand, std_demand)
        inventory_level = inventory_level - demand
        if demand >= inventory_level:
            inventory_level = 0

        if inventory_level <= rol and num_ordered == 0:

            num_ordered = rol + 1 - inventory_level
            num_ordered = (num_ordered/(rol+1))*roq
            lead_time = int(normal_distribution(mean_lead_time, std_lead_time))
            for i in range(lead_time):
                inventory_level_list.append(0)

            inventory_level += num_ordered
            num_ordered = 0
        time_run -= 1
    return inventory_level_list


path = "G:\\Book1.csv"
my_data = genfromtxt(path, delimiter=',')


@numba.njit
def run_montecarlo(df):
    avg_inventory_levels = []
    avg_levels = [0.]

    for i in range(df.shape[0]):
        _temp = df[i:i+1]
        z = one_item_process(_temp[0][1], _temp[0][2], _temp[0]
                             [3], _temp[0][4], _temp[0][5], _temp[0][6], _temp[0][7])
        avg_inventory_levels.append(z)

    for lvl in avg_inventory_levels:
        sums = 0
        cnt = 0
        for i in lvl:
            sums = sums + i
        for i in lvl:
            cnt += 1

        avg_levels.append(sums/cnt)

    return avg_levels


z = np.array(run_montecarlo(my_data))
plt.plot(np.arange(len(z[:1000])), z[:1000])
plt.show()
