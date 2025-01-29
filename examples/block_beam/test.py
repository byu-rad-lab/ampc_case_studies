#%%
import sympy as sp
import numpy as np


# x = sp.Matrix(sp.symbols('z, theta, z_dot, theta_dot'))
x = sp.Matrix(sp.symbols('x0, x1, x2, x3'))
u = sp.symbols('u')

g,length,m_block,m_beam = sp.symbols('g, l, m1, m2')

force = u*length*sp.cos(x[1])
friction = 2*m_block*x[0]*x[2]*x[3]
g_block = m_block*g*x[0]*sp.cos(x[1])
g_beam = 0.5*m_beam*g*length*sp.cos(x[1])
inertia = m_beam*length**2/3 + m_block*x[0]**2

f = sp.Matrix([[x[2]],
               [x[3]],
               [x[0]*x[3]**2 - g*sp.sin(x[1])],
               [(force - friction - g_block - g_beam) / inertia]])

sp.pprint(f)

#%%

A = f.jacobian(x)

#%%

sp.pprint(A[:2,:])

#%%

sp.pprint(A[2,:])

#%%

# sp.pprint(A[3,:])
# sp.pprint(A[3,0])
# sp.pprint(A[3,1])
# sp.pprint(A[3,2])
sp.pprint(A[3,3])

#%%
B = f.diff(u)
B
# %%
x_eq = {x[1]: 0, x[2]: 0, x[3]: 0}
A.subs(x_eq)

# %%

B.subs(x_eq)

# %%
state = {x[0]: 0.4, x[1]: 0, x[2]: 0, x[3]: 0}
state = {x[0]: 0.25, x[1]: -np.radians(15), x[2]: 0.1, x[3]: 0.01}
params = {g: 9.8, length: 0.5, m_block: 0.35, m_beam: 2}
# u_eq = (0.5*m_beam*g + m_block*x[0]*g/length).subs({x[0]: 0.25, g: 9.8, length: 0.5, m_block: 0.35, m_beam: 2})
u_eq = (0.5*m_beam*g + m_block*x[0]*g/length).subs(state | params)
inputs = {u: u_eq + 0.5}

# %%

A.subs(state | params | inputs)

# %%

B.subs(state | params | inputs)

# %%
