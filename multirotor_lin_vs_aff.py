import numpy as np
from examples.multirotor.simulator import Simulator
import examples.multirotor.trajectory as traj
from examples.multirotor.plotter import Plotter
from tqdm import tqdm
import yaml
import argparse
import os


def getParsedArgs():
    default_dir = '/tmp/ampc24/multirotor/tracking/'
    # default_param_file = 'default.yaml'
    # default_param_file = 'multi_cos60.py'

    parser = argparse.ArgumentParser(description='Run AMPC simulation analysis.')
    # parser.add_argument('params', nargs='?', type=str,
    #                     default=default_param_file,
    #                     help='Name of parameter YAML file.')
    parser.add_argument('-D', '--dir', type=str,
                        default=default_dir,
                        help='Specify path to directory where data will be saved.')
    parser.add_argument('-M', '--mkdirs', action='store_true',
                        help='Create DIR if it does not exist and is not the default.')
    parser.add_argument('-O', '--overwrite-dir', action='store_true',
                        help='Overwrite contents of DIR if it exists.')

    args = parser.parse_args()

    if not args.dir[-1] == '/':
        args.dir += '/'

    if not os.path.exists(args.dir):
        default = args.dir == default_dir
        if not default and not args.mkdirs:
            print(f'Directory does not exist: {args.dir}')
            ans = input('Create it? [Y/n]: ')
            if len(ans) == 0: ans = 'y'
            if not ans.startswith(('y','Y')):
                msg = f'Create {args.dir} first or use -M flag to create it.'
                raise NotADirectoryError(msg)
        os.makedirs(args.dir)
    else:
        if not args.overwrite_dir:
            ans = input(f'{args.dir} contains data. Do you wish to overwrite it? [Y/n]: ')
            if len(ans) == 0: ans = 'y'
            if not ans.startswith(('y','Y')):
                msg = f'Move contents of {args.dir} or choose a different DIR'
                raise FileExistsError(msg)
    print(f'Saving data to: {args.dir}')

    # if args.params[0] == '/':
    #     cwd = os.getcwd()
    #     l = len(cwd)
    #     if args.params[:l] == cwd: args.params = args.params[l+1:]
    # if args.params[:7] != 'params/':
    #     args.params = 'params/' + args.params
    # if not os.path.exists(args.params):
    #     ans = input(f'{args.params} does not exist. Do you wish to use default params? [Y/n]: ')
    #     if len(ans) == 0: ans = 'y'
    #     if not ans.startswith(('y','Y')):
    #         msg = f'Could not load params from {args.params}. Please select a valid param file from "params/" folder.'
    #         raise FileNotFoundError(msg)
    #     args.params = default_param_file

    return args

