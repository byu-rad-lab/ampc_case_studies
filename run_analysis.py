import numpy as np
from tqdm import tqdm

import case_studies.single_link_arm.simulator as arm_sim
import case_studies.block_beam.simulator as beam_sim
import case_studies.cart_pendulum.simulator as pendulum_sim
import case_studies.multirotor.simulator as multirotor_sim
import plot_analysis as plotter
from parsing import getParsedArgs_run


def main():
    default_dir = '/tmp/ampc24/analysis/'
    desc = 'Run full analysis'
    args = getParsedArgs_run(default_dir, desc)
    if args.system == 'arm':
        sim = arm_sim.getSimulator(args)
    elif args.system == 'blockbeam':
        sim = beam_sim.getSimulator(args)
    elif args.system == 'pendulum':
        sim = pendulum_sim.getSimulator(args)
    elif args.system == 'multirotor':
        sim = multirotor_sim.getSimulator(args)
    else:
        raise ValueError('Invalid system')

    num_c = 11
    c_list = np.linspace(0, 1, num_c)
    k_increment = 1
    if args.ref_type != 'step' and args.k_all:
        T_idx = 15
        k_list = np.array([*np.arange(0, T_idx), *np.arange(T_idx, sim.T, k_increment)])
    else:
        k_list = np.arange(1)

    # run a random sim
    c = np.random.rand()
    print(f'c init: {c}')
    _,_,_,_,_ = sim.run(c, k=0, method='lin')

    aff_uk_costs_all = []
    aff_uk_states_all = []
    aff_uk_inputs_all = []
    aff_uk_st_all = []

    aff_ueq_costs_all = []
    aff_ueq_states_all = []
    aff_ueq_inputs_all = []
    aff_ueq_st_all = []

    aff_xeq_costs_all = []
    aff_xeq_states_all = []
    aff_xeq_inputs_all = []
    aff_xeq_st_all = []

    lin_costs_all = []
    lin_states_all = []
    lin_inputs_all = []
    lin_st_all = []

    for kr in tqdm(k_list, desc='K Loop'):
        aff_uk_costs = []
        aff_uk_states = []
        aff_uk_inputs = []
        aff_uk_st = []

        aff_ueq_costs = []
        aff_ueq_states = []
        aff_ueq_inputs = []
        aff_ueq_st = []

        aff_xeq_costs = []
        aff_xeq_states = []
        aff_xeq_inputs = []
        aff_xeq_st = []

        lin_costs = []
        lin_states = []
        lin_inputs = []
        lin_st = []

        for c in tqdm(c_list, desc='C Loop', leave=False):
            cost, x_hist, xr_hist, u_hist, st_hist = sim.run(c, kr, method='uk')
            aff_uk_costs.append(cost)
            aff_uk_states.append(x_hist)
            aff_uk_inputs.append(u_hist)
            aff_uk_st.append(st_hist)

            cost, x_hist, xr_hist, u_hist, st_hist = sim.run(c, kr, method='ueq')
            aff_ueq_costs.append(cost)
            aff_ueq_states.append(x_hist)
            aff_ueq_inputs.append(u_hist)
            aff_ueq_st.append(st_hist)

            cost, x_hist, xr_hist, u_hist, st_hist = sim.run(c, kr, method='xeq')
            aff_xeq_costs.append(cost)
            aff_xeq_states.append(x_hist)
            aff_xeq_inputs.append(u_hist)
            aff_xeq_st.append(st_hist)

            cost, x_hist, xr_hist, u_hist, st_hist = sim.run(c, kr, method='lin')
            lin_costs.append(cost)
            lin_states.append(x_hist)
            lin_inputs.append(u_hist)
            lin_st.append(st_hist)

        aff_uk_costs_all.append(aff_uk_costs)
        aff_uk_states_all.append(aff_uk_states)
        aff_uk_inputs_all.append(aff_uk_inputs)
        aff_uk_st_all.append(aff_uk_st)

        aff_ueq_costs_all.append(aff_ueq_costs)
        aff_ueq_states_all.append(aff_ueq_states)
        aff_ueq_inputs_all.append(aff_ueq_inputs)
        aff_ueq_st_all.append(aff_ueq_st)

        aff_xeq_costs_all.append(aff_xeq_costs)
        aff_xeq_states_all.append(aff_xeq_states)
        aff_xeq_inputs_all.append(aff_xeq_inputs)
        aff_xeq_st_all.append(aff_xeq_st)

        lin_costs_all.append(lin_costs)
        lin_states_all.append(lin_states)
        lin_inputs_all.append(lin_inputs)
        lin_st_all.append(lin_st)

    np.save(args.dir + 'time.npy', sim.time)

    np.save(args.dir + 'aff_uk_costs.npy', np.array(aff_uk_costs_all))
    np.save(args.dir + 'aff_uk_states.npy', np.array(aff_uk_states_all))
    np.save(args.dir + 'aff_uk_inputs.npy', np.array(aff_uk_inputs_all))
    np.save(args.dir + 'aff_uk_solve_times.npy', np.array(aff_uk_st_all))

    np.save(args.dir + 'aff_ueq_costs.npy', np.array(aff_ueq_costs_all))
    np.save(args.dir + 'aff_ueq_states.npy', np.array(aff_ueq_states_all))
    np.save(args.dir + 'aff_ueq_inputs.npy', np.array(aff_ueq_inputs_all))
    np.save(args.dir + 'aff_ueq_solve_times.npy', np.array(aff_ueq_st_all))

    np.save(args.dir + 'aff_xeq_costs.npy', np.array(aff_xeq_costs_all))
    np.save(args.dir + 'aff_xeq_states.npy', np.array(aff_xeq_states_all))
    np.save(args.dir + 'aff_xeq_inputs.npy', np.array(aff_xeq_inputs_all))
    np.save(args.dir + 'aff_xeq_solve_times.npy', np.array(aff_xeq_st_all))

    np.save(args.dir + 'lin_costs.npy', np.array(lin_costs_all))
    np.save(args.dir + 'lin_states.npy', np.array(lin_states_all))
    np.save(args.dir + 'lin_inputs.npy', np.array(lin_inputs_all))
    np.save(args.dir + 'lin_solve_times.npy', np.array(lin_st_all))

    np.save(args.dir + 'ref_states.npy', xr_hist)

    np.save(args.dir + 'Q.npy', sim.Q)
    np.save(args.dir + 'k_list.npy', k_list)

    with open(args.dir + 'system.txt', 'w') as f:
        f.write(args.system)

    plotter.plot(args.dir, args.headless)

    return


if __name__ == '__main__':
    main()
