import numpy as np
from tqdm import tqdm

from examples.multirotor.simulator import Simulator
import examples.multirotor.trajectory as traj
import plot_multirotor_lin_vs_aff as plotter
from parsing import getParsedArgs_run


def main():
    default_dir = '/tmp/ampc24/multirotor/lin_vs_aff/'
    description='Run AMPC simulation analysis.'
    ref_types = ['step', 'wavy', 'ramp1', 'ramp3']
    args = getParsedArgs_run(default_dir, description, ref_types)

    tf = 10.0
    dt = 0.02
    T = 100
    x0 = np.array([0,0,-20., 0,0,0, 0,0,0])

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

    k_ref = 0
    c_list = np.linspace(0,1,11)
    # c_list = [0.0]*2

    deg = True
    legend = True
    fontsize = 12
    fig_size = 1000,800
    save = True
    image_type = 'svg'

    sim = Simulator(tf, dt, T, Q, traj_fn.eval, k_ref)

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
    _,_,_,_,_ = sim.run(x0, c, method='lin')
    for c in tqdm(c_list):
        cost, x_hist, xr_hist, u_hist, st_hist = sim.run(x0, c, method='uk')
        aff_uk_cost_list.append(cost)
        aff_uk_xtraj_hist.append(x_hist)
        aff_uk_utraj_hist.append(u_hist)
        aff_uk_st_trials.append(st_hist)
        cost, x_hist, xr_hist, u_hist, st_hist = sim.run(x0, c, method='ueq')
        aff_ueq_cost_list.append(cost)
        aff_ueq_xtraj_hist.append(x_hist)
        aff_ueq_utraj_hist.append(u_hist)
        aff_ueq_st_trials.append(st_hist)
        cost, x_hist, xr_hist, u_hist, st_hist = sim.run(x0, c, method='xeq')
        aff_xeq_cost_list.append(cost)
        aff_xeq_xtraj_hist.append(x_hist)
        aff_xeq_utraj_hist.append(u_hist)
        aff_xeq_st_trials.append(st_hist)
        cost, x_hist, xr_hist, u_hist, st_hist = sim.run(x0, c, method='lin')
        lin_cost_list.append(cost)
        lin_xtraj_hist.append(x_hist)
        lin_utraj_hist.append(u_hist)
        lin_st_trials.append(st_hist)

    if save:
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
