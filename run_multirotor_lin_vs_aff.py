import numpy as np
from tqdm import tqdm

import examples.multirotor.simulator as simulator
import plot_multirotor_lin_vs_aff as plotter
from parsing import getParsedArgs_run


def main():
    default_dir = '/tmp/ampc24/multirotor/lin_vs_aff/'
    description='Run AMPC simulation analysis.'
    ref_types = ['step', 'wavy', 'ramp1', 'ramp3']
    args = getParsedArgs_run(default_dir, description, ref_types)

    sim = simulator.getSimulator(args)

    k_ref = 0
    c_list = np.linspace(0,1,11)
    # c_list = [0.0]*2

    aff_uk_cost_list = []
    aff_ueq_cost_list = []
    aff_xeq_cost_list = []
    lin_cost_list = []
    aff_uk_xtraj_hist = []
    aff_ueq_xtraj_hist = []
    aff_xeq_xtraj_hist = []
    lin_xtraj_hist = []
    aff_uk_utraj_hist = []
    aff_ueq_utraj_hist = []
    aff_xeq_utraj_hist = []
    lin_utraj_hist = []
    aff_uk_st_trials = []
    aff_ueq_st_trials = []
    aff_xeq_st_trials = []
    lin_st_trials = []
    c = np.random.rand()
    print(f'c init: {c}')
    _,_,_,_,_ = sim.run(c, k_ref, method='lin')
    for c in tqdm(c_list):
        cost, x_hist, xr_hist, u_hist, st_hist = sim.run(c, k_ref, method='uk')
        aff_uk_cost_list.append(cost)
        aff_uk_xtraj_hist.append(x_hist)
        aff_uk_utraj_hist.append(u_hist)
        aff_uk_st_trials.append(st_hist)
        cost, x_hist, xr_hist, u_hist, st_hist = sim.run(c, k_ref, method='ueq')
        aff_ueq_cost_list.append(cost)
        aff_ueq_xtraj_hist.append(x_hist)
        aff_ueq_utraj_hist.append(u_hist)
        aff_ueq_st_trials.append(st_hist)
        cost, x_hist, xr_hist, u_hist, st_hist = sim.run(c, k_ref, method='xeq')
        aff_xeq_cost_list.append(cost)
        aff_xeq_xtraj_hist.append(x_hist)
        aff_xeq_utraj_hist.append(u_hist)
        aff_xeq_st_trials.append(st_hist)
        cost, x_hist, xr_hist, u_hist, st_hist = sim.run(c, k_ref, method='lin')
        lin_cost_list.append(cost)
        lin_xtraj_hist.append(x_hist)
        lin_utraj_hist.append(u_hist)
        lin_st_trials.append(st_hist)

    np.savetxt(args.dir + 'time.txt', sim.time)
    np.savetxt(args.dir + 'ref_states.txt', xr_hist)

    np.savetxt(args.dir + 'aff_uk_costs.txt', np.array(aff_uk_cost_list))
    np.savetxt(args.dir + 'aff_uk_states.txt', np.array(aff_uk_xtraj_hist).reshape(len(c_list), -1))
    np.savetxt(args.dir + 'aff_uk_inputs.txt', np.array(aff_uk_utraj_hist).reshape(len(c_list), -1))
    np.savetxt(args.dir + 'aff_uk_solve_times.txt', np.array(aff_uk_st_trials))

    np.savetxt(args.dir + 'aff_ueq_costs.txt', np.array(aff_ueq_cost_list))
    np.savetxt(args.dir + 'aff_ueq_states.txt', np.array(aff_ueq_xtraj_hist).reshape(len(c_list), -1))
    np.savetxt(args.dir + 'aff_ueq_inputs.txt', np.array(aff_ueq_utraj_hist).reshape(len(c_list), -1))
    np.savetxt(args.dir + 'aff_ueq_solve_times.txt', np.array(aff_ueq_st_trials))

    np.savetxt(args.dir + 'aff_xeq_costs.txt', np.array(aff_xeq_cost_list))
    np.savetxt(args.dir + 'aff_xeq_states.txt', np.array(aff_xeq_xtraj_hist).reshape(len(c_list), -1))
    np.savetxt(args.dir + 'aff_xeq_inputs.txt', np.array(aff_xeq_utraj_hist).reshape(len(c_list), -1))
    np.savetxt(args.dir + 'aff_xeq_solve_times.txt', np.array(aff_xeq_st_trials))

    np.savetxt(args.dir + 'lin_costs.txt', np.array(lin_cost_list))
    np.savetxt(args.dir + 'lin_states.txt', np.array(lin_xtraj_hist).reshape(len(c_list), -1))
    np.savetxt(args.dir + 'lin_inputs.txt', np.array(lin_utraj_hist).reshape(len(c_list), -1))
    np.savetxt(args.dir + 'lin_solve_times.txt', np.array(lin_st_trials))

    plotter.plot(args.dir)

if __name__ == '__main__':
    main()
