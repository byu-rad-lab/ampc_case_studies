import numpy as np
# from tqdm import tqdm
import os
import matplotlib.pyplot as plt
# import matplotlib.animation as animation

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

    aff_uk_costs = np.load(os.path.join(load_dir, 'aff_uk_costs.npy'))
    aff_ueq_costs = np.load(os.path.join(load_dir, 'aff_ueq_costs.npy'))
    aff_xeq_costs = np.load(os.path.join(load_dir, 'aff_xeq_costs.npy'))
    lin_costs = np.load(os.path.join(load_dir, 'lin_costs.npy'))

    aff_uk_min_idx = np.unravel_index(np.argmin(aff_uk_costs), aff_uk_costs.shape)
    aff_ueq_min_idx = np.unravel_index(np.argmin(aff_ueq_costs), aff_ueq_costs.shape)
    aff_xeq_min_idx = np.unravel_index(np.argmin(aff_xeq_costs), aff_xeq_costs.shape)
    lin_min_idx = np.unravel_index(np.argmin(lin_costs), lin_costs.shape)

    min_costs = [aff_uk_costs[aff_uk_min_idx], aff_ueq_costs[aff_ueq_min_idx],
                 aff_xeq_costs[aff_xeq_min_idx], lin_costs[lin_min_idx]]
    idx = np.argmin(min_costs)
    if idx == 0:
        anchor_pt = '(xt,ut)'
        states = np.load(os.path.join(load_dir, 'aff_uk_states.npy'))
        states_top = states[aff_uk_min_idx]
        best_idx = aff_uk_min_idx
    elif idx == 1:
        anchor_pt = '(xt,ue)'
        states = np.load(os.path.join(load_dir, 'aff_ueq_states.npy'))
        states_top = states[aff_ueq_min_idx]
        best_idx = aff_ueq_min_idx
    elif idx == 2:
        anchor_pt = '(xe,ut)'
        states = np.load(os.path.join(load_dir, 'aff_xeq_states.npy'))
        states_top = states[aff_xeq_min_idx]
        best_idx = aff_xeq_min_idx
    else:
        anchor_pt = '(xe,ue)'
        states = np.load(os.path.join(load_dir, 'lin_states.npy'))
        states_top = states[lin_min_idx]
        best_idx = lin_min_idx

    print(f'Top: {anchor_pt}, c={best_idx[1]/10:.1f}, k={best_idx[0]+1} \t Best Affinization')

    if method in C.METHODS:
        match method:
            case 'best_aff':
                anchor_point = anchor_pt
                k_idx, c_idx = best_idx
                label_bot = "Best Affinization"
            case 'best_lin':
                states = np.load(os.path.join(load_dir, 'lin_states.npy'))
                anchor_point = C.ANCHOR_POINTS[-1]
                k_idx, c_idx = best_idx
                label_bot = "Best Linearization"
            case 'nom_aff':
                states = np.load(os.path.join(load_dir, 'aff_uk_states.npy'))
                anchor_point = C.ANCHOR_POINTS[0]
                k_idx = 0
                c_idx = 0
                label_bot = "Nominal Affinization"
            case 'nom_lin':
                states = np.load(os.path.join(load_dir, 'lin_states.npy'))
                anchor_point = C.ANCHOR_POINTS[-1]
                k_idx = 0
                c_idx = 0
                label_bot = "Nominal Linearization"
            case _:
                raise ValueError(f'Invalid method: {method}')
        color_bot = C.COLORS[method]
    else:
        match anchor_point:
            case '(xt,ut)':
                states = np.load(os.path.join(load_dir, 'aff_uk_states.npy'))
                costs = np.load(os.path.join(load_dir, 'aff_uk_costs.npy'))
            case '(xt,ue)':
                states = np.load(load_dir + 'aff_ueq_states.npy')
                costs = np.load(load_dir + 'aff_ueq_costs.npy')
            case '(xe,ut)':
                states = np.load(load_dir + 'aff_xeq_states.npy')
                costs = np.load(load_dir + 'aff_xeq_costs.npy')
            case '(xe,ue)':
                states = np.load(load_dir + 'lin_states.npy')
                costs = np.load(load_dir + 'lin_costs.npy')
            case _:
                raise ValueError(f'Invalid approx_pt: {anchor_point}')
        if c_idx == -1 and k_idx == -1:
            k_idx,c_idx = np.unravel_index(np.argmin(costs), costs.shape)
        elif c_idx == -1:
            c_idx = np.argmin(costs[k_idx])
        elif k_idx == -1:
            k_idx = np.argmin(costs[:,c_idx])
        color_bot = 'tab:gray'
        label_bot = 'Manual Selection'

    states_bot = states[k_idx, c_idx]
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
    default_dir = '~/data/ampc24/analysis/arm/step_60'
    default_dir = '~/data/ampc24/analysis/arm/cos_90_3'
    default_dir = '~/data/ampc24/analysis/beam/step_0.4'
    default_dir = '~/data/ampc24/analysis/pendulum/cos_15_1'
    default_dir = '~/data/ampc24/analysis/pendulumz/rampz_5'
    # default_dir = '~/data/ampc24/analysis/multirotor/ramp1_10'
    # default_dir = '/tmp/ampc24/analysis/'
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
