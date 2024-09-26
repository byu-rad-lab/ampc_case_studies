import numpy as np

import examples.single_link_arm.simulator as simulator
from parsing import getParsedArgs_run
import plot_arm_tracking as plotter


def main():
    save_dir = '/tmp/ampc24/arm/tracking/'
    desc = 'Run tracking for single link arm'
    ref_types = ['step', 'ramp', 'cos']
    args = getParsedArgs_run(save_dir, desc, ref_types)

    sim = simulator.getSimulator(args)

    # k_ref = 0
    # c_list = np.linspace(0, 1, 11)
    k_list = [0, 10]
    c_list = [0, 1.]

    cost_list = []
    xtraj_hist = []
    utraj_hist = []

    c = np.random.rand()
    print(f'c init: {c}')
    _,_,_,_,_ = sim.run(c, k=0, linearize=True)

    for c,k in zip(c_list, k_list):
        cost, x_hist, xr_hist, u_hist, st_hist = sim.run(c, k, linearize=False)
        cost_list.append(cost)
        xtraj_hist.append(x_hist)
        utraj_hist.append(u_hist)

    np.savetxt(args.dir + 'time.txt', sim.time)
    np.savetxt(args.dir + 'costs.txt', np.array(cost_list))
    np.savetxt(args.dir + 'states.txt', np.array(xtraj_hist).reshape(len(c_list), -1))
    np.savetxt(args.dir + 'ref_states.txt', xr_hist)
    np.savetxt(args.dir + 'inputs.txt', np.array(utraj_hist).reshape(len(c_list), -1))
    np.savetxt(args.dir + 'k_list.txt', np.array(k_list))
    np.savetxt(args.dir + 'c_list.txt', np.array(c_list))

    plotter.plot(args.dir)
    return


if __name__ == '__main__':
    main()
