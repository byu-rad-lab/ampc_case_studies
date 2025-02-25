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
    k_list = np.load(load_dir + 'k_list.npy')
    # c_list = np.load(load_dir + 'c_list.npy')
    c_list = np.linspace(0, 1, 11)

    time = np.load(load_dir + 'time.npy')
    costs = np.load(load_dir + 'costs.npy')
    xtraj_hist = np.load(load_dir + 'states.npy').reshape(len(c_list),-1,2)
    xr_hist = np.load(load_dir + 'ref_states.npy')
    utraj_hist = np.load(load_dir + 'inputs.npy').reshape(len(c_list),-1)

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
