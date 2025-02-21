import numpy as np
from tabulate import tabulate

import case_studies.single_link_arm.plotter as arm_plotter
import case_studies.block_beam.plotter as beam_plotter
import case_studies.cart_pendulum.plotter as pendulum_plotter
import case_studies.multirotor.plotter as multirotor_plotter
from parsing import getParsedArgs_plot


def main():
    load_dir = '/tmp/ampc24/analysis/'
    desc = 'Plot linearization vs affinization comparison'
    args = getParsedArgs_plot(load_dir, desc)
    plot(args.dir, args.headless)


def plot(load_dir: str, headless: bool=False):
    ## Params
    deg = True
    legend = True
    fontsize = 14
    figsize = (1000,800)
    img_types = ['svg', 'pdf']

    ## Load Data
    time = np.load(load_dir + 'time.npy')

    aff_uk_costs = np.load(load_dir + 'aff_uk_costs.npy')
    aff_uk_states = np.load(load_dir + 'aff_uk_states.npy')
    aff_uk_inputs = np.load(load_dir + 'aff_uk_inputs.npy')

    aff_ueq_costs = np.load(load_dir + 'aff_ueq_costs.npy')
    aff_ueq_states = np.load(load_dir + 'aff_ueq_states.npy')
    aff_ueq_inputs = np.load(load_dir + 'aff_ueq_inputs.npy')

    aff_xeq_costs = np.load(load_dir + 'aff_xeq_costs.npy')
    aff_xeq_states = np.load(load_dir + 'aff_xeq_states.npy')
    aff_xeq_inputs = np.load(load_dir + 'aff_xeq_inputs.npy')

    lin_costs = np.load(load_dir + 'lin_costs.npy')
    lin_states = np.load(load_dir + 'lin_states.npy')
    lin_inputs = np.load(load_dir + 'lin_inputs.npy')

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

    ######## C Analysis ########
    pw = app.createPlotWindow('C Analysis')
    num_c = len(aff_uk_costs[0])
    c_list = np.linspace(0, 1, num_c)
    k = 0
    pw.plotCosts(c_list, aff_uk_costs[k], label='aff (uk)')
    pw.plotCosts(c_list, aff_ueq_costs[k], label='aff (ueq)')
    pw.plotCosts(c_list, aff_xeq_costs[k], label='aff (xeq)')
    pw.plotCosts(c_list, lin_costs[k], '-.', label='lin')

    aff_uk_idx = np.argmin(aff_uk_costs[k])
    aff_uk_mc = aff_uk_costs[k,aff_uk_idx]
    aff_uk_c0 = aff_uk_costs[k,0]

    aff_ueq_idx = np.argmin(aff_ueq_costs[k])
    aff_ueq_mc = aff_ueq_costs[k,aff_ueq_idx]
    aff_ueq_c0 = aff_ueq_costs[k,0]

    aff_xeq_idx = np.argmin(aff_xeq_costs[k])
    aff_xeq_mc = aff_xeq_costs[k,aff_xeq_idx]
    aff_xeq_c0 = aff_xeq_costs[k,0]

    lin_idx = np.argmin(lin_costs[k])
    lin_mc = lin_costs[k,lin_idx]
    lin_c0 = lin_costs[k,0]

    aff_mc = np.array([aff_uk_mc, aff_ueq_mc, aff_xeq_mc])
    aff_c0 = np.array([aff_uk_c0, aff_ueq_c0, aff_xeq_c0])
    aff_c_improve = (1 - aff_mc / aff_c0) * 100
    lin_c_improve = (1 - lin_mc / lin_c0) * 100

    data = [
        ['aff (uk)', aff_uk_mc, c_list[aff_uk_idx], aff_c_improve[0]],
        ['aff (ueq)', aff_ueq_mc, c_list[aff_ueq_idx], aff_c_improve[1]],
        ['aff (xeq)', aff_xeq_mc, c_list[aff_xeq_idx], aff_c_improve[2]],
        ['lin', lin_mc, c_list[lin_idx], lin_c_improve]
    ]
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

    idx = np.argmin(aff_mc)
    aff_improve = (1 - aff_mc[idx] / lin_mc) * 100
    if idx == 0:
        best = 'uk'
    elif idx == 1:
        best = 'ueq'
    else:
        best = 'xeq'
    print(f'Improvement from affinization: aff ({best}) by {aff_improve:.2f}%')
    print()

    for i,c in enumerate(c_list):
        pw.plotStateLine(time, aff_uk_states[k,i], label=f'aff (uk): {c = :.1f}')
        pw.plotStateLine(time, aff_ueq_states[k,i], label=f'aff (ueq): {c = :.1f}')
        pw.plotStateLine(time, aff_xeq_states[k,i], label=f'aff (xeq): {c = :.1f}')
        pw.plotStateLine(time, lin_states[k,i], '-.', label=f'lin: {c = :.1f}')
        pw.plotInputLine(time, aff_uk_inputs[k,i], label=f'aff (uk): {c = :.1f}')
        pw.plotInputLine(time, aff_ueq_inputs[k,i], label=f'aff (ueq): {c = :.1f}')
        pw.plotInputLine(time, aff_xeq_inputs[k,i], label=f'aff (xeq): {c = :.1f}')
        pw.plotInputLine(time, lin_inputs[k,i], '-.', label=f'lin: {c = :.1f}')
    pw.plotStateLine(time, xr_hist, 'r--', label='ref')

    # app.addWindow(pw)

    pw2 = app.createPlotWindow('Best Base Points from C Analysis')
    pw2.plotStateLine(time, aff_uk_states[k,aff_uk_idx], label=f'aff (uk): c = {c_list[aff_uk_idx]:.1f}')
    pw2.plotStateLine(time, aff_ueq_states[k,aff_ueq_idx], label=f'aff (ueq): c = {c_list[aff_ueq_idx]:.1f}')
    pw2.plotStateLine(time, aff_xeq_states[k,aff_xeq_idx], label=f'aff (xeq): c = {c_list[aff_xeq_idx]:.1f}')
    pw2.plotStateLine(time, lin_states[k,lin_idx], '-.', label=f'lin: c = {c_list[lin_idx]:.1f}')

    pw2.plotInputLine(time, aff_uk_inputs[k,aff_uk_idx], label=f'aff (uk): c = {c_list[aff_uk_idx]:.1f}')
    pw2.plotInputLine(time, aff_ueq_inputs[k,aff_ueq_idx], label=f'aff (ueq): c = {c_list[aff_ueq_idx]:.1f}')
    pw2.plotInputLine(time, aff_xeq_inputs[k,aff_xeq_idx], label=f'aff (xeq): c = {c_list[aff_xeq_idx]:.1f}')
    pw2.plotInputLine(time, lin_inputs[k,lin_idx], '-.', label=f'lin: c = {c_list[lin_idx]:.1f}')

    pw2.plotStateLine(time, xr_hist, 'r--', label='ref')

    # app.addWindow(pw2)
    ######## END: C Analysis ########

    ######## START: K Analysis ########
    if len(k_list) > 1:
        aff_uk_idx = np.argmin(aff_uk_costs, axis=1)
        aff_uk_min_costs = aff_uk_costs[range(len(aff_uk_costs)), aff_uk_idx]
        aff_uk_min_c = c_list[aff_uk_idx]

        aff_ueq_idx = np.argmin(aff_ueq_costs, axis=1)
        aff_ueq_min_costs = aff_ueq_costs[range(len(aff_ueq_costs)), aff_ueq_idx]
        aff_ueq_min_c = c_list[aff_ueq_idx]

        aff_xeq_idx = np.argmin(aff_xeq_costs, axis=1)
        aff_xeq_min_costs = aff_xeq_costs[range(len(aff_xeq_costs)), aff_xeq_idx]
        aff_xeq_min_c = c_list[aff_xeq_idx]

        lin_idx = np.argmin(lin_costs, axis=1)
        lin_min_costs = lin_costs[range(len(lin_costs)), lin_idx]
        lin_min_c = c_list[lin_idx]

        data = []
        min_idx = np.argmin(aff_uk_min_costs)
        min_cost = aff_uk_min_costs[min_idx]
        min_cost_nominal = aff_uk_min_costs[0]
        improve = (1 - min_cost / min_cost_nominal) * 100
        uk_k = k_list[min_idx]
        uk_c = aff_uk_min_c[min_idx]
        uk_c_idx = aff_uk_idx[uk_k]
        data.append(['aff (uk)', min_cost, uk_k, uk_c, improve])

        min_idx = np.argmin(aff_ueq_min_costs)
        min_cost = aff_ueq_min_costs[min_idx]
        min_cost_nominal = aff_ueq_min_costs[0]
        improve = (1 - min_cost / min_cost_nominal) * 100
        ueq_k = k_list[min_idx]
        ueq_c = aff_ueq_min_c[min_idx]
        ueq_c_idx = aff_ueq_idx[ueq_k]
        data.append(['aff (ueq)', min_cost, ueq_k, ueq_c, improve])

        min_idx = np.argmin(aff_xeq_min_costs)
        min_cost = aff_xeq_min_costs[min_idx]
        min_cost_nominal = aff_xeq_min_costs[0]
        improve = (1 - min_cost / min_cost_nominal) * 100
        xeq_k = k_list[min_idx]
        xeq_c = aff_xeq_min_c[min_idx]
        xeq_c_idx = aff_xeq_idx[xeq_k]
        data.append(['aff (xeq)', min_cost, xeq_k, xeq_c, improve])

        min_idx = np.argmin(lin_min_costs)
        min_cost = lin_min_costs[min_idx]
        min_cost_nominal = lin_min_costs[0]
        improve = (1 - min_cost / min_cost_nominal) * 100
        lin_k = k_list[min_idx]
        lin_c = lin_min_c[min_idx]
        lin_c_idx = lin_idx[lin_k]
        data.append(['lin', min_cost, lin_k, lin_c, improve])

        formatted_data = [[row[0], f'{row[1]:.6f}', f'{row[2]:.1f}', f'{row[3]:.1f}', f'{row[4]:.2f}'] for row in data]
        headers = ['Method', 'Min Cost', 'k @ min', 'c @ min', '% Improvement']
        # formats: plain, grid, pipe, fancy_grid, pretty, latex
        format = 'fancy_grid'
        table = tabulate(formatted_data, headers, tablefmt=format, disable_numparse=[1])
        print('K Analysis')
        print(table)
        # table = tabulate(data, headers, tablefmt=format, disable_numparse=[1])
        with open(load_dir + 'c_analysis_results.txt', 'w') as f:
            print(table, file=f)

        # aff_mc = np.array([row[1] for row in data[:-1]])
        aff_mc = np.array([row[1] for row in data])
        aff_k0 = np.array([aff_uk_min_costs[0], aff_ueq_min_costs[0],
                           aff_xeq_min_costs[0], lin_min_costs[0]])

        idx = np.argmin(aff_mc)
        aff_improve = (1 - aff_mc[idx] / min_cost) * 100

        min_cost = np.min(aff_mc)
        best_lin_reduction = (1 - min_cost / aff_mc[-1]) * 100
        nom_aff_reduction = (1 - min_cost / aff_uk_costs[0,0]) * 100
        nom_lin_reduction = (1 - min_cost / lin_costs[0,0]) * 100
        print(f'best lin vs best aff: {best_lin_reduction:.2f}% reduction')
        print(f'nom aff vs best aff: {nom_aff_reduction:.2f}% reduction')
        print(f'nom lin vs best aff: {nom_lin_reduction:.2f}% reduction')

        if idx == 0:
            best = 'uk'
            k = uk_k
            c_idx = aff_uk_idx[uk_k]
            best_aff_states = aff_uk_states[k,c_idx]
        elif idx == 1:
            best = 'ueq'
            k = ueq_k
            c_idx = aff_ueq_idx[ueq_k]
            best_aff_states = aff_ueq_states[k,c_idx]
        elif idx == 2:
            best = 'xeq'
            k = xeq_k
            c_idx = aff_xeq_idx[xeq_k]
            best_aff_states = aff_xeq_states[k,c_idx]
        else:
            best = 'lin'
            k = lin_k
            c_idx = lin_idx[lin_k]
            best_aff_states = lin_states[k,c_idx]
        # print(f'Improvement from affinization: aff ({best}) by {aff_improve:.2f}%')
        print()

        pw3 = app.createPlotWindow('K Analysis')
        pw3.plotMinCosts(k_list, aff_uk_min_costs, aff_uk_min_c, label='aff (uk)')
        pw3.plotMinCosts(k_list, aff_ueq_min_costs, aff_ueq_min_c, label='aff (ueq)')
        pw3.plotMinCosts(k_list, aff_xeq_min_costs, aff_xeq_min_c, label='aff (xeq)')
        pw3.plotMinCosts(k_list, lin_min_costs, lin_min_c, label='lin')
        pw3.plotCvK(c_list, k_list, aff_uk_costs)
        pw3.plotCvK(c_list, k_list, aff_ueq_costs)
        pw3.plotCvK(c_list, k_list, aff_xeq_costs)
        pw3.plotCvK(c_list, k_list, lin_costs)

    ######## END: K Analysis ########

    ######## START: Aff vs Lin Analysis ########
        pw4 = app.createPlotWindow('Summary Time Tracking')
        # nom_lin = lin_states[0,0]
        # nom_aff = aff_uk_states[0,0]
        # best_lin = lin_states[lin_k,lin_c]
        # best_aff = aff_uk_states[uk_k,uk_c]
        # pw4.plotStateLine(time, nom_lin, '-.', label='nominal lin')

        base_points = [r'$(x_0,u_{-1})$', r'$(x_0,u_e)$', r'$(x_e,u_{-1})$', r'$(x_e,u_e)$']
        lbl = f'best aff: k={k+1}, c={c_list[c_idx]:.1f}, p={base_points[idx]}'
        pw4.plotStateLine(time, best_aff_states, label=lbl)
        pw4.plotStateLine(time, aff_uk_states[0,0], label=f'nom aff')
        lbl = f'best lin: k = {lin_k+1}, c = {lin_c:.1f}'
        pw4.plotStateLine(time, lin_states[lin_k,lin_c_idx], label=lbl)
        pw4.plotStateLine(time, lin_states[0,0], label=f'nom lin')
        pw4.plotStateLine(time, xr_hist, 'r--', label='ref')

    ######## END: Aff vs Lin Analysis ########


    if headless:
        # app.plot_app.applyTightLayout()
        # app.plot_app.pause(0.5)
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
