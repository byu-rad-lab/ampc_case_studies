import numpy as np
from tqdm import tqdm

from case_studies.cart_pendulum.animation import Animation
from case_studies.tabbed_plot_window import TabbedPlotWindow
from parsing import getParsedArgs_plot


def animate(load_dir: str):
    figsize = 1000,800

    ## Load Data
    time = np.load(load_dir + 'time.npy')
    aff_uk_costs = np.load(load_dir + 'aff_uk_costs.npy')
    aff_ueq_costs = np.load(load_dir + 'aff_ueq_costs.npy')
    aff_xeq_costs = np.load(load_dir + 'aff_xeq_costs.npy')
    lin_costs = np.load(load_dir + 'lin_costs.npy')

    aff_uk_min_idx = np.unravel_index(np.argmin(aff_uk_costs), aff_uk_costs.shape)
    aff_ueq_min_idx = np.unravel_index(np.argmin(aff_ueq_costs), aff_ueq_costs.shape)
    aff_xeq_min_idx = np.unravel_index(np.argmin(aff_xeq_costs), aff_xeq_costs.shape)
    lin_min_idx = np.unravel_index(np.argmin(lin_costs), lin_costs.shape)

    min_costs = [aff_uk_costs[aff_uk_min_idx], aff_ueq_costs[aff_ueq_min_idx],
                 aff_xeq_costs[aff_xeq_min_idx], lin_costs[lin_min_idx]]
    idx = np.argmin(min_costs)
    if idx == 0:
        method = 'aff (uk)'
        states = np.load(load_dir + 'aff_uk_states.npy')
        k,c = aff_uk_min_idx
    elif idx == 1:
        method = 'aff (ueq)'
        states = np.load(load_dir + 'aff_ueq_states.npy')
        k,c = aff_ueq_min_idx
    elif idx == 2:
        method = 'aff (xeq)'
        states = np.load(load_dir + 'aff_xeq_states.npy')
        k,c = aff_xeq_min_idx
    else:
        method = 'lin'
        states = np.load(load_dir + 'lin_states.npy')
        k,c = lin_min_idx

    x_hist = states[k,c]
    animation = Animation(x_hist[0])
    pw = TabbedPlotWindow('Cart Pendulum', figsize)
    pw.addTab('animation', animation.fig)

    k += 1
    c = np.linspace(0, 1, 11)[c]
    print(f'Animating results from {method} with {k=} and {c=:.1f}')

    dt = time[1] - time[0]
    skip = 1
    for x in tqdm(x_hist[::skip]):
        animation.update(x)
        pw.pause(dt*skip)
    pw.show()


def main():
    load_dir = '/tmp/ampc24/pendulum/analysis'
    desc = 'Animate cart pendulum'
    args = getParsedArgs_plot(load_dir, desc)
    animate(args.dir)


if __name__ == '__main__':
    main()
