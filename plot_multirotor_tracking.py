import numpy as np

from case_studies.multirotor.plotter import Plotter
from parsing import getParsedArgs_plot


def plot(load_dir: str):
    ## Params
    deg = True
    legend = True
    fontsize = 14
    figsize = (1000,800)
    img_types = ['svg', 'pdf']

    ## Load Data
    k_list = np.loadtxt(load_dir + 'k_list.txt')
    c_list = np.loadtxt(load_dir + 'c_list.txt')
    with open(load_dir + 'method_list.txt', 'r') as f:
        method_list = f.read().splitlines()

    time = np.loadtxt(load_dir + 'time.txt')
    costs = np.loadtxt(load_dir + 'costs.txt')
    xtraj_hist = np.loadtxt(load_dir + 'states.txt').reshape(len(c_list),-1,9)
    xr_hist = np.loadtxt(load_dir + 'ref_states.txt')
    utraj_hist = np.loadtxt(load_dir + 'inputs.txt').reshape(len(c_list),-1,4)

    min_idx = np.argmin(costs)
    print(f'Min cost: {costs[min_idx]} at c = {c_list[min_idx]}, k = {k_list[min_idx]}')

    plotter = Plotter(legend, deg, fontsize, figsize)
    for i,(c,k,method) in enumerate(zip(c_list, k_list, method_list)):
        plotter.plotStateLine(time, xtraj_hist[i], label=f'{method}: {c = }, {k = }')
        plotter.plotInputLine(time, utraj_hist[i], label=f'{method}: {c = }, {k = }')
        print(f'cost ({method}) @ {c = }, {k = }: {costs[i]}')
    plotter.plotStateLine(time, xr_hist, 'r--', label='ref')
    plotter.show()

    for ext in img_types:
        plotter.savePlots(load_dir, image_type=ext)
    return


if __name__ == '__main__':
    load_dir = '/tmp/ampc24/multirotor/tracking/'
    desc = 'Plot selected tracking for multirotor'
    args = getParsedArgs_plot(load_dir, desc)
    plot(args.dir)
