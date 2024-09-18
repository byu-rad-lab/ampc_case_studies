import numpy as np
from tqdm import tqdm

import examples.multirotor.trajectory as traj
from examples.multirotor.simulator import Simulator
from parsing import getParsedArgs_run
import plot_multirotor_k_analysis as plotter


def main():
    default_dir = '/tmp/ampc24/multirotor/k_analysis/'
    desc = 'Run multirotor k analysis'
    ref_types = ['wavy', 'ramp1', 'ramp3', 'step']
    args = getParsedArgs_run(default_dir, desc, ref_types)

    tf = 10.0
    dt = 0.02
    x0 = np.array([0,0,-20., 0,0,0, 0,0,0])
    T = 100
    k_increment = 1

    traj_fn = traj.EulerStateTrajectory(T, dt)
    if args.ref_type == 'step':
        Q = np.array([1,1,100, 1,1,1, 2,2,2.], dtype=np.float64)
        default_params = [1.0, 2.0]
        params = args.params if len(args.params) != 0 else default_params
        assert len(params) == len(default_params)
        pos_step = params[0]
        yaw_step = np.pi / params[1]
        traj_fn.setNorthMode(traj.Mode.STEP, [x0[0] + pos_step])
        traj_fn.setEastMode(traj.Mode.STEP, [x0[1] + pos_step])
        traj_fn.setDownMode(traj.Mode.STEP, [x0[2] - pos_step])
        traj_fn.setYawMode(traj.Mode.STEP, [x0[5] + yaw_step])
        print(f'ref = step: pos amplitude = {pos_step:.1f}, yaw amplitude = pi/{params[1]:.1f}')
    elif args.ref_type == 'wavy':
        # Q = np.array([1,1,10, 1,1,1, 1,1,1.], dtype=np.float64)
        # Q = np.array([1,1,10, 1,1,1, 2,2,2.], dtype=np.float64)
        Q = np.array([1,1,10, 1,1,1, 1,1,1.], dtype=np.float64)
        default_params = [1., 5., 2., 6.]
        params = args.params if len(args.params) != 0 else default_params
        assert len(params) == len(default_params)
        amp = params[0]
        period = params[1]
        evel = params[2]
        yvel = np.pi/params[3]
        traj_fn.setNorthMode(traj.Mode.SINE, [amp, period, 0, x0[0]])
        traj_fn.setEastMode(traj.Mode.LINE, [evel, x0[1]])
        traj_fn.setDownMode(traj.Mode.SINE, [amp, period, 0.0, x0[2]])
        traj_fn.setYawMode(traj.Mode.LINE, [yvel, x0[5]])
        print(f'ref = wavy: n/d amp = {amp:.1f}, n/d period = {period:.1f}, ', end='')
        print(f'e vel = {evel:.1f}, y vel = pi/{params[3]:.1f}')
    elif args.ref_type == 'ramp1':
        # Q = np.array([1,1,10, 1,1,1, 1,1,1.], dtype=np.float64)
        Q = np.array([1,1,10, 1,1,1, 2,2,2.], dtype=np.float64)
        default_params = [5.0]
        params = args.params if len(args.params) != 0 else default_params
        assert len(params) == len(default_params)
        vel = params[0]
        traj_fn.setNorthMode(traj.Mode.STEP, [x0[0]])
        traj_fn.setEastMode(traj.Mode.LINE, [vel, x0[1]])
        traj_fn.setDownMode(traj.Mode.STEP, [x0[2]])
        traj_fn.setYawMode(traj.Mode.STEP, [x0[5]])
        print(f'ref = ramp1: e vel = {vel:.1f}')
    elif args.ref_type == 'ramp3':
        # Q = np.array([1,1,10, 1,1,1, 2,2,2.], dtype=np.float64) # bad Q
        Q = np.array([1,1,1, 1,1,1, 2,2,2.], dtype=np.float64)
        default_params = [3.0]
        params = args.params if len(args.params) != 0 else default_params
        assert len(params) == len(default_params)
        vel = params[0]
        traj_fn.setNorthMode(traj.Mode.LINE, [vel, x0[0]])
        traj_fn.setEastMode(traj.Mode.LINE, [vel, x0[1]])
        traj_fn.setDownMode(traj.Mode.LINE, [-vel, x0[2]])
        traj_fn.setYawMode(traj.Mode.STEP, [x0[5]])
        print(f'ref = ramp3: n/e/d vel = {vel:.1f}')

    if args.weights is not None:
        Q = np.array(args.weights)
        print('Q =', Q)

    if args.ref_type != 'step':
        T_idx = 15
        k_list = np.array([*np.arange(0, T_idx), *np.arange(T_idx, T, k_increment)])
    else:
        k_list = np.arange(1)
    c_list = np.linspace(0,1,11)
    # c_list = np.linspace(0,1,2)
    # c_list = [1.0]

    sim = Simulator(tf, dt, T, Q, traj_fn.eval, k_list)

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
        sim.k = kr
        aff_ueq_cost_list = []
        aff_uk_cost_list = []
        aff_xeq_cost_list = []
        lin_cost_list = []
        for c in tqdm(c_list, desc='C Loop', leave=False):
            cost, x_hist, xr_hist, u_hist, st_hist = sim.run(x0, c, 'ueq')
            aff_ueq_cost_list.append(cost)
            cost, x_hist, xr_hist, u_hist, st_hist = sim.run(x0, c, 'uk')
            aff_uk_cost_list.append(cost)
            cost, x_hist, xr_hist, u_hist, st_hist = sim.run(x0, c, 'xeq')
            aff_xeq_cost_list.append(cost)
            cost, x_hist, xr_hist, u_hist, st_hist = sim.run(x0, c, 'lin')
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
