import numpy as np
import matplotlib.pyplot as plt
from examples.single_link_arm.plotter import Plotter
import yaml
import argparse


parser = argparse.ArgumentParser(description='Run AMPC simulation analysis.')
parser.add_argument('dir', nargs='?', type=str, default='/tmp/ampc24_paper/',
                    help='Specify path to directory from which to load data.')
args = parser.parse_args()

if not args.dir[-1] == '/':
    args.dir += '/'
print('Save path:', args.dir)

## Load Parameters
param_path = args.dir + 'params.yaml'
with open(param_path, 'r') as file:
    params = yaml.full_load(file)
    c_list = params['c']
    deg = params['deg']
    legend = params['legend']
    fontsize = params['fontsize']
    fig_size = params['fig_size']
    if type(fig_size) == str:
        fig_size = eval(fig_size)
    save = params['save']
    image_type = params['image_type']

## Load Data
time = np.loadtxt(args.dir + 'time.txt')
costs = np.loadtxt(args.dir + 'costs.txt')
xtraj_hist = np.loadtxt(args.dir + 'states.txt')
xr_hist = np.loadtxt(args.dir + 'ref_states.txt')
utraj_hist = np.loadtxt(args.dir + 'inputs.txt')
solve_times = np.loadtxt(args.dir + 'solve_times.txt')


plotter = Plotter(time, legend, deg, fontsize, fig_size)

if type(c_list) == float:
    plotter.plotStateLine(xtraj_hist, label='state')
    plotter.plotStateLine(xr_hist, 'r--', label='ref')
    plotter.plotInputLine(utraj_hist)
    plotter.plotSolveTimes(solve_times)
elif type(c_list) == list:
    xtraj_hist = xtraj_hist.reshape((len(c_list), -1, 2))
    plotter.plotCosts(c_list, costs)
    for i in range(len(c_list)):
        plotter.plotStateLine(xtraj_hist[i], label=f'c = {c_list[i]:.1f}')
    plotter.plotStateLine(xr_hist, 'r--', label='ref')

plotter.show()

if save:
    plotter.savePlots(args.dir, image_type)
