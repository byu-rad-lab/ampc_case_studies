METHODS = ['best_aff', 'nom_aff', 'best_lin', 'nom_lin']
ANCHOR_POINTS = ['(xt,ut)', '(xt,ue)', '(xe,ut)', '(xe,ue)']
ANCHOR_POINTS_RAW = [r'$(x_t,u_t)$', r'$(x_t,u_e)$', r'$(x_e,u_t)$', r'$(x_e,u_e)$']
# COLORS = ['tab:pink', 'tab:blue', 'tab:orange', 'tab:green']
# REF_COLOR = 'tab:red'

COLORS = {
    'best_aff': 'tab:pink',
    'nom_aff': 'tab:blue',
    'best_lin': 'tab:orange',
    'nom_lin': 'tab:green',
    'ref': 'tab:red',

    0: 'tab:pink',
    1: 'tab:blue',
    2: 'tab:orange',
    3: 'tab:green',
    4: 'tab:red',
}

LINE_STYLES = {
    'best': '-',
    'nom': '-.',
    'ref': '--',
}
