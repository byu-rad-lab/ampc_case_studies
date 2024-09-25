import numpy as np
import matplotlib.pyplot as plt

# from examples.single_link_arm.plotter import Plotter
from examples.tabbed_plot_window import TabbedPlotWindow
from parsing import getParsedArgs_plot


def plot(load_dir: str):
    ## Params
    fontsize = 14
    figsize = (1000,800)
    img_types = ['svg', 'pdf']

    ## Load Data
    aff_all_costs = np.loadtxt(load_dir + 'aff_all_costs.txt')
    aff_min_costs = np.loadtxt(load_dir + 'aff_min_costs.txt')
    if aff_min_costs.ndim == 0:
        aff_min_costs = aff_min_costs.reshape(-1)
    aff_min_c_list = np.loadtxt(load_dir + 'aff_min_c_values.txt')
    if aff_min_c_list.ndim == 0:
        aff_min_c_list = aff_min_c_list.reshape(-1)

    lin_all_costs = np.loadtxt(load_dir + 'lin_all_costs.txt')
    lin_min_costs = np.loadtxt(load_dir + 'lin_min_costs.txt')
    if lin_min_costs.ndim == 0:
        lin_min_costs = lin_min_costs.reshape(-1)
    lin_min_c_list = np.loadtxt(load_dir + 'lin_min_c_values.txt')
    if lin_min_c_list.ndim == 0:
        lin_min_c_list = lin_min_c_list.reshape(-1)

    c_list = np.loadtxt(load_dir + 'c_list.txt')
    if c_list.ndim == 0:
        c_list = c_list.reshape(-1)
    k_list = np.loadtxt(load_dir + 'k_list.txt') + 1
    if k_list.ndim == 0:
        k_list = k_list.reshape(-1)


    print()
    min_idx = np.argmin(aff_min_costs)
    aff_min = aff_min_costs[min_idx]
    print(f'aff min cost: {aff_min} @ k = {k_list[min_idx]}, c = {aff_min_c_list[min_idx]:.1f}')
    print(f'aff nominal cost: {aff_min_costs[0]} @ k = {k_list[0]}, c = {aff_min_c_list[0]:.1f}')
    if min_idx != 0:
        print(f'aff k improvement: {100*(1-aff_min/aff_min_costs[0]):.2f}%')
    else:
        print(f'aff k improvement: 0%')
    print()

    min_idx = np.argmin(lin_min_costs)
    lin_min = lin_min_costs[min_idx]
    print(f'lin min cost: {lin_min} @ k = {k_list[min_idx]}, c = {lin_min_c_list[min_idx]:.1f}')
    print(f'lin nominal cost: {lin_min_costs[0]} @ k = {k_list[0]}, c = {lin_min_c_list[0]:.1f}')
    if min_idx != 0:
        print(f'lin k improvement: {100*(1-lin_min/lin_min_costs[0]):.2f}%')
    else:
        print(f'lin k improvement: 0%')
    print()

    print(f'aff improvement: {100*(1-aff_min/lin_min):.2f}%')

    if len(k_list) > 1:
        pw = TabbedPlotWindow('K-Analysis', figsize)#, fontsize)
        leg_fontsize = fontsize-4
        fig1,ax = plt.subplots(2)
        a: plt.Axes = ax[0]
        a.plot(k_list, aff_min_costs, label='aff')
        a.plot(k_list, lin_min_costs, label='lin')
        a.set_ylabel(r'$\int$cost', fontsize=fontsize)
        a.legend(fontsize=leg_fontsize)
        a: plt.Axes = ax[1]
        a.plot(k_list, aff_min_c_list, '.')
        a.set_xlabel('k', fontsize=fontsize)
        a.set_ylabel('c', fontsize=fontsize)
        pw.addTab('min costs', fig1)
        # a.legend(fontsize=leg_fontsize)
        fig1.tight_layout()

        fig2,ax = plt.subplots(2)
        a: plt.Axes = ax[0]
        for i,c in enumerate(c_list):
            a.plot(k_list, aff_all_costs.T[i], label=f'aff: {c = :.1f}')
            a.plot(k_list, lin_all_costs.T[i], label=f'lin: {c = :.1f}')
        # a.plot(k_list, all_costs)
        a.set_xlabel('k', fontsize=fontsize)
        a.set_ylabel(r'$\int$cost', fontsize=fontsize)
        if len(a.get_lines()) < 15:
            a.legend(fontsize=leg_fontsize)
        a: plt.Axes = ax[1]
        for i,k in enumerate(k_list):
            a.plot(c_list, aff_all_costs[i], label=f'aff: {k = }')
            a.plot(c_list, lin_all_costs[i], label=f'lin: {k = }')
        # a.plot(k_list, all_costs)
        a.set_xlabel('c', fontsize=fontsize)
        a.set_ylabel(r'$\int$cost', fontsize=fontsize)
        if len(a.get_lines()) < 15:
            a.legend(fontsize=leg_fontsize)
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