# ## Load Parameters
# param_path = args.params
# if param_path[:7] != 'params/':
#     param_path = 'params/' + param_path
# with open(param_path, 'r') as file:
#     params = yaml.full_load(file)
#     tf = params['tf']
#     dt = params['dt']
#     x0 = np.array([np.radians(params['pos0_deg']), params['vel0']])
#     Q = np.array(params['Q'])
#     T = params['T']
#     reference_type = params['reference_type']
#     amplitude_deg = params['amplitude_deg']
#     amplitude = np.radians(amplitude_deg)
#     if reference_type != 'step':
#         frequency_hz = params['frequency_hz']
#         if type(frequency_hz) == str:
#             frequency_hz = eval(frequency_hz)
#     k_ref = params['k_ref']
#     c_list = params['c']
#     deg = params['deg']
#     legend = params['legend']
#     fontsize = params['fontsize']
#     fig_size = params['fig_size']
#     if type(fig_size) == str:
#         fig_size = eval(fig_size)
#     save = params['save']
#     image_type = params['image_type']
def main():
    args = getParsedArgs()
    tf = 10.0
    dt = 0.02
    x0 = np.array([0,0,-20., 0,0,0, 0,0,0])
    # Q = np.array([1,1,100, 1,1,1, 2,2,2.], dtype=np.float64) # step
    # Q = np.array([1,1,10, 1,1,1, 1,1,1.], dtype=np.float64) # wavy
    # Q = np.array([1,1,10, 1,1,1, 2,2,2.], dtype=np.float64) # high velocity
    Q = np.array([1,1,10, 1,1,1, 2,2,2.], dtype=np.float64) # 3D ramp
    T = 100
    # reference_type = params['reference_type']
    # amplitude_deg = params['amplitude_deg']
    # amplitude = np.radians(amplitude_deg)
    # if reference_type != 'step':
    #     frequency_hz = params['frequency_hz']
    #     if type(frequency_hz) == str:
    #         frequency_hz = eval(frequency_hz)
    k_ref = 0
    # k_ref = np.arange(T)
    c_list = np.linspace(0,1,11)
    c_list = [0.0]*2
    deg = True
    legend = True
    fontsize = 14
    fig_size = 800,600
    save = True
    image_type = 'svg'

    n,m = 9,4

    traj_fn = traj.EulerStateTrajectory(T, dt)
    ## step
    # traj_fn.setNorthMode(traj.Mode.STEP, [x0[0] + 1.0])
    # traj_fn.setEastMode(traj.Mode.STEP, [x0[1] + 1.0])
    # traj_fn.setDownMode(traj.Mode.STEP, [x0[2] - 2.0])
    # traj_fn.setYawMode(traj.Mode.STEP, [x0[5] + np.pi/2])
    ## high 3D ramp
    traj_fn.setNorthMode(traj.Mode.LINE, [10., x0[0]])
    traj_fn.setEastMode(traj.Mode.LINE, [10., x0[1]])
    traj_fn.setDownMode(traj.Mode.LINE, [-10., x0[2]])
    traj_fn.setYawMode(traj.Mode.STEP, [x0[5]])
    ## high velocity
    # traj_fn.setNorthMode(traj.Mode.STEP, [x0[0]])
    # traj_fn.setEastMode(traj.Mode.LINE, [25.0, x0[1]])
    # traj_fn.setDownMode(traj.Mode.STEP, [x0[2]])
    # traj_fn.setYawMode(traj.Mode.STEP, [x0[5]])
    ## wavy
    # traj_fn.setNorthMode(traj.Mode.SINE, [1.0, 5, 0, x0[0]])
    # traj_fn.setEastMode(traj.Mode.LINE, [2.0, x0[1]])
    # traj_fn.setDownMode(traj.Mode.SINE, [1.0, 5.0, 0.0, x0[2]])
    # traj_fn.setYawMode(traj.Mode.LINE, [np.pi/6, x0[5]])

    # if reference_type == 'step':
    #     xr = np.array([amplitude, 0.0])
    #     traj_fn = traj.Step(xr, T)
    # else:
    #     traj_fn = traj.Sinusoidal(amplitude, frequency_hz, T, dt, reference_type)

    sim = Simulator(tf, dt, T, Q, traj_fn.eval, k_ref)
    plotter = Plotter(legend, deg, fontsize, fig_size)

    if type(c_list) == float:
        cost, x_hist, xr_hist, u_hist, st_hist = sim.run(x0, c_list)
        print('cost:', cost)
        plotter.plotStateLine(sim.time, x_hist, label='state')
        plotter.plotStateLine(sim.time, xr_hist, 'r--', label='ref')
        plotter.plotInputLine(sim.time, u_hist)
        plotter.plotSolveTimes(sim.time, st_hist)

        # if save:
        #     np.savetxt(args.dir + 'time.txt', sim.time)
        #     np.savetxt(args.dir + 'costs.txt', np.array([cost]))
        #     np.savetxt(args.dir + 'states.txt', x_hist)
        #     np.savetxt(args.dir + 'ref_states.txt', xr_hist)
        #     np.savetxt(args.dir + 'inputs.txt', u_hist)
        #     np.savetxt(args.dir + 'solve_times.txt', np.array(st_hist))

    else: # type(c_list) == list:
        aff_cost_list = []
        lin_cost_list = []
        aff_xtraj_hist = []
        lin_xtraj_hist = []
        aff_utraj_hist = []
        lin_utraj_hist = []
        aff_st_trials = []
        lin_st_trials = []
        plotter._setupCostPlot()
        for c in tqdm(c_list):
            cost, x_hist, xr_hist, u_hist, st_hist = sim.run(x0, c)
            aff_cost_list.append(cost)
            aff_xtraj_hist.append(x_hist)
            aff_utraj_hist.append(u_hist)
            aff_st_trials.append(st_hist)
            plotter.plotStateLine(sim.time, x_hist, label=f'aff: c = {c:.1f}')
            plotter.plotInputLine(sim.time, u_hist, label=f'aff: c = {c:.1f}')
            plotter.plotSolveTimes(sim.time, st_hist, label=f'aff: c = {c:.1f}')
            cost, x_hist, xr_hist, u_hist, st_hist = sim.run(x0, c, linearize=True)
            lin_cost_list.append(cost)
            lin_xtraj_hist.append(x_hist)
            lin_utraj_hist.append(u_hist)
            lin_st_trials.append(st_hist)
            plotter.plotStateLine(sim.time, x_hist, '-.', label=f'lin: c = {c:.1f}')
            plotter.plotInputLine(sim.time, u_hist, '-.', label=f'lin: c = {c:.1f}')
            plotter.plotSolveTimes(sim.time, st_hist, '-.', label=f'lin: c = {c:.1f}')
        plotter.plotCosts(c_list, aff_cost_list, '.', label='aff')
        plotter.plotCosts(c_list, lin_cost_list, '.', label='lin')
        plotter.plotStateLine(sim.time, xr_hist, 'r--', label='ref')

        if save:
            np.savetxt(args.dir + 'time.txt', sim.time)
            np.savetxt(args.dir + 'ref_states.txt', xr_hist)
            np.savetxt(args.dir + 'aff_costs.txt', np.array(aff_cost_list))
            np.savetxt(args.dir + 'aff_states.txt', np.array(aff_xtraj_hist).reshape(len(c_list), -1))
            np.savetxt(args.dir + 'aff_inputs.txt', np.array(aff_utraj_hist).reshape(len(c_list), -1))
            np.savetxt(args.dir + 'aff_solve_times.txt', np.array(aff_st_trials))
            np.savetxt(args.dir + 'lin_costs.txt', np.array(lin_cost_list))
            np.savetxt(args.dir + 'lin_states.txt', np.array(lin_xtraj_hist).reshape(len(c_list), -1))
            np.savetxt(args.dir + 'lin_inputs.txt', np.array(lin_utraj_hist).reshape(len(c_list), -1))
            np.savetxt(args.dir + 'lin_solve_times.txt', np.array(lin_st_trials))

        min_idx = np.argmin(aff_cost_list)
        print(f'Min cost: {aff_cost_list[min_idx]} at c = {c_list[min_idx]}')

    plotter.show()

    if save:
        plotter.savePlots(args.dir, image_type)
        plotter.savePlots(args.dir, image_type='pdf')
        # os.system(f'cp {param_path} {args.dir}params.yaml')

if __name__ == '__main__':
    main()
