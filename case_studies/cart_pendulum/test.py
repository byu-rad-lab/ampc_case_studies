# %%
import sympy as sp
import numpy as np


# x = sp.Matrix(sp.symbols('z, theta, z_dot, theta_dot'))
x = sp.Matrix(sp.symbols('x0, x1, x2, x3'))
u = sp.symbols('u')

g,length,b,m_p,m_c = sp.symbols('g, l, b, m1, m2')

tmp = m_p*length/2*sp.cos(x[1])
M = sp.Matrix([[m_c + m_p, tmp],
               [tmp, m_p*length**2/3]])
c = sp.Matrix([m_p*length/2*x[3]**2*sp.sin(x[1]) + u - b*x[2],
               m_p*g*length/2*sp.sin(x[1])])

# sp.pprint(M)
# sp.pprint(c)
# ddot = sp.solve_linear_system(M, c)
# ddot = sp.solve(M, c)
ddot = sp.simplify(M.solve(c))
test = sp.simplify(M.inv() @ c)

# %%
sp.pprint(ddot)
sp.pprint(test)
# sp.pprint(sp.simplify(ddot - test))

# %%

f = sp.Matrix([[x[2]],
               [x[3]],
               [ddot[0]],
               [ddot[1]]])

sp.pprint(f)

# %%

A = f.jacobian(x)
A = sp.simplify(A)

# %%
sp.pprint(A)
# %%
sp.pprint(A[0,:])
# %%
sp.pprint(A[1,:])
# %%
# sp.pprint(A[2,0])
# sp.pprint(A[2,1])
# sp.pprint(A[2,2])
sp.pprint(A[2,3])
# %%
# sp.pprint(A[3,:])
# sp.pprint(A[3,0])
# sp.pprint(A[3,1])
# sp.pprint(A[3,2])
sp.pprint(A[3,3])

#%%
B = f.diff(u)
B
# %%
state = {x[1]: 0, x[2]: 0, x[3]: 0}
A.subs(state)

# %%

B.subs(state)

# %%
# state = {x[0]: 0.4} | state
state = {x[0]: 0.25, x[1]: -np.radians(15), x[2]: 0.1, x[3]: 0.01}
params = {g: 9.8, length: 1, m_p: 0.25, m_c: 1, b: 0.05}
u_eq = 0.0
inputs = {u: u_eq + 0.5}

# %%
A.subs(state | params | inputs)

# %%
B.subs(state | params | inputs)

# %%
w = f - A @ x - B * u
w.subs(state | params | inputs)

# %%
