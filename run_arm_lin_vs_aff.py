import numpy as np
from tqdm import tqdm

import examples.single_link_arm.simulator as simulator
import examples.trajectory as traj
import plot_arm_lin_vs_aff as plotter
from parsing import getParsedArgs_run


def main():
    save_dir = f'/tmp/ampc24/arm/lin_vs_aff/'
    desc = 'Run linearization vs affinization comparison for single link arm'
    ref_types = ['step', 'ramp', 'cos']
    args = getParsedArgs_run(save_dir, desc, ref_types)

    tf = 10.0
    dt = 0.01
    x0 = np.array([np.radians(0), 0.0])
    T = 100
    Q = np.array(args.weights) if args.weights is not None else np.ones(2)
    assert len(Q) == 2
    print(f'{Q = }')

    k_ref = 0
    c_list = np.linspace(0, 1, 11)
    # c_list = np.array([0.1, 0.1])

    reference_type = args.ref_type
    print(f'{reference_type = }: ', end='')
    if reference_type == 'step':
        # Q = np.array([1.0, 1.0])
        default_params = [30.]
        params = args.params if len(args.params) != 0 else default_params
        assert len(params) == len(default_params)
        amplitude = np.radians(params[0])
        xr = np.array([amplitude, 0.0])
        traj_fn = traj.Step(xr, T)
        print(f'amplitude = radians({params[0]})')
    elif reference_type == 'cos':
        # Q = np.array([1.0, 1.0])
        # Q = np.array([1.0, 0.1])
        # Q = np.array([1.0, 0.01])
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
        # Q = np.array([1.0, 1.0])
        # Q = np.array([1.0, 0.1])
        # Q = np.array([1.0, 0.01])
        default_params = [10.]
        params = args.params if len(args.params) != 0 else default_params
        assert len(params) == len(default_params)
        vel = 2*np.pi / params[0]
        traj_fn = traj.Ramp(velocity=vel, offset=x0[0], horizon=T, dt=dt)
        print(f'ref = ramp: vel = 2pi/{params[0]:.1f}')
    else:
        raise ValueError(f'ref type must be in {ref_types}')

    sim = simulator.Simulator(tf, dt, T, Q, traj_fn, k_ref)

    aff_cost_list = []
    lin_cost_list = []
    aff_xtraj_hist = []
    lin_xtraj_hist = []
    aff_utraj_hist = []
    lin_utraj_hist = []
    aff_st_trials = []
    lin_st_trials = []
    c = np.random.rand()
    print(f'c init: {c}')
    _,_,_,_,_ = sim.run(x0, c, linearize=True)
    for c in tqdm(c_list):
        cost, x_hist, xr_hist, u_hist, st_hist = sim.run(x0, c)
        aff_cost_list.append(cost)
        aff_xtraj_hist.append(x_hist)
        aff_utraj_hist.append(u_hist)
        aff_st_trials.append(st_hist)
        cost, x_hist, xr_hist, u_hist, st_hist = sim.run(x0, c, linearize=True)
        lin_cost_list.append(cost)
        lin_xtraj_hist.append(x_hist)
        lin_utraj_hist.append(u_hist)
        lin_st_trials.append(st_hist)

    np.savetxt(args.dir + 'time.txt', sim.time)
    np.savetxt(args.dir + 'costs.txt', np.array([aff_cost_list,lin_cost_list]))
    np.savetxt(args.dir + 'aff_states.txt', np.array(aff_xtraj_hist).reshape(len(c_list), -1))
    np.savetxt(args.dir + 'lin_states.txt', np.array(lin_xtraj_hist).reshape(len(c_list), -1))
    np.savetxt(args.dir + 'ref_states.txt', xr_hist)
    # np.savetxt(args.dir + 'inputs.txt', np.array(aff_utraj_hist).reshape(len(c_list), -1))
    # np.savetxt(args.dir + 'solve_times.txt', np.array(aff_st_trials))

    plotter.plot(args.dir)


if __name__ == '__main__':
    main()
