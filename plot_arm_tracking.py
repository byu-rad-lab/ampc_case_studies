import numpy as np

from case_studies.single_link_arm.plotter import Plotter
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

    time = np.loadtxt(load_dir + 'time.txt')
    costs = np.loadtxt(load_dir + 'costs.txt')
    xtraj_hist = np.loadtxt(load_dir + 'states.txt').reshape(len(c_list),-1,2)
    xr_hist = np.loadtxt(load_dir + 'ref_states.txt')
    utraj_hist = np.loadtxt(load_dir + 'inputs.txt').reshape(len(c_list),-1)

    plotter = Plotter(time, legend, deg, fontsize, figsize)

    for i,k in enumerate(k_list):
        plotter.plotStateLine(xtraj_hist[i], label=f'{k = }')
        plotter.plotInputLine(utraj_hist[i], label=f'{k = }')
    plotter.plotStateLine(xr_hist, 'r--', label='ref')

    min_idx = np.argmin(costs)
    print(f'Min cost: {costs[min_idx]} @ k = {k_list[min_idx]}, c = {c_list[min_idx]:.1f}')

    plotter.show()

    for ext in img_types:
        plotter.savePlots(load_dir, image_type=ext)
    return


if __name__ == '__main__':
    load_dir = '/tmp/ampc24/arm/tracking/'
    desc = 'Plot selected tracking for single link arm'
    args = getParsedArgs_plot(load_dir, desc)
    plot(args.dir)
