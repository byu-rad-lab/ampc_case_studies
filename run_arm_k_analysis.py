import numpy as np
import matplotlib.pyplot as plt
import importlib
import yaml
import argparse
import os
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
    Q = np.array([1.0, 1.0])
    T = 100

    c_list = np.linspace(0, 1, 11)

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
        vel = 2*np.pi / 2.5
        traj_fn = traj.Ramp(velocity=vel, offset=x0[0], horizon=T, dt=dt)
    else:
        raise ValueError(f'ref type must be in {ref_types}')

    sim = simulator.Simulator(tf, dt, T, Q, traj_fn, k_ref=0)

    all_costs = []
    min_costs = []
    min_c_list = []
    if reference_type != 'step':
        k_list = np.arange(0, T)
    else:
        k_list = np.arange(1)

    for k in tqdm.tqdm(k_list):
        sim.k = k
        cost_list = []
        for c in c_list:
            # cost, x_hist, xr_hist, u_hist, st_hist = sim.run(x0, c)
            cost, _, _, _, _ = sim.run(x0, c)
            cost_list.append(cost)
        all_costs.append(cost_list)
        min_idx = np.argmin(cost_list)
        min_costs.append(cost_list[min_idx])
        min_c_list.append(c_list[min_idx])

    all_costs = np.array(all_costs)
    min_costs = np.array(min_costs)
    min_c_list = np.array(min_c_list)

    np.savetxt(args.dir + 'all_costs.txt', np.array(all_costs))
    np.savetxt(args.dir + 'min_costs.txt', np.array(min_costs))
    np.savetxt(args.dir + 'min_c_values.txt', np.array(min_c_list))
    np.savetxt(args.dir + 'c_list.txt', c_list)
    np.savetxt(args.dir + 'k_list.txt', k_list)

    plotter.plot(args.dir)
    return


if __name__ == '__main__':
    main()
