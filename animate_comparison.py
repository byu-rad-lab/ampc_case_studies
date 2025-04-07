import numpy as np
import os
import matplotlib.pyplot as plt

from case_studies.animation import StackedAnimation
from case_studies.single_link_arm.animation import ArmAnimator
from case_studies.block_beam.animation import BlockBeamAnimator
from case_studies.cart_pendulum.animation import CartPendulumAnimator
from case_studies.multirotor.animation import MultirotorAnimator
from parsing import getParsedArgs_animate
import constants as C


def animate(load_dir: str, save_path: str, method:str|None, anchor_point: str,
            c_idx: int, k_idx: int):
    """
    Animate the results of AMPC simulations.

    Args:
        load_dir (str): Directory to load data from.
        save_path (str): Full path where animation will be saved.
        method (str|None): Method to use for animation.
        anchor_point (str): Anchor point for animation.
        c_idx (int): Index of c value [0-10] or -1 for best.
        k_idx (int): Index of k value [0-(T-1)] or -1 for best.
    """

    load_dir = os.path.expanduser(load_dir)
    with open(os.path.join(load_dir, 'system.txt'), 'r') as f:
        system = f.read()

    time = np.load(os.path.join(load_dir, 'time.npy'))
    xr_hist = np.load(os.path.join(load_dir, 'ref_states.npy'))
    x_hist = np.load(os.path.join(load_dir, 'states.npz'))
    costs = np.load(os.path.join(load_dir, 'costs.npz'))

    min_costs = np.empty(len(C.ANCHOR_POINTS))
    min_idx = {}
    for i, p in enumerate(C.ANCHOR_POINTS):
        min_idx[p] = np.unravel_index(np.argmin(costs[p]), costs[p].shape)
        min_costs[i] = costs[p][min_idx[p]]

    idx = np.argmin(min_costs)
    best_p = C.ANCHOR_POINTS[idx]
    best_idx = min_idx[best_p]
    states_top = x_hist[best_p][best_idx]

    print(f'Top: {best_p}, c={best_idx[1]/10:.1f}, k={best_idx[0]+1} \t Best Affinization')

    if method in C.METHODS:
        match method:
            case 'best_aff':
                anchor_point = best_p
                k_idx, c_idx = best_idx
                label_bot = "Best Affinization"
            case 'best_lin':
                anchor_point = C.ANCHOR_POINTS[-1]
                k_idx, c_idx = best_idx
                label_bot = "Best Linearization"
            case 'nom_aff':
                anchor_point = C.ANCHOR_POINTS[0]
                k_idx = 0
                c_idx = 0
                label_bot = "Nominal Affinization"
            case 'nom_lin':
                anchor_point = C.ANCHOR_POINTS[-1]
                k_idx = 0
                c_idx = 0
                label_bot = "Nominal Linearization"
            case _:
                raise ValueError(f'Invalid method: {method}')
        color_bot = C.COLORS[method]
    else:
        if c_idx == -1 and k_idx == -1:
            k_idx,c_idx = min_idx[anchor_point]
        elif c_idx == -1:
            c_idx = np.argmin(costs[anchor_point][k_idx])
        elif k_idx == -1:
            k_idx = np.argmin(costs[anchor_point][:,c_idx])
        color_bot = 'tab:gray'
        label_bot = 'Manual Selection'

    states_bot = x_hist[anchor_point][k_idx, c_idx]
    bot_info = f'{anchor_point}, c={c_idx/10:.1f}, k={k_idx+1} \t {label_bot}'
    print(f'Bot: {bot_info}')
    if label_bot == '':
        label_bot = bot_info

    states_top = states_top.T
    states_bot = states_bot.T
    xr_hist = xr_hist.T

    fig = plt.figure(figsize=(19.2,10.8), layout='tight')
    extra_fig_opts = {} # used to specify 3d axes for multirotor

    # default plot space settings
    wr = np.array([0.125, 1, 0.1, 1.5, 0.1])
    hr = np.array([1, 1, 0.05, 1, 1])
    ani_col = 1
    data_col = 3

    # default indices of x to plot next to animation
    data_idx = [0, 1]

    match system:
        case 'arm':
            Animator = ArmAnimator
            x_labels = [r'$\theta$ (deg)', r'$\dot{\theta}$ (rad/s)']
            wr = np.array([1, 1.5, 0.125])
            ani_col = 0
            data_col = 1
        case 'blockbeam':
            Animator = BlockBeamAnimator
            x_labels = ['z (m)', r'$\theta$ (deg)']
        case 'pendulum':
            Animator = CartPendulumAnimator
            Q = np.load(os.path.join(load_dir, 'Q.npy'))
            if Q[0] == 0.0: # controlling pendulum
                data_idx = [1, 3]
                x_labels = [r'$\theta$ (deg)', r'$\dot{\theta}$ (rad/s)']
            else: # controlling cart
                x_labels = ['z (m)', r'$\theta$ (deg)']
        case 'multirotor':
            Animator = MultirotorAnimator
            data_idx = [1, 2, 3]
            hr = np.array([1, 1, 1, 0.05, 1, 1, 1])
            x_labels = ['$p_y$ (m)', '$p_z$ (m)', r'$\phi$ (deg)']
            extra_fig_opts['projection'] = '3d'
        case _:
            raise ValueError(f"System {system} not recognized.")

    n = len(data_idx)
    gs = fig.add_gridspec(len(hr), len(wr), width_ratios=wr, height_ratios=hr)
    ani_axes = [fig.add_subplot(gs[:n,ani_col], **extra_fig_opts),
                fig.add_subplot(gs[-n:,ani_col], **extra_fig_opts)]
    data_axes = [[fig.add_subplot(gs[i,data_col]) for i in range(n)],
                    [fig.add_subplot(gs[-i,data_col]) for i in range(n,0,-1)]]

    x_hists = [states_top, states_bot]
    colors = [C.COLORS[0], color_bot]
    labels = ['Best Affinization', label_bot]

    ani = StackedAnimation(Animator, fig, ani_axes, data_axes, time, x_hists,
                           data_idx, x_labels, xr_hist, colors, labels)

    if save_path is not None:
        save_path = os.path.expanduser(save_path)
        ani.save(save_path)
        print(f'Saved animation to {save_path}')
    else:
        ani.animate()

def main():
    default_dir = '/tmp/ampc24/analysis/'
    desc = '''
        AniMate stacked AMPC simulations. The top animation is the best affinization and the bottom defaults to be nominal linearization, but a different modeling method can be manually selected.
        '''
    args = getParsedArgs_animate(default_dir, desc)
    load_dir = args.dir
    method =  args.method
    save_path = args.save_path
    approx_pt = f'({args.xp},{args.up})'
    c_idx = args.c_idx
    if args.k is None:
        args.k = -1
    k_idx = args.k - 1 if args.k > 0 else -1
    animate(load_dir, save_path, method, approx_pt, c_idx, k_idx)

if __name__ == '__main__':
    main()
