import matplotlib.pyplot as plt
import numpy as np
from typing import List


def create_and_save_plots(input_technology: str, list_pp: List[str], ptx_technology, list_ptx, a, sens_ptx, sens_infra):

    # a graphic is created from the power production profile
    if input_technology in list_pp and ptx_technology in list_ptx:
        plt.figure(0)
        plt.plot('time', 'pv_production', data=a, marker='', color='skyblue', linewidth=1)
        plt.plot('time', 'wind_production', data=a, marker='', color='olive', linewidth=1)
        plt.legend()
        plt.savefig('static/power_production_plot.png')
        plt.close()

    plt.figure(1)
    for name, values in sens_ptx.items():
       plt.plot(values, label=name)
    plt.xticks(np.arange(0,21,2.5),['0%','25%','50%','75%','100%','125%','150%','175%','200%'])
    plt.ylabel('Net Present Value [€]')
    plt.xlabel('Change')
    plt.legend()
    plt.savefig("static/sensitivity_plot.png")
    plt.close()
    plt.figure(2)
    for name, values in sens_infra.items():
        plt.plot(values, label=name)
    plt.ylabel('Net Present Value [€]')
    plt.xlabel('Change')
    plt.legend()
    plt.savefig("static/sensitivity_infra_plot.png")
    plt.close()