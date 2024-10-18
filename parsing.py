import argparse
import os


def fixDirString(dir_s: str):
    if not dir_s[-1] == '/':
        dir_s += '/'
    return dir_s


def fixSystemString(s: str):
    if s[0] == 'a':
        return 'arm'
    elif s[0] == 'b':
        return 'blockbeam'
    elif s[0] in ['c', 'p']:
        return 'pendulum'
    elif s[0] == 'm':
        return 'multirotor'
    else:
        raise ValueError(f'Invalid system: {s}')


def getParsedArgs_run(default_dir: str, description: str):
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('-S', '--system', type=str, default='arm', nargs='?',
                        help='System to simulate: [arm, blockbeam, multirotor]')
    parser.add_argument('-D', '--dir', type=str,
                        default=default_dir,
                        help='Specify path to directory where data will be saved.')
    parser.add_argument('-m', '--mkdirs', action='store_true',
                        help='Create DIR if it does not exist and is not the default.')
    parser.add_argument('-o', '--overwrite-dir', action='store_true',
                        help='Overwrite contents of DIR if it exists.')
    parser.add_argument('-H', '--headless', action='store_true',
                        help='Run in headless mode')
    parser.add_argument('-k', '--k-all', action='store_true',
                        help='Run for all k indices or just k=0')
    # parser.add_argument('-K', type=int, default=0, nargs='?',
    #                     help='Specify k indices to anlayze: start, [stop], [step]')
    parser.add_argument('-Q', '--weights', type=float, nargs='*',
                        help='State weights')
    parser.add_argument('-R', '--ref-type', type=str, default='step',
                        help=f'Reference trajectory type')
    parser.add_argument('params', nargs='*', type=float,
                        help='A list of parameters for the reference trajectory')
    args = parser.parse_args()
    args.dir = fixDirString(args.dir)
    args.system = fixSystemString(args.system)

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
                msg = f'Move contents of {args.dir}, choose a different DIR, or use -O flag'
                raise FileExistsError(msg)
    print(f'Saving data to: {args.dir}')
    return args


def getParsedArgs_plot(default_dir: str, description: str):
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('-D', '--dir', type=str,
                        default=default_dir,
                        help='Specify path to directory from which data will be loaded.')
    parser.add_argument('-H', '--headless', action='store_true',
                        help='Run in headless mode')
    args = parser.parse_args()
    args.dir = fixDirString(args.dir)
    print(f'Loading data from: {args.dir}')
    return args
