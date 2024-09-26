import numpy as np

from examples.single_link_arm.plotter import Plotter
from parsing import getParsedArgs_plot


def plot(load_dir: str):
    ## Params
    deg = True
    legend = True
    fontsize = 14
    figsize = (1000,800)
    img_types = ['svg', 'pdf']

    ## Load Data
    time = np.loadtxt(load_dir + 'time.txt')
    costs = np.loadtxt(load_dir + 'costs.txt')
    aff_states = np.loadtxt(load_dir + 'aff_states.txt')
    lin_states = np.loadtxt(load_dir + 'lin_states.txt')
    xr_hist = np.loadtxt(load_dir + 'ref_states.txt')

    plotter = Plotter(time, legend, deg, fontsize, figsize)

    c_list = np.linspace(0, 1, len(costs[0]))
    plotter.plotCosts(c_list, costs[0], label='affinized')
    plotter.plotCosts(c_list, costs[1], '-.', label='linearized')

    idx = np.argmin(costs, axis=1)
    aff_mc = costs[0,idx[0]]
    lin_mc = costs[1,idx[1]]
    print(f'min aff cost = {aff_mc} at c = {c_list[idx[0]]:.1f}')
    print(f'min lin cost = {lin_mc} at c = {c_list[idx[1]]:.1f}')

    if idx[0] == 0:
        aff_improve = 0.0
    else:
        aff_improve = 1 - aff_mc/costs[0,0]
    if idx[1] == 0:
        lin_improve = 0.0
    else:
        lin_improve = 1 - lin_mc/costs[1,0]
    print(f'aff improvement: {aff_improve*100:.2f}%')
    print(f'lin improvement: {lin_improve*100:.2f}%')

    diff = aff_mc - lin_mc
    if np.abs(diff) < 1e-6:
        better = 'aff/lin'
        imp = 0.0
    elif diff <= 0:
        better = 'aff'
        imp = 1 - aff_mc / lin_mc
    else:
        better = 'lin'
        imp = 1 - lin_mc / aff_mc
    print(f'best_method: {better} by {imp*100:.2f}%')

    aff_states = aff_states.reshape(len(c_list),-1,2)
    lin_states = lin_states.reshape(len(c_list),-1,2)
    for i,c in enumerate(c_list):
        plotter.plotStateLine(aff_states[i], label=f'aff: {c = :.1f}')
        plotter.plotStateLine(lin_states[i], '-.', label=f'lin: {c = :.1f}')
    plotter.plotStateLine(xr_hist, 'r--', label='ref')

    plotter.show()

    for ext in img_types:
        plotter.savePlots(load_dir, image_type=ext)
    return


if __name__ == '__main__':
    load_dir = '/tmp/ampc24/arm/lin_vs_aff'
    desc = 'Plot linearization vs affinization comparison for single link arm'
    args = getParsedArgs_plot(load_dir, desc)
    plot(args.dir)
