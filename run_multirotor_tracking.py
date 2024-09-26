import numpy as np
from tqdm import tqdm

import examples.multirotor.simulator as Simulator
import plot_multirotor_tracking as plotter
from parsing import getParsedArgs_run


def main():
    default_dir = '/tmp/ampc24/multirotor/tracking/'
    desc = 'Run tracking for multirotor'
    ref_types = ['step', 'wavy', 'ramp1', 'ramp3']
    args = getParsedArgs_run(default_dir, desc, ref_types)

    sim = Simulator.getSimulator(args)

    ### Change these 3 lines (keep the same number of elements in each list)
    c_list = [0, 1]
    k_list = [0, 0]
    method_list = ['uk', 'uk']

    cost_list = []
    xtraj_hist = []
    utraj_hist = []
    c = np.random.rand()
    print(f'c init: {c}')
    _,_,_,_,_ = sim.run(c, k=0, method='lin')
    for c,k,method in tqdm(zip(c_list, k_list, method_list)):
        cost, x_hist, xr_hist, u_hist, _ = sim.run(c, k, method)
        cost_list.append(cost)
        xtraj_hist.append(x_hist)
        utraj_hist.append(u_hist)

    np.savetxt(args.dir + 'c_list.txt', c_list)
    np.savetxt(args.dir + 'k_list.txt', k_list)
    with open(args.dir + 'method_list.txt', 'w') as f:
        for method in method_list:
            f.write(f'{method}\n')

    np.savetxt(args.dir + 'time.txt', sim.time)
    np.savetxt(args.dir + 'costs.txt', np.array(cost_list))
    np.savetxt(args.dir + 'states.txt', np.array(xtraj_hist).reshape(len(c_list), -1))
    np.savetxt(args.dir + 'ref_states.txt', xr_hist)
    np.savetxt(args.dir + 'inputs.txt', np.array(utraj_hist).reshape(len(c_list), -1))

    plotter.plot(args.dir)
    return


if __name__ == '__main__':
    main()
