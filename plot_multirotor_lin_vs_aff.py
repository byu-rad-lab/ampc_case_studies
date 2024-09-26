import numpy as np

from examples.multirotor.plotter import Plotter
from parsing import getParsedArgs_plot


def plot(load_dir: str):
    ## Params
    deg = True
    legend = True
    fontsize = 14
    figsize = (1000,850)
    img_types = ['svg', 'pdf']

    ## Load Data
    time = np.loadtxt(load_dir + 'time.txt')
    xr_hist = np.loadtxt(load_dir + 'ref_states.txt')

    aff_uk_costs = np.loadtxt(load_dir + 'aff_uk_costs.txt')
    aff_uk_states = np.loadtxt(load_dir + 'aff_uk_states.txt')
    aff_uk_inputs = np.loadtxt(load_dir + 'aff_uk_inputs.txt')
    aff_uk_solve_times = np.loadtxt(load_dir + 'aff_uk_solve_times.txt')

    aff_ueq_costs = np.loadtxt(load_dir + 'aff_ueq_costs.txt')
    aff_ueq_states = np.loadtxt(load_dir + 'aff_ueq_states.txt')
    aff_ueq_inputs = np.loadtxt(load_dir + 'aff_ueq_inputs.txt')
    aff_ueq_solve_times = np.loadtxt(load_dir + 'aff_ueq_solve_times.txt')

    aff_xeq_costs = np.loadtxt(load_dir + 'aff_xeq_costs.txt')
    aff_xeq_states = np.loadtxt(load_dir + 'aff_xeq_states.txt')
    aff_xeq_inputs = np.loadtxt(load_dir + 'aff_xeq_inputs.txt')
    aff_xeq_solve_times = np.loadtxt(load_dir + 'aff_xeq_solve_times.txt')

    lin_costs = np.loadtxt(load_dir + 'lin_costs.txt')
    lin_states = np.loadtxt(load_dir + 'lin_states.txt')
    lin_inputs = np.loadtxt(load_dir + 'lin_inputs.txt')
    lin_solve_times = np.loadtxt(load_dir + 'lin_solve_times.txt')

    plotter = Plotter(legend, deg, fontsize, figsize)

    num_c = len(aff_uk_costs)
    c_list = np.linspace(0, 1, num_c)
    plotter.plotCosts(c_list, aff_uk_costs, label='aff (uk)')
    plotter.plotCosts(c_list, aff_ueq_costs, label='aff (ueq)')
    plotter.plotCosts(c_list, aff_xeq_costs, label='aff (xeq)')
    plotter.plotCosts(c_list, lin_costs, '-.', label='lin')

    aff_uk_idx = np.argmin(aff_uk_costs)
    aff_ueq_idx = np.argmin(aff_ueq_costs)
    aff_xeq_idx = np.argmin(aff_xeq_costs)
    lin_idx = np.argmin(lin_costs)
    aff_uk_mc = aff_uk_costs[aff_uk_idx]
    aff_ueq_mc = aff_ueq_costs[aff_ueq_idx]
    aff_xeq_mc = aff_xeq_costs[aff_xeq_idx]
    lin_mc = lin_costs[lin_idx]
    aff_uk_c = c_list[aff_uk_idx]
    aff_ueq_c = c_list[aff_ueq_idx]
    aff_xeq_c = c_list[aff_xeq_idx]
    lin_c = c_list[lin_idx]

    aff_mc = np.array([aff_uk_mc, aff_ueq_mc, aff_xeq_mc])
    aff_c0 = np.array([aff_uk_costs[0], aff_ueq_costs[0], aff_xeq_costs[0]])
    aff_c_improve = (1 - aff_mc/aff_c0) * 100
    lin_c_improve = (1 - lin_mc/lin_costs[0]) * 100

    print(f'min aff (uk) cost = {aff_uk_mc} @ c = {aff_uk_c:.1f} ({aff_c_improve[0]:.2f}% better than c=0)')
    print(f'min aff (ueq) cost = {aff_ueq_mc} @ c = {aff_ueq_c:.1f} ({aff_c_improve[1]:.2f}% better than c=0)')
    print(f'min aff (xeq) cost = {aff_xeq_mc} @ c = {aff_xeq_c:.1f} ({aff_c_improve[2]:.2f}% better than c=0)')
    print(f'min lin cost = {lin_mc} @ c = {lin_c:.1f} ({lin_c_improve:.2f}% better than c=0)')

    idx = np.argmin(aff_mc)
    aff_improve = (1 - aff_mc[idx] / lin_mc) * 100
    if idx == 0:
        best = 'aff (uk)'
    elif idx == 1:
        best = 'aff (ueq)'
    elif idx == 2:
        best = 'aff (xeq)'
    print(f'Improvement from affinization: {best} by {aff_improve:.2f}%')

    aff_uk_states = aff_uk_states.reshape(num_c,-1,9)
    aff_ueq_states = aff_ueq_states.reshape(num_c,-1,9)
    aff_xeq_states = aff_xeq_states.reshape(num_c,-1,9)
    lin_states = lin_states.reshape(num_c,-1,9)
    aff_uk_inputs = aff_uk_inputs.reshape(num_c,-1,4)
    aff_ueq_inputs = aff_ueq_inputs.reshape(num_c,-1,4)
    aff_xeq_inputs = aff_xeq_inputs.reshape(num_c,-1,4)
    lin_inputs = lin_inputs.reshape(num_c,-1,4)
    for i,c in enumerate(c_list):
        plotter.plotStateLine(time, aff_uk_states[i], label=f'aff (uk): {c = :.1f}')
        plotter.plotStateLine(time, aff_ueq_states[i], label=f'aff (ueq): {c = :.1f}')
        plotter.plotStateLine(time, aff_xeq_states[i], label=f'aff (xeq): {c = :.1f}')
        plotter.plotStateLine(time, lin_states[i], '-.', label=f'lin: {c = :.1f}')
        plotter.plotInputLine(time, aff_uk_inputs[i], label=f'aff (uk): {c = :.1f}')
        plotter.plotInputLine(time, aff_ueq_inputs[i], label=f'aff (ueq): {c = :.1f}')
        plotter.plotInputLine(time, aff_xeq_inputs[i], label=f'aff (xeq): {c = :.1f}')
        plotter.plotInputLine(time, lin_inputs[i], '-.', label=f'lin: {c = :.1f}')
        plotter.plotSolveTimes(time, aff_uk_solve_times[i], label=f'aff (uk): {c = :.1f}')
        plotter.plotSolveTimes(time, aff_ueq_solve_times[i], label=f'aff (ueq): {c = :.1f}')
        plotter.plotSolveTimes(time, aff_xeq_solve_times[i], label=f'aff (xeq): {c = :.1f}')
        plotter.plotSolveTimes(time, lin_solve_times[i], '-.', label=f'lin: {c = :.1f}')
    plotter.plotStateLine(time, xr_hist, 'r--', label='ref')

    plotter.show()

    for ext in img_types:
        plotter.savePlots(load_dir, image_type=ext)
    return


if __name__ == '__main__':
    load_dir = '/tmp/ampc24/multirotor/lin_vs_aff'
    desc = 'Plot linearization vs affinization comparison for multirotor'
    args = getParsedArgs_plot(load_dir, desc)
    plot(args.dir)
