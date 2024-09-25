import numpy as np
import matplotlib.pyplot as plt
import tqdm

import examples.single_link_arm.simulator as simulator
import examples.trajectory as traj
from parsing import getParsedArgs_run
import plot_arm_k_analysis as plotter


def main():
    default_dir = '/tmp/ampc24/arm/k_analysis/'
    desc = 'Run arm k analysis'
    ref_types = ['ramp', 'cos', 'step']
    args = getParsedArgs_run(default_dir, desc, ref_types)

    tf = 10.0
    dt = 0.01
    x0 = np.array([np.radians(0), 0.0])
    T = 100
    Q = np.array(args.weights) if args.weights is not None else np.ones(2)
    assert len(Q) == 2
    print(f'{Q = }')

    c_list = np.linspace(0, 1, 11)

    reference_type = args.ref_type
    if reference_type != 'step':
        k_list = np.arange(0, T)
    else:
        k_list = np.arange(1)

    print(f'{reference_type = }')
    if reference_type == 'step':
        default_params = [30.]
        params = args.params if len(args.params) != 0 else default_params
        assert len(params) == len(default_params)
        amplitude = np.radians(params[0])
        xr = np.array([amplitude, 0.0])
        traj_fn = traj.Step(xr, T)
        print(f'amplitude = radians({params[0]})')
    elif reference_type == 'cos':
        default_params = [60., 2.]
        params = args.params if len(args.params) != 0 else default_params
        assert len(params) == len(default_params)
        amplitude = np.radians(params[0])
        period = tf / params[1]
        frequency_hz = 1 / period
        offset = x0[0]
        traj_fn = traj.Sinusoidal(amplitude, frequency_hz, offset, T, dt, reference_type)
        print(f'amplitude = radians({params[0]:.1f}), period = tf/{params[1]:.1f}')
    elif reference_type == 'ramp':
        default_params = [10.]
        params = args.params if len(args.params) != 0 else default_params
        assert len(params) == len(default_params)
        vel = 2*np.pi / params[0]
        traj_fn = traj.Ramp(velocity=vel, offset=x0[0], horizon=T, dt=dt)
        print(f'ref = ramp: vel = 2pi/{params[0]:.1f}')
    else:
        raise ValueError(f'ref type must be in {ref_types}')

    sim = simulator.Simulator(tf, dt, T, Q, traj_fn, k_ref=0)

    aff_all_costs = []
    aff_min_costs = []
    aff_min_c_list = []

    lin_all_costs = []
    lin_min_costs = []
    lin_min_c_list = []

    c = np.random.rand()
    print(f'c init: {c}')
    _,_,_,_,_ = sim.run(x0, c, linearize=True)

    for k in tqdm.tqdm(k_list, desc='K Loop'):
        sim.k = k
        aff_cost_list = []
        lin_cost_list = []
        for c in tqdm.tqdm(c_list, desc='C Loop', leave=False):
            # cost, x_hist, xr_hist, u_hist, st_hist = sim.run(x0, c)
            cost, _, _, _, _ = sim.run(x0, c)
            aff_cost_list.append(cost)
            cost, _, _, _, _ = sim.run(x0, c, linearize=True)
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
