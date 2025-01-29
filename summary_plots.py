import numpy as np
import matplotlib.pyplot as plt
import os
import pickle

from examples.plot_application import PlotApplication, TabbedWindow, FigureSpacing

import matplotlib
matplotlib.rcParams['axes.formatter.limits'] = (-3, 3) # display 3 sig figs


def main():
    load_dir = f'{os.environ["HOME"]}/data/ampc24/analysis/summary'
    systems = ['arm', 'beam', 'pendulum', 'pendulumz', 'multirotor']
    total_count = 0
    total_trials = 0
    c_all = []
    k_all = []
    c_reduction_all = []
    k_reduction_all = []
    aff_reductions_all = []
    best_lin_reductions_all = []
    nom_lin_reductions_all = []
    best_methods = []

    with open(f'{load_dir}/refs.pkl', 'rb') as file:
        ref_cmds = pickle.load(file)
    ref_types = {
        'arm': ['step', 'ramp', 'cos_60', 'cos_90'],
        'beam': ['step', 'ramp', 'cos'],
        'pendulum': ['step', 'cos_15', 'cos_25', 'ramp'],
        'pendulumz': ['stepz', 'cosz_2', 'cosz_5', 'rampz'],
        'multirotor': ['step', 'wavy', 'ramp1', 'ramp3']
    }

    app = PlotApplication()
    size = [500, 700]
    cost_win = TabbedWindow(f'wIAE', size)
    reduction_win = TabbedWindow(f'affinization % reduction', size)
    # improvement_win = TabbedWindow(f'affinization % improvement', size)

    for system in systems:
        uk = np.load(f'{load_dir}/{system}_aff_uk.npz')
        ueq = np.load(f'{load_dir}/{system}_aff_ueq.npz')
        xeq = np.load(f'{load_dir}/{system}_aff_xeq.npz')
        lin = np.load(f'{load_dir}/{system}_lin.npz')
        summary = np.load(f'{load_dir}/{system}_analysis.npz')

        methods = [uk, ueq, xeq, lin]

        refs: list[str] = ref_cmds[system]
        cost_best_aff = []
        cost_nom_aff = []
        cost_best_lin = []
        cost_nom_lin = []
        aff_reductions = []
        best_lin_reductions = []
        nom_lin_reductions = []
        aff_improvements = []
        best_lin_improvements = []
        nom_lin_improvements = []
        idx = 0
        current_ref = 'n/a'
        n = len(current_ref)
        for i,ref in enumerate(refs):
            if ref[:n] != current_ref:
                cost_best_aff.append([summary['best_aff_cost'][i]])
                cost_nom_aff.append([summary['nominal_aff_cost'][i]])
                cost_best_lin.append([summary['best_lin_cost'][i]])
                cost_nom_lin.append([summary['nominal_lin_cost'][i]])
                aff_reductions.append([summary['aff_reduction'][i]])
                best_lin_reductions.append([summary['best_lin_reduction'][i]])
                nom_lin_reductions.append([summary['nom_lin_reduction'][i]])
                aff_improvements.append([summary['aff_improvement'][i]])
                best_lin_improvements.append([summary['best_lin_improvement'][i]])
                nom_lin_improvements.append([summary['nom_lin_improvement'][i]])

                current_ref = ref_types[system][idx]
                n = len(current_ref)
                idx += 1
            else:
                cost_best_aff[-1].extend([summary['best_aff_cost'][i]])
                cost_nom_aff[-1].extend([summary['nominal_aff_cost'][i]])
                cost_best_lin[-1].extend([summary['best_lin_cost'][i]])
                cost_nom_lin[-1].extend([summary['nominal_lin_cost'][i]])
                aff_reductions[-1].extend([summary['aff_reduction'][i]])
                best_lin_reductions[-1].extend([summary['best_lin_reduction'][i]])
                nom_lin_reductions[-1].extend([summary['nom_lin_reduction'][i]])
                aff_improvements[-1].extend([summary['aff_improvement'][i]])
                best_lin_improvements[-1].extend([summary['best_lin_improvement'][i]])
                nom_lin_improvements[-1].extend([summary['nom_lin_improvement'][i]])
            aff_reductions_all.extend([summary['aff_reduction'][i]])
            best_lin_reductions_all.extend([summary['best_lin_reduction'][i]])
            nom_lin_reductions_all.extend([summary['nom_lin_reduction'][i]])

        n = len(aff_reductions)
        fig_costs, ax_costs = plt.subplots(n)
        cost_win.addTab(f'{system}', fig_costs)
        fig_reductions, ax_reductions = plt.subplots(n)
        reduction_win.addTab(f'{system}', fig_reductions)
        # fig_improvements, ax_improvements = plt.subplots(n)
        # improvement_win.addTab(f'{system}', fig_improvements)
        for i in range(n):
            title = f'{ref_types[system][i].replace("_", " ").replace("z", "")}'

            a: plt.Axes = ax_costs[i]
            a.set_title(title)
            x = np.arange(len(cost_best_aff[i])) + 1
            a.plot(x, cost_best_aff[i], 'm', label='best aff')
            a.plot(x, cost_nom_aff[i], 'b--', label='nom aff')
            a.plot(x, cost_best_lin[i], 'g', label='best lin')
            a.plot(x, cost_nom_lin[i], 'r--', label='nom lin')
            a.set_ylabel('wIAE')
            # if system == 'multirotor':
            #     a.set_yscale('log')
            if i == n-1:
                a.set_xlabel('difficulty')
            a.set_xticks(x)
            a.set_xticklabels(x.astype(str))
            # a.ticklabel_format(scilimits=(-4,4))
            if i == 0:
                a.legend(ncol=2)

            a: plt.Axes = ax_reductions[i]
            a.set_title(title)
            x = np.arange(len(aff_reductions[i])) + 1
            a.plot(x, aff_reductions[i], 'b--', label='nom aff')
            a.plot(x, best_lin_reductions[i], 'g', label='best lin')
            a.plot(x, nom_lin_reductions[i], 'r-.', label='nom lin')

            # print(f'{system} {ref_types[system][i]} mean reductions: ', end='')
            # aff_mean = np.mean(aff_reductions[i])
            # print(f'{aff_mean:.2f}%, ', end='')
            # best_lin_mean = np.mean(best_lin_reductions[i])
            # print(f'{best_lin_mean:.2f}%, ', end='')
            # nom_lin_mean = np.mean(nom_lin_reductions[i])
            # print(f'{nom_lin_mean:.2f}%')
            # a.plot([x[0], x[-1]], [aff_mean]*2, 'b:')
            # a.plot([x[0], x[-1]], [best_lin_mean]*2, 'g:')
            # a.plot([x[0], x[-1]], [nom_lin_mean]*2, 'r:')

            a.set_ylabel(f'% reduction')
            if i == n-1:
                a.set_xlabel('difficulty')
            a.set_xticks(x)
            a.set_xticklabels(x.astype(str))
            if i == 0:
                a.legend(ncol=1)

            # a: plt.Axes = ax_improvements[i]
            # a.set_title(ref_types[system][i])
            # x = np.arange(len(aff_improvements[i])) + 1
            # print(f'{system} {ref_types[system][i]} mean improvements: ', end='')
            # aff_mean = np.mean(aff_improvements[i])
            # print(f'{aff_mean:.2f}%, ', end='')
            # best_lin_mean = np.mean(best_lin_improvements[i])
            # print(f'{best_lin_mean:.2f}%, ', end='')
            # nom_lin_mean = np.mean(nom_lin_improvements[i])
            # print(f'{nom_lin_mean:.2f}%')
            # a.plot(x, aff_improvements[i], 'b--', label='nom aff')
            # # a.plot([x[0], x[-1]], [aff_mean]*2, 'b:')
            # a.plot(x, best_lin_improvements[i], 'g', label='best lin')
            # # a.plot([x[0], x[-1]], [best_lin_mean]*2, 'g:')
            # a.plot(x, nom_lin_improvements[i], 'r-.', label='nom lin')
            # # a.plot([x[0], x[-1]], [nom_lin_mean]*2, 'r:')
            # a.set_ylabel(f'% improvement')
            # if i == n-1:
            #     a.set_xlabel('difficulty')
            # a.set_xticks(x)
            # a.set_xticklabels(x.astype(str))
            # a.legend()

        errors = []
        ck_better = []
        for method in methods:
            # idx = refs.find
            # ref_type =
            c = method['c_best']
            k = method['k_best']
            c_is_nominal = c == 0
            k_is_nominal = k == 1
            c_all.extend(c)
            k_all.extend(k)
            c_reduction_all.extend(method['c_reduction'])
            k_reduction_all.extend(method['k_reduction'])
            ck_better.append(~c_is_nominal)
            error_mask = c_is_nominal & ~k_is_nominal
            k_is_nominal[error_mask] = True
            errors.append(np.sum(error_mask))
        count = np.sum(ck_better)
        trials = len(ck_better)*len(ck_better[0])
        total_count += count
        total_trials += trials
        # print(np.array(ck_better, dtype=np.int64))
        print(f'{system}:', end=' ')
        print(f'better {count} times of {trials} ({100*count/trials:.2f}%)')
        # print(f'{system}: {errors}\n')

        # c_mask = uk['c_best'] == 0
        # k_mask = uk['k_best'] != 1
        # print(f'{system}: {np.sum(c_mask)} / {len(c_mask)}, {np.sum(k_mask&c_mask)} / {len(k_mask)}')
        # print(uk['k_best'][c_mask])

        best_methods.extend(summary['best_method'])

    app.addWindow(cost_win)
    app.addWindow(reduction_win)
    # app.addWindow(improvement_win)

    print(f'better {total_count} times of {total_trials} ({100*total_count/total_trials:.2f}%)')

    # c_all = np.array([c for c_row in c_all for c in c_row]).flatten()
    c_all = np.array(c_all)
    k_all = np.array(k_all)
    c_reduction_all = np.array(c_reduction_all)
    k_reduction_all = np.array(k_reduction_all)

    win1 = TabbedWindow('System Analysis', size=[500,400])

    # hist_data = np.zeros(total_trials)
    # hist_data[:total_count] = 1
    fig, ax_reductions = plt.subplots(2)
    a: plt.Axes = ax_reductions[0]
    bins = np.arange(0, 1.2, 0.1) - 0.05
    a.hist(c_all, bins, range=(0,1), align='mid', rwidth=0.8)
    a.set_xlabel('c')
    a.set_ylabel('count')
    a.set_ylim(bottom=0)
    a.set_xticks(np.arange(0, 1.1, 0.1))
    a: plt.Axes = ax_reductions[1]
    a.hist(c_reduction_all, bins=15, align='mid', rwidth=0.8)
    a.set_xlabel(f'c % reduction')
    a.set_ylabel('count')
    win1.addTab('c', fig)

    fig, ax_reductions = plt.subplots(2)
    a: plt.Axes = ax_reductions[0]
    a.hist(k_all, bins=11, align='mid', rwidth=0.8)
    a.set_xlabel('k')
    a.set_ylabel('count')
    a: plt.Axes = ax_reductions[1]
    a.hist(k_reduction_all, bins=15, align='mid', rwidth=0.8)
    a.set_xlabel(f'k % reduction')
    a.set_ylabel('count')
    win1.addTab('k', fig)

    app.addWindow(win1)


    # win = TabbedWindow('Reduction Histograms')
    # fig, ax_reductions = plt.subplots()
    # a: plt.Axes = ax_reductions
    # a.hist(aff_reductions_all)#, bins=15, align='mid', rwidth=0.8)
    # a.set_xlabel(f'aff % reduction')
    # a.set_ylabel('count')
    # win.addTab('aff', fig)

    # fig, ax_reductions = plt.subplots()
    # a: plt.Axes = ax_reductions
    # a.hist(best_lin_reductions_all)#, bins=15, align='mid', rwidth=0.8)
    # a.set_xlabel(f'best lin % reduction')
    # a.set_ylabel('count')
    # win.addTab('best lin', fig)

    # fig, ax_reductions = plt.subplots()
    # a: plt.Axes = ax_reductions
    # a.hist(nom_lin_reductions_all)#, bins=15, align='mid', rwidth=0.8)
    # a.set_xlabel(f'nom_lin % reduction')
    # a.set_ylabel('count')
    # win.addTab('nom lin', fig)

    # fig, ax_reductions = plt.subplots()
    # a: plt.Axes = ax_reductions
    # reductions_all = aff_reductions_all + best_lin_reductions_all + nom_lin_reductions_all
    # a.hist(reductions_all)#, bins=15, align='mid', rwidth=0.8)
    # a.set_xlabel(f'% reduction')
    # a.set_ylabel('count')
    # win.addTab('all', fig)

    fig, ax_reductions = plt.subplots()
    a: plt.Axes = ax_reductions
    bins = [-5, 5, 15, 25, 35, 45, 55, 65, 75, 85, 95, 105]
    lbl = ' vs best aff'
    a.hist([aff_reductions_all, best_lin_reductions_all, nom_lin_reductions_all],
            bins=bins, stacked=False, align='mid',
            label=['nom aff'+lbl, 'best lin'+lbl, 'nom lin'+lbl])
    a.set_xlabel(f'% reduction')
    a.set_ylabel('count')
    # a.set_title(f'Histogram of % Reductions')# Comparing other Methods to Nominal Affinization')
    a.legend()
    # win.addTab('all v2', fig)
    win1.addTab('reductions', fig)

    fig, ax_methods = plt.subplots()
    a: plt.Axes = ax_methods
    bins = np.arange(0, 5, 1) - 0.5
    labels = [r'$(x_0,u_{-1})$', r'$(x_0,u_e)$', r'$(x_e,u_{-1})$', r'$(x_e,u_e)$']
    best_methods = np.array(best_methods).ravel()
    methods = np.empty(best_methods.shape, dtype=int)
    for i, label in enumerate(labels):
        methods[best_methods == label] = i
    # a.hist(summary['best_method'], bins, range=(0,1), align='mid', rwidth=0.8)
    # a.hist(best_methods, bins, align='mid', rwidth=0.8)
    a.hist(methods, bins, align='mid', rwidth=0.8)
    a.set_xticks(np.arange(0, 4))
    a.set_xticklabels(labels)
    win1.addTab('best method', fig)

    # print(f'count aff: {np.sum(summary["best_method"] == "aff (x0,u0)")}')

    # app.addWindow(win)

    app.show()
    return


if __name__ == '__main__':
    main()
