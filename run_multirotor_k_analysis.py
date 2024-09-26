import numpy as np
from tqdm import tqdm

import examples.multirotor.simulator as simulator
from parsing import getParsedArgs_run
import plot_multirotor_k_analysis as plotter


def main():
    default_dir = '/tmp/ampc24/multirotor/k_analysis/'
    desc = 'Run multirotor k analysis'
    ref_types = ['wavy', 'ramp1', 'ramp3', 'step']
    args = getParsedArgs_run(default_dir, desc, ref_types)

    sim = simulator.getSimulator(args)

    k_increment = 1
    if args.ref_type != 'step':
        T_idx = 15
        k_list = np.array([*np.arange(0, T_idx), *np.arange(T_idx, sim.T, k_increment)])
    else:
        k_list = np.arange(1)
    c_list = np.linspace(0,1,11)
    # c_list = np.linspace(0,1,2)
    # c_list = [1.0]

    aff_ueq_all_costs = []
    aff_ueq_min_costs = []
    aff_ueq_min_c_list = []
    aff_uk_all_costs = []
    aff_uk_min_costs = []
    aff_uk_min_c_list = []
    aff_xeq_all_costs = []
    aff_xeq_min_costs = []
    aff_xeq_min_c_list = []
    lin_all_costs = []
    lin_min_costs = []
    lin_min_c_list = []
    for kr in tqdm(k_list, desc='K Loop'):
        aff_ueq_cost_list = []
        aff_uk_cost_list = []
        aff_xeq_cost_list = []
        lin_cost_list = []
        for c in tqdm(c_list, desc='C Loop', leave=False):
            cost, x_hist, xr_hist, u_hist, st_hist = sim.run(c, kr, 'ueq')
            aff_ueq_cost_list.append(cost)
            cost, x_hist, xr_hist, u_hist, st_hist = sim.run(c, kr, 'uk')
            aff_uk_cost_list.append(cost)
            cost, x_hist, xr_hist, u_hist, st_hist = sim.run(c, kr, 'xeq')
            aff_xeq_cost_list.append(cost)
            cost, x_hist, xr_hist, u_hist, st_hist = sim.run(c, kr, 'lin')
            lin_cost_list.append(cost)
        aff_ueq_all_costs.append(aff_ueq_cost_list)
        min_idx = np.argmin(aff_ueq_cost_list)
        aff_ueq_min_costs.append(aff_ueq_cost_list[min_idx])
        aff_ueq_min_c_list.append(c_list[min_idx])

        aff_uk_all_costs.append(aff_uk_cost_list)
        min_idx = np.argmin(aff_uk_cost_list)
        aff_uk_min_costs.append(aff_uk_cost_list[min_idx])
        aff_uk_min_c_list.append(c_list[min_idx])

        aff_xeq_all_costs.append(aff_xeq_cost_list)
        min_idx = np.argmin(aff_xeq_cost_list)
        aff_xeq_min_costs.append(aff_xeq_cost_list[min_idx])
        aff_xeq_min_c_list.append(c_list[min_idx])

        lin_all_costs.append(lin_cost_list)
        min_idx = np.argmin(lin_cost_list)
        lin_min_costs.append(lin_cost_list[min_idx])
        lin_min_c_list.append(c_list[min_idx])

    aff_ueq_all_costs = np.array(aff_ueq_all_costs)
    aff_ueq_min_costs = np.array(aff_ueq_min_costs)
    aff_ueq_min_c_list = np.array(aff_ueq_min_c_list)

    aff_uk_all_costs = np.array(aff_uk_all_costs)
    aff_uk_min_costs = np.array(aff_uk_min_costs)
    aff_uk_min_c_list = np.array(aff_uk_min_c_list)

    aff_xeq_all_costs = np.array(aff_xeq_all_costs)
    aff_xeq_min_costs = np.array(aff_xeq_min_costs)
    aff_xeq_min_c_list = np.array(aff_xeq_min_c_list)

    lin_all_costs = np.array(lin_all_costs)
    lin_min_costs = np.array(lin_min_costs)
    lin_min_c_list = np.array(lin_min_c_list)

    np.savetxt(args.dir + 'aff_ueq_all_costs.txt', aff_ueq_all_costs)
    np.savetxt(args.dir + 'aff_ueq_min_costs.txt', aff_ueq_min_costs)
    np.savetxt(args.dir + 'aff_ueq_min_c_values.txt', aff_ueq_min_c_list)

    np.savetxt(args.dir + 'aff_uk_all_costs.txt', aff_uk_all_costs)
    np.savetxt(args.dir + 'aff_uk_min_costs.txt', aff_uk_min_costs)
    np.savetxt(args.dir + 'aff_uk_min_c_values.txt', aff_uk_min_c_list)

    np.savetxt(args.dir + 'aff_xeq_all_costs.txt', aff_xeq_all_costs)
    np.savetxt(args.dir + 'aff_xeq_min_costs.txt', aff_xeq_min_costs)
    np.savetxt(args.dir + 'aff_xeq_min_c_values.txt', aff_xeq_min_c_list)

    np.savetxt(args.dir + 'lin_all_costs.txt', lin_all_costs)
    np.savetxt(args.dir + 'lin_min_costs.txt', lin_min_costs)
    np.savetxt(args.dir + 'lin_min_c_values.txt', lin_min_c_list)

    np.savetxt(args.dir + 'c_list.txt', c_list)
    np.savetxt(args.dir + 'k_list.txt', k_list)

    plotter.plot(args.dir)
    return


if __name__ == '__main__':
    main()
