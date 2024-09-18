import numpy as np

from examples.multirotor.plotter import Plotter
from parsing import getParsedArgs_plot


def plot(load_dir: str):
    ## Params
    deg = True
    legend = True
    fontsize = 14
    figsize = (1000,850)
    save = True
    img_types = ['svg', 'pdf']

    ## Load Data
    aff_ueq_all_costs = np.loadtxt(load_dir + 'aff_ueq_all_costs.txt')
    aff_ueq_min_costs = np.loadtxt(load_dir + 'aff_ueq_min_costs.txt')
    aff_ueq_min_c_list = np.loadtxt(load_dir + 'aff_ueq_min_c_values.txt')

    aff_uk_all_costs = np.loadtxt(load_dir + 'aff_uk_all_costs.txt')
    aff_uk_min_costs = np.loadtxt(load_dir + 'aff_uk_min_costs.txt')
    aff_uk_min_c_list = np.loadtxt(load_dir + 'aff_uk_min_c_values.txt')

    aff_xeq_all_costs = np.loadtxt(load_dir + 'aff_xeq_all_costs.txt')
    aff_xeq_min_costs = np.loadtxt(load_dir + 'aff_xeq_min_costs.txt')
    aff_xeq_min_c_list = np.loadtxt(load_dir + 'aff_xeq_min_c_values.txt')

    lin_all_costs = np.loadtxt(load_dir + 'lin_all_costs.txt')
    lin_min_costs = np.loadtxt(load_dir + 'lin_min_costs.txt')
    lin_min_c_list = np.loadtxt(load_dir + 'lin_min_c_values.txt')

    c_list = np.loadtxt(load_dir + 'c_list.txt')
    k_list = np.loadtxt(load_dir + 'k_list.txt') + 1

    print()
    min_idx = np.argmin(aff_ueq_min_costs)
    print(f'min cost (aff ueq): {aff_ueq_min_costs[min_idx]:.6f} @ k = {k_list[min_idx]:.0f}, c = {aff_ueq_min_c_list[min_idx]:.1f}')
    print(f'nominal cost (aff ueq): {aff_ueq_min_costs[0]:.6f} @ k = {k_list[0]:.0f}, c = {aff_ueq_min_c_list[0]:.1f}')
    if min_idx != 0:
        print(f'improvement (aff ueq): {100*(1-aff_ueq_min_costs[min_idx]/aff_ueq_min_costs[0]):.2f}%')
    else:
        print(f'improvement (aff ueq): 0%')

    print()
    min_idx = np.argmin(aff_uk_min_costs)
    print(f'min cost (aff uk): {aff_uk_min_costs[min_idx]:.6f} @ k = {k_list[min_idx]:.0f}, c = {aff_uk_min_c_list[min_idx]:.1f}')
    print(f'nominal cost (aff uk): {aff_uk_min_costs[0]:.6f} @ k = {k_list[0]:.0f}, c = {aff_uk_min_c_list[0]:.1f}')
    if min_idx != 0:
        print(f'improvement (aff uk): {100*(1-aff_uk_min_costs[min_idx]/aff_uk_min_costs[0]):.2f}%')
    else:
        print(f'improvement (aff uk): 0%')

    print()
    min_idx = np.argmin(aff_xeq_min_costs)
    print(f'min cost (aff xeq): {aff_xeq_min_costs[min_idx]:.6f} @ k = {k_list[min_idx]:.0f}, c = {aff_xeq_min_c_list[min_idx]:.1f}')
    print(f'nominal cost (aff xeq): {aff_xeq_min_costs[0]:.6f} @ k = {k_list[0]:.0f}, c = {aff_xeq_min_c_list[0]:.1f}')
    if min_idx != 0:
        print(f'improvement (aff xeq): {100*(1-aff_xeq_min_costs[min_idx]/aff_xeq_min_costs[0]):.2f}%')
    else:
        print(f'improvement (aff xeq): 0%')

    print()
    min_idx = np.argmin(lin_min_costs)
    print(f'min cost (lin): {lin_min_costs[min_idx]:.6f} @ k = {k_list[min_idx]:.0f}, c = {lin_min_c_list[min_idx]:.1f}')
    print(f'nominal cost (lin): {lin_min_costs[0]:.6f} @ k = {k_list[0]:.0f}, c = {lin_min_c_list[0]:.1f}')
    if min_idx != 0:
        print(f'improvement (lin): {100*(1-lin_min_costs[min_idx]/lin_min_costs[0]):.2f}%')
    else:
        print(f'improvement (lin): 0%')
    print()

    plotter = Plotter(legend, deg, fontsize, figsize)
    plotter.plotMinCosts(k_list, aff_ueq_min_costs, aff_ueq_min_c_list, label='aff (ueq)')
    plotter.plotMinCosts(k_list, aff_uk_min_costs, aff_uk_min_c_list, label='aff (uk)')
    plotter.plotMinCosts(k_list, aff_xeq_min_costs, aff_xeq_min_c_list, label='aff (xeq)')
    plotter.plotMinCosts(k_list, lin_min_costs, lin_min_c_list, label='lin')
    plotter.plotCvK(c_list, k_list, aff_ueq_all_costs)
    plotter.plotCvK(c_list, k_list, aff_uk_all_costs)
    plotter.plotCvK(c_list, k_list, aff_xeq_all_costs)
    plotter.plotCvK(c_list, k_list, lin_all_costs)
    plotter.show()
    for ext in img_types:
        plotter.savePlots(load_dir, image_type=ext)

    return


if __name__ == '__main__':
    load_dir = '/tmp/ampc24/multirotor/k_analysis/'
    desc = 'Plot k-analysis for multirotor'
    args = getParsedArgs_plot(load_dir, desc)
    plot(args.dir)
