import numpy as np
from tqdm import tqdm

from case_studies.block_beam.animation import Animation
from case_studies.tabbed_plot_window import TabbedPlotWindow
from parsing import getParsedArgs_plot


def animate(load_dir: str):
    figsize = 1000,800

    ## Load Data
    time = np.loadtxt(load_dir + 'time.txt')
    aff_costs = np.loadtxt(load_dir + 'aff_costs.txt')
    lin_costs = np.loadtxt(load_dir + 'lin_costs.txt')
    num_c = len(aff_costs)
    aff_states = np.loadtxt(load_dir + 'aff_states.txt').reshape(num_c,-1,4)
    lin_states = np.loadtxt(load_dir + 'lin_states.txt').reshape(num_c,-1,4)
    xr_hist = np.loadtxt(load_dir + 'ref_states.txt')

    min_idx = np.argmin(aff_costs)
    x_hist = aff_states[min_idx]
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
