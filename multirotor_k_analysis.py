import argparse
import numpy as np
import os
import matplotlib.pyplot as plt
from tqdm import tqdm

import examples.multirotor.trajectory as traj
from examples.multirotor.simulator import Simulator
from examples.multirotor.plotter import Plotter
# from examples.tabbed_plot_window import TabbedPlotWindow


def getParsedArgs():
    default_dir = '/tmp/ampc24/multirotor/k_analysis/'
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
    Q = np.array([1,1,1, 1,1,1, 1,1,1.])
    T = 100
    # reference_type = params['reference_type']
    # amplitude_deg = params['amplitude_deg']
    # amplitude = np.radians(amplitude_deg)
    # if reference_type != 'step':
    #     frequency_hz = params['frequency_hz']
    #     if type(frequency_hz) == str:
    #         frequency_hz = eval(frequency_hz)
    # k_list = np.arange(T)
    # k_list = np.arange(stop=T,step=5)
    # k_list = np.array([0,0,0])
    k_list = np.arange(2)
    # c_list = np.linspace(0,1,11)
    c_list = np.linspace(0,1,2)
    # c_list = [1.0]
    deg = True
    legend = True
    fontsize = 14
    fig_size = 800,600
    save = True
    image_type = 'svg'

    n,m = 9,4

    traj_fn = traj.EulerStateTrajectory(T, dt)
    ## step
    # traj_fn.setNorthMode(traj.Mode.STEP, [1.0])
    # traj_fn.setEastMode(traj.Mode.STEP, [1.0])
    # traj_fn.setDownMode(traj.Mode.STEP, [-22.0])
    # traj_fn.setYawMode(traj.Mode.STEP, [np.pi/2])
    ## high velocity
    # traj_fn.setNorthMode(traj.Mode.STEP, [0.0])
    # traj_fn.setEastMode(traj.Mode.LINE, [25.0, 0.0])
    # traj_fn.setDownMode(traj.Mode.STEP, [-20.0])
    # traj_fn.setYawMode(traj.Mode.STEP, [0.0])
    ## wavy
    traj_fn.setNorthMode(traj.Mode.SINE, [1.0, 2*np.pi/5, 0, 0])
    traj_fn.setEastMode(traj.Mode.LINE, [2.0, 0.0])
    traj_fn.setDownMode(traj.Mode.SINE, [1.0, 2*np.pi/5.0, 0.0, -20.0])
    traj_fn.setYawMode(traj.Mode.LINE, [np.pi/6, 0.0])

    sim = Simulator(tf, dt, T, Q, traj_fn.eval, k_list)

    all_costs = []
    min_costs = []
    min_c_list = []
    for kr in tqdm(k_list, desc='K Loop'):
        sim.k = kr
        cost_list = []
        for c in tqdm(c_list, desc='C Loop', leave=False):
            cost, x_hist, xr_hist, u_hist, st_hist = sim.run(x0, c)
            cost_list.append(cost)
        all_costs.append(cost_list)
        min_idx = np.argmin(cost_list)
        min_costs.append(cost_list[min_idx])
        min_c_list.append(c_list[min_idx])

    all_costs = np.array(all_costs)
    min_costs = np.array(min_costs)
    min_c_list = np.array(min_c_list)

    if save:
        np.savetxt(args.dir + 'all_costs.txt', all_costs)
        np.savetxt(args.dir + 'min_costs.txt', min_costs)
        np.savetxt(args.dir + 'min_c_values.txt', min_c_list)
        np.savetxt(args.dir + 'c_list.txt', c_list)

    k_list += 1

    plotter = Plotter(legend, deg, fontsize, fig_size)
    plotter.plotMinCosts(k_list, min_costs, min_c_list)
    plotter.plotCvK(c_list, k_list, all_costs)
    # pw = TabbedPlotWindow()
    # fig1,ax = plt.subplots(2)
    # a: plt.Axes = ax[0]
    # a.plot(k_list, min_costs)
    # a.set_ylabel(r'$\int$cost')
    # a: plt.Axes = ax[1]
    # a.plot(k_list, min_c_list, '.')
    # a.set_xlabel('k')
    # a.set_ylabel('c')
    # pw.addTab('min costs', fig1)

    # fig2,ax = plt.subplots(2)
    # a: plt.Axes = ax[0]
    # for i,c in enumerate(c_list):
    #     a.plot(k_list, all_costs.T[i], label=f'c = {c:.1f}')
    # a.set_xlabel('k')
    # a.set_ylabel(r'$\int$cost')
    # a.legend()
    # a: plt.Axes = ax[1]
    # for i,k in enumerate(k_list):
    #     a.plot(c_list, all_costs[i], label=f'k = {k}')
    # # a.plot(k_list, all_costs)
    # a.set_xlabel('c')
    # a.set_ylabel(r'$\int$cost')
    # a.legend()
    # pw.addTab('c vs k', fig2)

    plotter.show()

    if save:
        plotter.savePlots(args.dir, image_type='svg')
        plotter.savePlots(args.dir, image_type='pdf')
        # fig1.savefig(args.dir + 'min_costs.svg')
        # fig1.savefig(args.dir + 'min_costs.pdf')
        # fig2.savefig(args.dir + 'c_vs_k.svg')
        # fig2.savefig(args.dir + 'c_vs_k.pdf')
        # plotter.savePlots(args.dir, image_type='pdf')
    #     os.system(f'cp {param_path} {args.dir}params.yaml')

if __name__ == '__main__':
    main()
