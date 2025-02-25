import numpy as np
from tqdm import tqdm

from case_studies.block_beam.animation import Animation
from case_studies.tabbed_plot_window import TabbedPlotWindow
from parsing import getParsedArgs_plot


def animate(load_dir: str):
    figsize = 1000,800

    ## Load Data
    time = np.load(load_dir + 'time.npy')
    aff_costs = np.load(load_dir + 'aff_uk_costs.npy')
    lin_costs = np.load(load_dir + 'lin_costs.npy')
    num_c = len(aff_costs)
    aff_states = np.load(load_dir + 'aff_uk_states.npy')
    lin_states = np.load(load_dir + 'lin_states.npy')
    xr_hist = np.load(load_dir + 'ref_states.npy')

    min_idx = np.argmin(aff_costs)
    k_idx = min_idx // aff_costs.shape[1]
    c_idx = min_idx % aff_costs.shape[1]
    x_hist = aff_states[k_idx, c_idx]
    animation = Animation(x_hist[0])
    pw = TabbedPlotWindow('Block Beam', figsize)
    pw.addTab('animation', animation.fig)

    dt = time[1] - time[0]
    skip = 1
    for x in tqdm(x_hist[::skip]):
        animation.update(x)
        pw.pause(dt*skip)
    pw.show()


def main():
    load_dir = '/tmp/ampc24/blockbeam/lin_vs_aff'
    desc = 'Animate linearization vs affinization comparison for block beam'
    args = getParsedArgs_plot(load_dir, desc)
    animate(args.dir)


if __name__ == '__main__':
    main()
