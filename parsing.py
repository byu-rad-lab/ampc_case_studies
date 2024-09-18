import argparse
import os


def fixDirString(dir_s: str):
    if not dir_s[-1] == '/':
        dir_s += '/'
    return dir_s


def getParsedArgs_run(default_dir: str, description: str, ref_types: list[str]):
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('-D', '--dir', type=str,
                        default=default_dir,
                        help='Specify path to directory where data will be saved.')
    parser.add_argument('-m', '--mkdirs', action='store_true',
                        help='Create DIR if it does not exist and is not the default.')
    parser.add_argument('-o', '--overwrite-dir', action='store_true',
                        help='Overwrite contents of DIR if it exists.')
    parser.add_argument('-Q', '--weights', type=float, nargs='*',
                        help='State weights')
    parser.add_argument('-R', '--ref-type', type=str,
                        default=ref_types[0],
                        help=f'Reference trajectory type: {ref_types}')
    parser.add_argument('params', nargs='*', type=float,
                        help='A list of parameters for the reference trajectory')
    args = parser.parse_args()
    args.dir = fixDirString(args.dir)

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
    args = parser.parse_args()
    args.dir = fixDirString(args.dir)
    print(f'Loading data from: {args.dir}')
    return args
