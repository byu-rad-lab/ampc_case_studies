import numpy as np

from examples.single_link_arm.plotter import Plotter, PlotWindow
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
    aff_inputs = np.loadtxt(load_dir + 'aff_inputs.txt')
    lin_inputs = np.loadtxt(load_dir + 'lin_inputs.txt')
    lin_states = np.loadtxt(load_dir + 'lin_states.txt')
    xr_hist = np.loadtxt(load_dir + 'ref_states.txt')

    app = Plotter(fontsize)
    pw = PlotWindow(time, legend, deg, fontsize, figsize)
    pw2 = PlotWindow(time, legend, deg, fontsize, figsize)

    c_list = np.linspace(0, 1, len(costs[0]))
    pw.plotCosts(c_list, costs[0], label='affinized')
    pw.plotCosts(c_list, costs[1], '-.', label='linearized')

    idx = np.argmin(costs, axis=1)
    aff_mc = costs[0,idx[0]]
    lin_mc = costs[1,idx[1]]

    aff_improve = (1 - aff_mc/costs[0,0]) * 100
    lin_improve = (1 - lin_mc/costs[1,0]) * 100

    print(f'min aff cost = {aff_mc} @ c = {c_list[idx[0]]:.1f} ({aff_improve:.2f}% better than c=0)')
    print(f'min lin cost = {lin_mc} at c = {c_list[idx[1]]:.1f} ({lin_improve:.2f}% better than c=0)')

    aff_improve = 1 - aff_mc / lin_mc
    print(f'aff improvement: {aff_improve:.2f}%')

    aff_states = aff_states.reshape(len(c_list),-1,2)
    aff_inputs = aff_inputs.reshape(len(c_list),-1,1)
    lin_states = lin_states.reshape(len(c_list),-1,2)
    lin_inputs = lin_inputs.reshape(len(c_list),-1,1)
    for i,c in enumerate(c_list):
        pw.plotStateLine(aff_states[i], label=f'aff: {c = :.1f}')
        pw.plotStateLine(lin_states[i], '-.', label=f'lin: {c = :.1f}')
    pw.plotStateLine(xr_hist, 'r--', label='ref')

    app.addWindow(pw)

    pw2.plotStateLine(time, aff_states[idx[0]], label=f'aff (uk): c = {c_list[idx[0]]:.1f}')
    pw2.plotStateLine(time, lin_states[idx[1]], '-.', label=f'lin: c = {c_list[idx[1]]:.1f}')

    pw2.plotInputLine(time, aff_inputs[aff_uk_idx], label=f'aff (uk): c = {c_list[aff_uk_idx]:.1f}')
    pw2.plotInputLine(time, lin_inputs[lin_idx], '-.', label=f'lin: c = {c_list[lin_idx]:.1f}')

    pw2.plotStateLine(time, xr_hist, 'r--', label='ref')

    app.addWindow(pw2)
    app.show()

    print('Saving plots...')
    for ext in img_types:
        pw.savePlots(load_dir, image_type=ext)
    print('Plots saved')

    return


if __name__ == '__main__':
    load_dir = '/tmp/ampc24/arm/lin_vs_aff'
    desc = 'Plot linearization vs affinization comparison for single link arm'
    args = getParsedArgs_plot(load_dir, desc)
    plot(args.dir)
