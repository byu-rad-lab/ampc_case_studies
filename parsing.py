import argparse
import os


def fixDirString(dir_s: str):
    if not dir_s[-1] == '/':
        dir_s += '/'
    return os.path.expanduser(dir_s)


def fixSystemString(s: str):
    if s[0] == 'a':
        return 'arm'
    elif s[0] == 'b':
        return 'blockbeam'
    elif s[0] in ['p']:
        return 'pendulum'
    elif s[0] in ['c']:
        return 'cart'
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
                msg = f'Create {args.dir} first or use -m flag to create it.'
                raise NotADirectoryError(msg)
        os.makedirs(args.dir)
    else:
        if not args.overwrite_dir:
            ans = input(f'{args.dir} contains data. Do you wish to overwrite it? [y/N]: ')
            if len(ans) == 0: ans = 'n'
            if not ans.startswith(('y','Y')):
                msg = f'Move contents of {args.dir}, choose a different DIR, or use -o flag'
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


def getParsedArgs_animate(default_dir: str, description: str):
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('-D', '--dir', type=str,
                        default=default_dir,
                        help='Specify path to directory from which data will be loaded.')
    parser.add_argument('-m', '--mkdirs', action='store_true',
                        help='Create SAVE-DIR if it does not exist.')
    parser.add_argument('-o', '--overwrite', action='store_true',
                        help='Overwrite contents of save_path if it exists.')
    group = parser.add_argument_group('Method Selection',
        """
        Specify the to use for the animation. Use -method to select from
        predefined methods or use -xp, -up, -c, and -k to specify custom values.
        """
        )
    opts = ['best_aff', 'best_lin', 'nom_aff', 'nom_lin', 'manual']
    group.add_argument('-method', type=str, choices=opts, default='nom_lin',
                       help='Specify method (if manual - must define xp, up, c_idx, and k)')
    group.add_argument('-xp', type=str, choices=['xt','xe'],
                       help='Specify anchor state xp')
    group.add_argument('-up', type=str, choices=['ut','ue'],
                       help='Specify anchor input up')
    group.add_argument('-c', '--c-idx', type=int,
                       help='Specify index of c (0-10 or -1 for "best")')
    group.add_argument('-k', type=int,
                       help='Specify value of k (1-100 or -1 for "best")')
    parser.add_argument('save_path', nargs='?', type=str,
                        help='Where to save the MP4 animation. If not provided, the animation will be displayed live.')
    args = parser.parse_args()
    args.dir = fixDirString(args.dir)
    print(f'Loading data from: {args.dir}')

    if args.method == 'manual':
        if args.xp is None:
            raise ValueError('xp is required when using manual mode')
        if args.up is None:
            raise ValueError('up is required when using manual mode')
        if args.c_idx is None:
            raise ValueError('c_idx is required when using manual mode')
        if args.k is None:
            raise ValueError('k is required when using manual mode')

    if args.c_idx is not None:
        if not isinstance(args.c_idx, int):
            raise TypeError(f'Invalid c_idx: {args.c_idx} (should be an integer)')
        if not -1 <= args.c_idx <= 10:
            raise ValueError(f'Invalid c_idx: {args.c_idx} (should be between 0 and 10 or -1 for "best")')
    if args.k is not None:
        if not isinstance(args.k, int):
            raise TypeError(f'Invalid k_idx: {args.k} (should be an integer)')
        if not -1 <= args.k <= 100 and args.k != 0:
            raise ValueError(f'Invalid k_idx: {args.k} (should be between 1 and 100 or -1 for "best")')

    if args.save_path is not None:
        if not args.save_path.endswith('.mp4'):
            raise ValueError(f'Invalid save path: {args.save_path} (should end with .mp4)')
        if not len(args.save_path) > 4:
            raise ValueError(f'Invalid save path: {args.save_path} (must specify a filename)')
        save_dir = os.path.dirname(args.save_path)
        if not os.path.exists(save_dir) and not args.mkdirs:
            print(f'Directory does not exist: {save_dir}')
            ans = input('Create it? [Y/n]: ')
            if len(ans) == 0: ans = 'y'
            if not ans.startswith(('y','Y')):
                msg = f'Create {save_dir} first or use -m flag to create it.'
                raise NotADirectoryError(msg)
            os.makedirs(save_dir)

        if os.path.exists(args.save_path) and not args.overwrite:
            ans = input(f'{args.save_path} contains data. Do you wish to overwrite it? [y/N]: ')
            if len(ans) == 0: ans = 'n'
            if not ans.startswith(('y','Y')):
                msg = f'Move contents of {args.save_path}, choose a different SAVE-PATH, or use -o flag'
                raise FileExistsError(msg)

    return args
