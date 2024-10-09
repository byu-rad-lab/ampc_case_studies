import numpy as np
from tqdm import tqdm

import examples.single_link_arm.simulator as simulator
import plot_arm_lin_vs_aff as plotter
from parsing import getParsedArgs_run


def main():
    save_dir = f'/tmp/ampc24/arm/lin_vs_aff/'
    desc = 'Run linearization vs affinization comparison for single link arm'
    ref_types = ['step', 'ramp', 'cos']
    args = getParsedArgs_run(save_dir, desc, ref_types)

    sim = simulator.getSimulator(args)

    c_list = np.linspace(0, 1, 11)

    aff_cost_list = []
    aff_xtraj_hist = []
    aff_utraj_hist = []
    aff_st_hist = []

    lin_cost_list = []
    lin_xtraj_hist = []
    lin_utraj_hist = []
    lin_st_hist = []

    c = np.random.rand()
    print(f'c init: {c}')
    _,_,_,_,_ = sim.run(c, k=0, linearize=True)

    for c in tqdm(c_list):
        cost, x_hist, xr_hist, u_hist, st_hist = sim.run(c, k=0, linearize=False)
        aff_cost_list.append(cost)
        aff_xtraj_hist.append(x_hist)
        aff_utraj_hist.append(u_hist)
        aff_st_hist.append(st_hist)
        cost, x_hist, xr_hist, u_hist, st_hist = sim.run(c, k=0, linearize=True)
        lin_cost_list.append(cost)
        lin_xtraj_hist.append(x_hist)
        lin_utraj_hist.append(u_hist)
        lin_st_hist.append(st_hist)

    np.savetxt(args.dir + 'time.txt', sim.time)
    np.savetxt(args.dir + 'costs.txt', np.array([aff_cost_list,lin_cost_list]))
    np.savetxt(args.dir + 'aff_states.txt', np.array(aff_xtraj_hist).reshape(len(c_list), -1))
    np.savetxt(args.dir + 'aff_inputs.txt', np.array(aff_utraj_hist).reshape(len(c_list), -1))
    np.savetxt(args.dir + 'aff_solve_times.txt', np.array(aff_st_hist))

    np.savetxt(args.dir + 'lin_states.txt', np.array(lin_xtraj_hist).reshape(len(c_list), -1))
    np.savetxt(args.dir + 'lin_inputs.txt', np.array(lin_utraj_hist).reshape(len(c_list), -1))
    np.savetxt(args.dir + 'lin_solve_times.txt', np.array(lin_st_hist))

    np.savetxt(args.dir + 'ref_states.txt', xr_hist)

    plotter.plot(args.dir)


if __name__ == '__main__':
    main()
