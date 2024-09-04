import numpy as np
import matplotlib.pyplot as plt
import examples.single_link_arm.simulator as simulator
import examples.trajectory as traj
# from examples.single_link_arm.plotter import Plotter
import importlib
from params.params import Params
import yaml
import argparse
import os
import tqdm

def getParsedArgs():
    default_dir = '/tmp/ampc24/k_analysis/'
    default_param_file = 'default.yaml'
    default_param_file = 'multi_cos60.py'

    parser = argparse.ArgumentParser(description='Run AMPC simulation analysis.')
    parser.add_argument('params', nargs='?', type=str,
                        default=default_param_file,
                        help='Name of parameter YAML file.')
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

    if args.params[0] == '/':
        cwd = os.getcwd()
        l = len(cwd)
        if args.params[:l] == cwd: args.params = args.params[l+1:]
    if args.params[:7] != 'params/':
        args.params = 'params/' + args.params
    if not os.path.exists(args.params):
        ans = input(f'{args.params} does not exist. Do you wish to use default params? [Y/n]: ')
        if len(ans) == 0: ans = 'y'
        if not ans.startswith(('y','Y')):
            msg = f'Could not load params from {args.params}. Please select a valid param file from "params/" folder.'
            raise FileNotFoundError(msg)
        args.params = default_param_file

    return args

def getParams(param_path: str) -> Params:
    print(f'Using params from: {param_path}')
    if param_path[-3:] == '.py':
        param_path = param_path[:-3]
    param_path = param_path.replace('/', '.')
    params: Params = importlib.import_module(param_path).params
    return params

def main():
    args = getParsedArgs()
    p: Params = getParams(args.params)
    p.c_list = np.linspace(0, 1, 11)

    if p.reference_type == Params.ReferenceType.STEP:
        xr = np.array([p.amplitute, 0.0])
        traj_fn = traj.Step(xr, p.T)
    else:
        traj_fn = traj.Sinusoidal(p.amplitute, p.frequency_hz, p.T, p.dt, p.reference_type.name.lower())

    sim = simulator.Simulator(p.tf, p.dt, p.T, p.Q, traj_fn, p.k_ref)

    all_costs = []
    min_costs = []
    min_c_list = []
    if p.reference_type is not Params.ReferenceType.STEP:
        k_list = np.arange(0, p.T)
    else: k_list = np.arange(1)
    for k in tqdm.tqdm(k_list):
        sim.k = k
        # if type(p.c_list) is float:
        #     cost, x_hist, xr_hist, u_hist, st_hist = sim.run(p.x0, p.c_list)
        #     min_costs.append(cost)
        #     min_c_list.append(p.c_list)

        # elif type(c_list) == list:
        # else:# type(c_list) == list:
        cost_list = []
        for c in p.c_list:
            cost, x_hist, xr_hist, u_hist, st_hist = sim.run(p.x0, c)
            cost_list.append(cost)
        all_costs.append(cost_list)
        min_idx = np.argmin(cost_list)
        min_costs.append(cost_list[min_idx])
        min_c_list.append(p.c_list[min_idx])

    all_costs = np.array(all_costs)
    min_costs = np.array(min_costs)
    min_c_list = np.array(min_c_list)

    if p.save:
        np.savetxt(args.dir + 'all_costs.txt', np.array(all_costs))
        np.savetxt(args.dir + 'min_costs.txt', np.array(min_costs))
        np.savetxt(args.dir + 'min_c_values.txt', np.array(min_c_list))
        np.savetxt(args.dir + 'c_list.txt', p.c_list)
        # os.system(f'cp {args.params} {args.dir}params.yaml')
        os.system(f'echo "{str(p)}" > {args.dir}params.yaml')

    k_list += 1

    fig,ax = plt.subplots(2)
    a: plt.Axes = ax[0]
    a.plot(k_list, min_costs)
    a.set_ylabel(r'$\int$cost')
    a: plt.Axes = ax[1]
    a.plot(k_list, min_c_list, '.')
    a.set_xlabel('k')
    a.set_ylabel('c')

    fig,ax = plt.subplots(2)
    a: plt.Axes = ax[0]
    for i in range(len(p.c_list)):
        a.plot(k_list, all_costs.T[i], label=f'c = {p.c_list[i]:.1f}')
    # a.plot(k_list, all_costs)
    a.set_xlabel('k')
    a.set_ylabel(r'$\int$cost')
    a.legend()
    a: plt.Axes = ax[1]
    for i in range(len(k_list)):
        a.plot(p.c_list, all_costs[i], label=f'k = {k_list[i]}')
    # a.plot(k_list, all_costs)
    a.set_xlabel('c')
    a.set_ylabel(r'$\int$cost')
    a.legend()

    plt.show()

if __name__ == '__main__':
    main()
