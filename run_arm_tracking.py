import numpy as np

import examples.single_link_arm.simulator as simulator
import examples.trajectory as traj
from parsing import getParsedArgs_run
import plot_arm_tracking as plotter


def main():
    save_dir = f'/tmp/ampc24/arm/tracking/'
    desc = 'Run tracking for single link arm'
    ref_types = ['step', 'ramp', 'cos']
    args = getParsedArgs_run(save_dir, desc, ref_types)

    tf = 10.0
    dt = 0.01
    x0 = np.array([np.radians(0), 0.0])
    Q = np.array([1.0, 1.0])
    T = 100

    legend = True
    deg = True
    fontsize = 14
    fig_size = (1000,800)

    # k_ref = 0
    # c_list = np.linspace(0, 1, 11)
    k_list = [0, 10]
    c_list = [0, 1.]

    reference_type = args.ref_type
    print(f'{reference_type = }')
    if reference_type == 'step':
        amplitude = np.radians(30)
        xr = np.array([amplitude, 0.0])
        traj_fn = traj.Step(xr, T)
    elif reference_type == 'cos':
        amplitude = np.radians(90)
        period = tf / 4
        frequency_hz = 1 / period
        traj_fn = traj.Sinusoidal(amplitude, frequency_hz, T, dt, reference_type)
    elif reference_type == 'ramp':
        vel = 2*np.pi / 7.5
        traj_fn = traj.Ramp(velocity=vel, offset=x0[0], horizon=T, dt=dt)
    else:
        raise ValueError(f'ref type must be in {ref_types}')

    sim = simulator.Simulator(tf, dt, T, Q, traj_fn, k_ref=0)

    cost_list = []
    xtraj_hist = []
    utraj_hist = []
    st_trials = []
    for c,k in zip(c_list, k_list):
        sim.k = k
        cost, x_hist, xr_hist, u_hist, st_hist = sim.run(x0, c)
        cost_list.append(cost)
        xtraj_hist.append(x_hist)
        utraj_hist.append(u_hist)
        st_trials.append(st_hist)

    np.savetxt(args.dir + 'time.txt', sim.time)
    np.savetxt(args.dir + 'costs.txt', np.array(cost_list))
    np.savetxt(args.dir + 'states.txt', np.array(xtraj_hist).reshape(len(c_list), -1))
    np.savetxt(args.dir + 'ref_states.txt', xr_hist)
    np.savetxt(args.dir + 'inputs.txt', np.array(utraj_hist).reshape(len(c_list), -1))
    # np.savetxt(args.dir + 'solve_times.txt', np.array(st_trials))
    np.savetxt(args.dir + 'k_list.txt', np.array(k_list))
    np.savetxt(args.dir + 'c_list.txt', np.array(c_list))

    plotter.plot(args.dir)
    return


if __name__ == '__main__':
    main()
