import numpy as np
# import matplotlib.pyplot as plt
import examples.single_link_arm.simulator as simulator
import examples.trajectory as traj
from examples.trajectory1d import Trajectory1D, Mode
from examples.single_link_arm.plotter import Plotter
import yaml
import argparse
import os


parser = argparse.ArgumentParser(description='Run AMPC simulation analysis.')
parser.add_argument('params', nargs='?', type=str, default='default.yaml',
                    help='Name of parameter YAML file.')
parser.add_argument('-D', '--dir', type=str, default='/tmp/ampc24/arm/tracking',
                    help='Specify path to directory from which to save data.')
parser.add_argument('-M', '--mkdirs', action='store_true',
                    help='Create directory DIR if it does not exist already.')
args = parser.parse_args()

if not args.dir[-1] == '/':
    args.dir += '/'
print('Save path:', args.dir)

if not os.path.exists(args.dir):
    if not args.mkdirs:
        msg = f'Directory does not exist: {args.dir}\n'
        msg += 'Create it first or use -M flag to create it.'
        raise OSError(msg)
    os.makedirs(args.dir)

## Load Parameters
param_path = args.params
if param_path[:7] != 'params/':
    param_path = 'params/' + param_path
with open(param_path, 'r') as file:
    params = yaml.full_load(file)
    tf = params['tf']
    dt = params['dt']
    x0 = np.array([np.radians(params['pos0_deg']), params['vel0']])
    Q = np.array(params['Q'])
    T = params['T']
    reference_type = params['reference_type']
    amplitude_deg = params['amplitude_deg']
    amplitude = np.radians(amplitude_deg)
    if reference_type != 'step':
        frequency_hz = params['frequency_hz']
        if type(frequency_hz) == str:
            frequency_hz = eval(frequency_hz)
    k_ref = params['k_ref']
    c_list = params['c']
    deg = params['deg']
    legend = params['legend']
    fontsize = params['fontsize']
    fig_size = params['fig_size']
    if type(fig_size) == str:
        fig_size = eval(fig_size)
    save = params['save']
    image_type = params['image_type']

if reference_type == 'step':
    xr = np.array([amplitude, 0.0])
    traj_fn = traj.Step(xr, T)
else:
    traj_fn = traj.Sinusoidal(amplitude, frequency_hz, T, dt, reference_type)

traj_fn = Trajectory1D(Mode.LINE, params=[np.pi/2, 0]).eval()

sim = simulator.Simulator(tf, dt, T, Q, traj_fn, k_ref)
plotter = Plotter(sim.time, legend, deg, fontsize, fig_size)

if type(c_list) == float:
    cost, x_hist, xr_hist, u_hist, st_hist = sim.run(x0, c_list)
    print('cost:', cost)
    plotter.plotStateLine(x_hist, label='state')
    plotter.plotStateLine(xr_hist, 'r--', label='ref')
    plotter.plotInputLine(u_hist)
    plotter.plotSolveTimes(st_hist)

    if save:
        np.savetxt(args.dir + 'time.txt', sim.time)
        np.savetxt(args.dir + 'costs.txt', np.array([cost]))
        np.savetxt(args.dir + 'states.txt', x_hist)
        np.savetxt(args.dir + 'ref_states.txt', xr_hist)
        np.savetxt(args.dir + 'inputs.txt', u_hist)
        np.savetxt(args.dir + 'solve_times.txt', np.array(st_hist))

else: # type(c_list) == list:
    cost_list = []
    xtraj_hist = []
    utraj_hist = []
    st_trials = []
    for c in c_list:
        cost, x_hist, xr_hist, u_hist, st_hist = sim.run(x0, c)
        cost_list.append(cost)
        xtraj_hist.append(x_hist)
        utraj_hist.append(u_hist)
        st_trials.append(st_hist)
    plotter.plotCosts(c_list, cost_list)
    for i in range(len(c_list)):
        plotter.plotStateLine(xtraj_hist[i], label=f'c = {c_list[i]}')
    plotter.plotStateLine(xr_hist, 'r--', label='ref')

    if save:
        np.savetxt(args.dir + 'time.txt', sim.time)
        np.savetxt(args.dir + 'costs.txt', np.array(cost_list))
        np.savetxt(args.dir + 'states.txt', np.array(xtraj_hist).reshape(len(c_list), -1))
        np.savetxt(args.dir + 'ref_states.txt', xr_hist)
        np.savetxt(args.dir + 'inputs.txt', np.array(utraj_hist).reshape(len(c_list), -1))
        np.savetxt(args.dir + 'solve_times.txt', np.array(st_trials))

    min_idx = np.argmin(cost_list)
    print(f'Min cost: {cost_list[min_idx]} at c = {c_list[min_idx]}')

plotter.show()

if save:
    plotter.savePlots(args.dir, image_type='pdf')
    os.system(f'cp {param_path} {args.dir}params.yaml')
