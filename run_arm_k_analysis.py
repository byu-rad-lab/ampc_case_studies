import numpy as np
import tqdm

import examples.single_link_arm.simulator as simulator
from parsing import getParsedArgs_run
import plot_arm_k_analysis as plotter


def main():
    default_dir = '/tmp/ampc24/arm/k_analysis/'
    desc = 'Run arm k analysis'
    ref_types = ['ramp', 'cos', 'step']
    args = getParsedArgs_run(default_dir, desc, ref_types)

    sim = simulator.getSimulator(args)

    c_list = np.linspace(0, 1, 11)
    reference_type = args.ref_type
    if reference_type != 'step':
        k_list = np.arange(0, sim.T)
    else:
        k_list = np.arange(1)

    aff_all_costs = []
    aff_min_costs = []
    aff_min_c_list = []

    lin_all_costs = []
    lin_min_costs = []
    lin_min_c_list = []

    c = np.random.rand()
    print(f'c init: {c}')
    _,_,_,_,_ = sim.run(c, k=0, linearize=True)

    for k in tqdm.tqdm(k_list, desc='K Loop'):
        aff_cost_list = []
        lin_cost_list = []
        for c in tqdm.tqdm(c_list, desc='C Loop', leave=False):
            # cost, x_hist, xr_hist, u_hist, st_hist = sim.run(x0, c)
            cost, _, _, _, _ = sim.run(c, k, linearize=False)
            aff_cost_list.append(cost)
            cost, _, _, _, _ = sim.run(c, k, linearize=True)
            lin_cost_list.append(cost)

        aff_all_costs.append(aff_cost_list)
        min_idx = np.argmin(aff_cost_list)
        aff_min_costs.append(aff_cost_list[min_idx])
        aff_min_c_list.append(c_list[min_idx])

        lin_all_costs.append(lin_cost_list)
        min_idx = np.argmin(lin_cost_list)
        lin_min_costs.append(lin_cost_list[min_idx])
        lin_min_c_list.append(c_list[min_idx])

    aff_all_costs = np.array(aff_all_costs)
    aff_min_costs = np.array(aff_min_costs)
    aff_min_c_list = np.array(aff_min_c_list)

    lin_all_costs = np.array(lin_all_costs)
    lin_min_costs = np.array(lin_min_costs)
    lin_min_c_list = np.array(lin_min_c_list)

    np.savetxt(args.dir + 'aff_all_costs.txt', np.array(aff_all_costs))
    np.savetxt(args.dir + 'aff_min_costs.txt', np.array(aff_min_costs))
    np.savetxt(args.dir + 'aff_min_c_values.txt', np.array(aff_min_c_list))

    np.savetxt(args.dir + 'lin_all_costs.txt', np.array(lin_all_costs))
    np.savetxt(args.dir + 'lin_min_costs.txt', np.array(lin_min_costs))
    np.savetxt(args.dir + 'lin_min_c_values.txt', np.array(lin_min_c_list))

    np.savetxt(args.dir + 'c_list.txt', c_list)
    np.savetxt(args.dir + 'k_list.txt', k_list)

    plotter.plot(args.dir)
    return


if __name__ == '__main__':
    main()
