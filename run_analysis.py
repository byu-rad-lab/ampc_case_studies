import numpy as np
from tqdm import tqdm

import case_studies.single_link_arm.simulator as arm_sim
import case_studies.block_beam.simulator as beam_sim
import case_studies.cart_pendulum.simulator as pendulum_sim
import case_studies.multirotor.simulator as multirotor_sim
import plot_analysis as plotter
from parsing import getParsedArgs_run
import constants as C


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
    _,_,_,_,_ = sim.run(C.ANCHOR_POINTS[-1], c, k=0)

    k_len = len(k_list)
    c_len = len(c_list)
    t_len = len(sim.time)
    costs = {p: np.empty((k_len,c_len)) for p in C.ANCHOR_POINTS}
    states = {p: np.empty((k_len,c_len,t_len,sim.n)) for p in C.ANCHOR_POINTS}
    inputs = {p: np.empty((k_len,c_len,t_len-1,sim.m)) for p in C.ANCHOR_POINTS}
    solve_times = {p: np.empty((k_len,c_len,t_len-1)) for p in C.ANCHOR_POINTS}

    for k_idx,k in enumerate(tqdm(k_list, desc='K Loop')):
        for c_idx,c in enumerate(tqdm(c_list, desc='C Loop', leave=False)):
            for p in C.ANCHOR_POINTS:
                cost, x_hist, xr_hist, u_hist, st_hist = sim.run(p, c, k)
                costs[p][k_idx,c_idx] = cost
                states[p][k_idx,c_idx] = x_hist
                inputs[p][k_idx,c_idx] = u_hist
                solve_times[p][k_idx,c_idx] = st_hist

    np.save(args.dir + 'time.npy', sim.time)
    np.savez(args.dir + 'costs.npz', **costs)
    np.savez(args.dir + 'states.npz', **states)
    np.savez(args.dir + 'inputs.npz', **inputs)
    np.savez(args.dir + 'solve_times.npz', **solve_times)
    np.save(args.dir + 'ref_states.npy', xr_hist)
    np.save(args.dir + 'Q.npy', sim.Q)
    np.save(args.dir + 'k_list.npy', k_list)
    with open(args.dir + 'system.txt', 'w') as f:
        f.write(args.system)

    plotter.plot(args.dir, args.headless)

    return


if __name__ == '__main__':
    main()
