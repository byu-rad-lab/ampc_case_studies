import numpy as np
import matplotlib.pyplot as plt

from examples.single_link_arm.plotter import Plotter
from examples.tabbed_plot_window import TabbedPlotWindow
from parsing import getParsedArgs_plot


def plot(load_dir: str):
    ## Params
    fontsize = 14
    figsize = (1000,800)
    save = True
    img_types = ['svg', 'pdf']

    ## Load Data
    all_costs = np.loadtxt(load_dir + 'all_costs.txt')
    min_costs = np.loadtxt(load_dir + 'min_costs.txt')
    min_c_list = np.loadtxt(load_dir + 'min_c_values.txt')
    c_list = np.loadtxt(load_dir + 'c_list.txt')
    k_list = np.loadtxt(load_dir + 'k_list.txt') + 1

    pw = TabbedPlotWindow('K-Analysis', figsize)#, fontsize)

    min_idx = np.argmin(min_costs)
    print(f'min cost: {min_costs[min_idx]} @ k = {k_list[min_idx]}, c = {min_c_list[min_idx]:.2f}')
    print(f'nominal cost: {min_costs[0]} @ k = {k_list[0]}, c = {min_c_list[0]:.2f}')
    if min_idx != 0:
        print(f'improvement: {100*(1-min_costs[min_idx]/min_costs[0]):.2f}%')
    else:
        print(f'improvement: 0%')

    fig1,ax = plt.subplots(2)
    a: plt.Axes = ax[0]
    a.plot(k_list, min_costs)
    a.set_ylabel(r'$\int$cost', fontsize=fontsize)
    a: plt.Axes = ax[1]
    a.plot(k_list, min_c_list, '.')
    a.set_xlabel('k', fontsize=fontsize)
    a.set_ylabel('c', fontsize=fontsize)
    pw.addTab('min costs', fig1)
    fig1.tight_layout()

    fig2,ax = plt.subplots(2)
    a: plt.Axes = ax[0]
    for i,c in enumerate(c_list):
        a.plot(k_list, all_costs.T[i], label=f'{c = :.1f}')
    # a.plot(k_list, all_costs)
    a.set_xlabel('k', fontsize=fontsize)
    a.set_ylabel(r'$\int$cost', fontsize=fontsize)
    a.legend(fontsize=fontsize-4)
    a: plt.Axes = ax[1]
    for i,k in enumerate(k_list):
        a.plot(c_list, all_costs[i], label=f'{k = }')
    # a.plot(k_list, all_costs)
    a.set_xlabel('c', fontsize=fontsize)
    a.set_ylabel(r'$\int$cost', fontsize=fontsize)
    if len(a.get_lines()) < 15:
        a.legend(fontsize=fontsize-4)
    fig2.tight_layout()
    pw.addTab('c vs k', fig2)

    pw.pause(0.1)
    fig1.tight_layout()
    fig2.tight_layout()
    pw.show()

    for ext in img_types:
        fig1.savefig(load_dir + 'min_costs.' + ext)
        fig2.savefig(load_dir + 'c_vs_k.' + ext)

    return


if __name__ == '__main__':
    load_dir = '/tmp/ampc24/arm/k_analysis/'
    desc = 'Plot k-analysis for single link arm'
    args = getParsedArgs_plot(load_dir, desc)
    plot(args.dir)
