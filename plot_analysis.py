import numpy as np
from tabulate import tabulate

import case_studies.single_link_arm.plotter as arm_plotter
import case_studies.block_beam.plotter as beam_plotter
import case_studies.cart_pendulum.plotter as pendulum_plotter
import case_studies.multirotor.plotter as multirotor_plotter
from parsing import getParsedArgs_plot
import constants as C


def main():
    default_load_dir = '/tmp/ampc_analysis/'
    desc = 'Plot linearization vs affinization comparison'
    args = getParsedArgs_plot(default_load_dir, desc)
    plot(args.dir, args.headless)


def plot(load_dir: str, headless: bool=False):
    ## Params
    fontsize = 14
    img_types = ['svg', 'pdf']

    ## Load Data
    time = np.load(load_dir + 'time.npy')
    x_hist = np.load(load_dir + 'states.npz')
    u_hist = np.load(load_dir + 'inputs.npz')
    costs = np.load(load_dir + 'costs.npz')
    solve_times = np.load(load_dir + 'solve_times.npz')

    xr_hist = np.load(load_dir + 'ref_states.npy')
    Q = np.load(load_dir + 'Q.npy')
    print(f'Q = {Q.tolist()}')
    k_list = np.load(load_dir + 'k_list.npy')

    with open(load_dir + 'system.txt', 'r') as f:
        system = f.readline()
    print(f'System: {system}')

    if system == 'arm':
        app = arm_plotter.Plotter(fontsize)
        n,m = 2,1
    elif system == 'blockbeam':
        app = beam_plotter.Plotter(fontsize)
        n,m = 4,1
    elif system == 'pendulum':
        app = pendulum_plotter.Plotter(fontsize)
        n,m = 4,1
    elif system == 'multirotor':
        app = multirotor_plotter.Plotter(fontsize)
        n,m = 9, 4
    else:
        raise ValueError(f'Unknown system: {system}')

    ######## START: C Analysis ########
    pw = app.createPlotWindow('C Analysis')
    num_c = costs[C.ANCHOR_POINTS[0]].shape[1]
    c_list = np.linspace(0, 1, num_c)
    k = 0

    best_c_idx = np.empty(len(C.ANCHOR_POINTS), dtype=int)
    best_c = np.empty(len(C.ANCHOR_POINTS))
    best_aff_cost = np.empty(len(C.ANCHOR_POINTS))
    nom_cost = np.empty(len(C.ANCHOR_POINTS))
    c_improvement = np.empty(len(C.ANCHOR_POINTS))
    data = []

    for i,p in enumerate(C.ANCHOR_POINTS):
        pw.plotCosts(c_list, costs[p][k], C.LINE_STYLES[i], label=p)
        best_c_idx[i] = np.argmin(costs[p][k])
        best_c[i] = c_list[best_c_idx[i]]
        best_aff_cost[i] = costs[p][k,best_c_idx[i]]
        nom_cost[i] = costs[p][k,0]
        c_improvement[i] = (1 - best_aff_cost[i] / nom_cost[i]) * 100
        data.append([p, best_aff_cost[i], best_c[i], c_improvement[i]])

    formatted_data = [[row[0], f'{row[1]:.6f}', f'{row[2]:.1f}', f'{row[3]:.2f}'] for row in data]
    headers = ['Method', 'Min Cost', 'c @ min', '% Improvement']
    # formats: plain, grid, pipe, fancy_grid, pretty, latex
    format = 'fancy_grid'
    table = tabulate(formatted_data, headers, tablefmt=format, disable_numparse=[1])
    print('C Analysis')
    print(table)
    # table = tabulate(data, headers, tablefmt=format, disable_numparse=[1])
    with open(load_dir + 'analysis_results.txt', 'w') as f:
        print(table, file=f)

    idx = np.argmin(best_aff_cost)
    min_lin_anchor_cost = best_aff_cost[-1]
    aff_improve = (1 - best_aff_cost[idx] / min_lin_anchor_cost) * 100
    best = C.ANCHOR_POINTS[idx]
    print(f'Improvement from affinization: aff ({best}) by {aff_improve:.2f}%\n')

    for i,c in enumerate(c_list):
        for j,p in enumerate(C.ANCHOR_POINTS):
            pw.plotStateLine(time, x_hist[p][k,i], C.LINE_STYLES[j],
                             label=f'{p}: {c = :.1f}')
            pw.plotInputLine(time, u_hist[p][k,i], C.LINE_STYLES[j],
                             label=f'{p} (u): {c = :.1f}')
    pw.plotStateLine(time, xr_hist, 'r--', label='ref')

    pw2 = app.createPlotWindow('Best Anchor Points from C Analysis')
    for i,p in enumerate(C.ANCHOR_POINTS):
        pw2.plotStateLine(time, x_hist[p][k,best_c_idx[i]], C.LINE_STYLES[i],
                          label=f'{p}: c = {best_c[i]:.1f}')
        pw2.plotInputLine(time, u_hist[p][k,best_c_idx[i]], C.LINE_STYLES[i],
                          label=f'{p}: c = {best_c[i]:.1f}')
    pw2.plotStateLine(time, xr_hist, C.LINE_STYLES['ref'], color=C.COLORS['ref'],
                      label='ref')
    ######## END: C Analysis ########

    ######## START: K Analysis ########
    if len(k_list) > 1:
        idx = {}
        min_cost = {}
        min_c = {}
        data = []
        for i,p in enumerate(C.ANCHOR_POINTS):
            idx[p] = np.unravel_index(np.argmin(costs[p]), costs[p].shape)
            min_cost[p] = costs[p][idx[p]]
            min_cost_nominal = costs[p][0,0]
            improvement = (1 - min_cost[p] / min_cost_nominal) * 100
            k_idx,c_idx = idx[p]
            min_k = k_list[k_idx]
            min_c[p] = c_list[c_idx]

            data.append([p, min_cost[p], min_k+1, min_c[p], improvement])

        formatted_data = [[row[0], f'{row[1]:.6f}', f'{row[2]:.1f}', f'{row[3]:.1f}', f'{row[4]:.2f}'] for row in data]
        headers = ['Method', 'Min Cost', 'k @ min', 'c @ min', '% Improvement']
        # formats: plain, grid, pipe, fancy_grid, pretty, latex
        format = 'fancy_grid'
        table = tabulate(formatted_data, headers, tablefmt=format, disable_numparse=[1])
        print('K Analysis')
        print(table, end='\n\n')
        # table = tabulate(data, headers, tablefmt=format, disable_numparse=[1])
        with open(load_dir + 'c_analysis_results.txt', 'w') as f:
            print(table, file=f)

        pw3 = app.createPlotWindow('K Analysis')
        for i,p in enumerate(C.ANCHOR_POINTS):
            idx = np.argmin(costs[p], axis=1)
            min_costs = costs[p][range(len(costs[p])), idx]
            min_c_list = c_list[idx]
            pw3.plotMinCosts(k_list, min_costs, min_c_list, label=p)
            # pw3.plotMinCosts(k_list, min_cost[p], min_c[p], label=p)
            pw3.plotCvK(c_list, k_list, costs[p])
    ######## END: K Analysis ########

    ######## START: Aff vs Lin Analysis ########
    pw4 = app.createPlotWindow('Time Tracking: Aff vs Lin', fontsize=10, fig_size=(500,420))

    idx = {}
    best_costs = np.empty(len(C.ANCHOR_POINTS))
    for i,p in enumerate(C.ANCHOR_POINTS):
        idx[p] = np.unravel_index(np.argmin(costs[p]), costs[p].shape)
        best_costs[i] = costs[p][idx[p]]
    lin_k_idx,lin_c_idx = idx[p]

    best_p_idx = np.argmin(best_costs)
    best_p = C.ANCHOR_POINTS[best_p_idx]
    best_idx = idx[best_p]
    best_aff_states = x_hist[best_p][best_idx]

    best_aff_cost = np.min(best_costs)
    best_lin_cost = best_costs[-1]
    nom_aff_cost = costs[C.ANCHOR_POINTS[0]][0,0]
    nom_lin_cost = costs[C.ANCHOR_POINTS[-1]][0,0]
    best_lin_reduction = (1 - best_aff_cost / best_lin_cost) * 100
    nom_aff_reduction = (1 - best_aff_cost / nom_aff_cost) * 100
    nom_lin_reduction = (1 - best_aff_cost / nom_lin_cost) * 100
    print(f'best aff vs best lin: {best_lin_reduction:.2f}% reduction')
    print(f'best aff vs nom aff: {nom_aff_reduction:.2f}% reduction')
    print(f'best aff vs nom lin: {nom_lin_reduction:.2f}% reduction')

    k_idx,c_idx = best_idx

    nom_aff_states = x_hist[C.ANCHOR_POINTS[0]][0,0]
    best_lin_states = x_hist[C.ANCHOR_POINTS[-1]][lin_k_idx,lin_c_idx]
    nom_lin_states = x_hist[C.ANCHOR_POINTS[-1]][0,0]

    lw = 1.25

    lbl = f'best aff: k={k_idx+1}, c={c_list[c_idx]:.1f}, p={best_p}'
    print(lbl)
    pw4.plotStateLine(time, best_aff_states, C.LINE_STYLES['best'], label=lbl[:8],
                      color=C.COLORS['best_aff'], linewidth=lw)
    pw4.plotStateLine(time, nom_aff_states, C.LINE_STYLES['nom'], label=f'nom aff',
                      color=C.COLORS['nom_aff'], linewidth=lw)
    lin_c = c_list[lin_c_idx]
    lbl = f'best lin: k={lin_k_idx+1}, c={lin_c:.1f}'
    print(lbl)
    pw4.plotStateLine(time, best_lin_states, C.LINE_STYLES['best'],
                      label=lbl[:8], color=C.COLORS['best_lin'], linewidth=lw)
    pw4.plotStateLine(time, nom_lin_states, C.LINE_STYLES['nom'], label=f'nom lin',
                      color=C.COLORS['nom_lin'], linewidth=lw)
    pw4.plotStateLine(time, xr_hist, C.LINE_STYLES['ref'], label='ref',
                      color=C.COLORS['ref'], linewidth=lw)
    ######## END: Aff vs Lin Analysis ########


    if headless:
        app.pause(0.5)
    else:
        app.show()

    print('Saving plots...')
    for ext in img_types:
        pw.savePlots(load_dir, end='_all', image_type=ext)
        pw2.savePlots(load_dir, end='_best', image_type=ext)
        if len(k_list) > 1:
            pw3.savePlots(load_dir, end='', image_type=ext)
    print('Plots saved')

    return


if __name__ == '__main__':
    main()
