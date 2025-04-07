import numpy as np
import os
import csv
from tabulate import tabulate
import pickle

import constants as C


class MethodTable:
    def __init__(self):
        self.min_cost = [] # vary c,k
        self.k_best = []
        self.c_best = []
        self.k1_min_cost = [] # vary c, k=1
        self.c_at_k1 = []
        self.nominal_cost = [] # c=0, k=1
        self.c_reduction = []
        self.c_improvement = []
        self.c_times_better = []
        self.k_reduction = []
        self.k_improvement = []
        self.k_times_better = []
        self.ck_reduction = []
        self.ck_improvement = []
        self.ck_times_better = []

    def writeCSV(self, writer: csv.writer, method: str):
        writer.writerow([f'{method} min cost'] + self.min_cost)
        writer.writerow([f'{method} best k'] + self.k_best)
        writer.writerow([f'{method} best c'] + self.c_best)
        writer.writerow([f'{method} cost @ k1'] + self.k1_min_cost)
        writer.writerow([f'{method} c @ k1'] + self.c_at_k1)
        writer.writerow([f'{method} nominal cost'] + self.nominal_cost)
        writer.writerow([f'{method} c % reduction'] + self.c_reduction)
        # writer.writerow([f'{method} c % improvement'] + self.c_improvement)
        # writer.writerow([f'{method} c X better'] + self.c_times_better)
        writer.writerow([f'{method} k % reduction'] + self.k_reduction)
        # writer.writerow([f'{method} k % improvement'] + self.k_improvement)
        # writer.writerow([f'{method} k X better'] + self.k_times_better)
        writer.writerow([f'{method} ck % reduction'] + self.ck_reduction)
        # writer.writerow([f'{method} ck % improvement'] + self.ck_improvement)
        # writer.writerow([f'{method} ck X better'] + self.ck_times_better)
        return

    def writeNpz(self, save_dir: str, method: str):
        data = {
            'min_cost': np.array(self.min_cost),
            'k_best': np.array(self.k_best, dtype=np.int64),
            'c_best': np.array(self.c_best),
            'k1_min_cost': np.array(self.k1_min_cost),
            'c_at_k1': np.array(self.c_at_k1),
            'nominal_cost': np.array(self.nominal_cost),
            'c_reduction': np.array(self.c_reduction),
            'c_improvement': np.array(self.c_improvement),
            'c_times_better': np.array(self.c_times_better),
            'k_reduction': np.array(self.k_reduction),
            'k_improvement': np.array(self.k_improvement),
            'k_times_better': np.array(self.k_times_better),
            'ck_reduction': np.array(self.ck_reduction),
            'ck_improvement': np.array(self.ck_improvement),
            'ck_times_better': np.array(self.ck_times_better)
        }
        np.savez(f'{save_dir}/{method}.npz', **data)


class AnalysisTable:
    def __init__(self):
        self.m_table = {}
        for p in C.ANCHOR_POINTS:
            self.m_table[p] = MethodTable()
        self.best_aff_cost = []
        self.nominal_aff_cost = []
        self.best_lin_cost = []
        self.nominal_lin_cost = []
        self.aff_improvement = []
        self.aff_times_better = []
        self.aff_reduction = []
        self.best_lin_improvement = []
        self.best_lin_times_better = []
        self.best_lin_reduction = []
        self.nom_lin_improvement = []
        self.nom_lin_times_better = []
        self.nom_lin_reduction = []
        self.best_method = []

    def writeCSV(self, write_dir: str, headers: list[str], system: str):
        with open(f'{write_dir}/{system}_analysis.csv', 'w') as file:
            writer = csv.writer(file)
            writer.writerow([''] + headers)
            for p in C.ANCHOR_POINTS:
                table: MethodTable = self.m_table[p]
                table.writeCSV(writer, p)
                writer.writerow(['']*len(headers))

            writer.writerow(['best cost'] + self.best_aff_cost)
            writer.writerow(['aff nominal cost'] + self.nominal_aff_cost)
            writer.writerow(['lin best cost'] + self.best_lin_cost)
            writer.writerow(['lin nominal cost'] + self.nominal_lin_cost)
            # writer.writerow([f'% improvement over nom aff'] + self.aff_improvement)
            # writer.writerow(['X better than nom aff'] + self.aff_times_better)
            writer.writerow([f'% reduction over nom aff'] + self.aff_reduction)
            # writer.writerow([f'% improvement over best lin'] + self.best_lin_improvement)
            # writer.writerow(['X better than best lin'] + self.best_lin_times_better)
            writer.writerow([f'% reduction over best lin'] + self.best_lin_reduction)
            # writer.writerow([f'% improvement over nom lin'] + self.nom_lin_improvement)
            # writer.writerow(['X better than nom lin'] + self.nom_lin_times_better)
            writer.writerow([f'% reduction over nom lin'] + self.nom_lin_reduction)
            writer.writerow(['best method'] + self.best_method)
        return

    def writeNpz(self, write_dir: str, system: str):
        for p in C.ANCHOR_POINTS:
            table: MethodTable = self.m_table[p]
            table.writeNpz(write_dir, f'{system}_{p[1:-1].replace(",", "_")}')
        data = {
            'best_aff_cost': np.array(self.best_aff_cost),
            'nominal_aff_cost': np.array(self.nominal_aff_cost),
            'best_lin_cost': np.array(self.best_lin_cost),
            'nominal_lin_cost': np.array(self.nominal_lin_cost),
            'aff_improvement': np.array(self.aff_improvement),
            'aff_times_better': np.array(self.aff_times_better),
            'aff_reduction': np.array(self.aff_reduction),
            'best_lin_improvement': np.array(self.best_lin_improvement),
            'best_lin_times_better': np.array(self.best_lin_times_better),
            'best_lin_reduction': np.array(self.best_lin_reduction),
            'nom_lin_improvement': np.array(self.nom_lin_improvement),
            'nom_lin_times_better': np.array(self.nom_lin_times_better),
            'nom_lin_reduction': np.array(self.nom_lin_reduction),
            'best_method': np.array(self.best_method)
        }
        np.savez(f'{write_dir}/{system}_analysis.npz', **data)


class SimData:
    def __init__(self, load_dir: str):
        self.load_dir = load_dir
        self.time = np.load(load_dir + 'time.npy')
        self.costs = np.load(load_dir + 'costs.npz')
        self.states = np.load(load_dir + 'states.npz')
        self.inputs = np.load(load_dir + 'inputs.npz')
        self.ref_states = np.load(load_dir + 'ref_states.npy')
        self.Q = np.load(load_dir + 'Q.npy')
        self.k_list = np.load(load_dir + 'k_list.npy')

        with open(load_dir + 'system.txt', 'r') as f:
            self.system = f.readline()

        self.num_c = len(self.costs[C.ANCHOR_POINTS[0]][0])
        self.c_list = np.linspace(0, 1, self.num_c)


def main():
    base_dir = f'{os.environ["HOME"]}/data/ampc_case_studies/'
    save_dir = f'{base_dir}summary'
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    systems = ['arm', 'beam', 'pendulum', 'cart', 'multirotor']

    arm_steps = ['step_30', 'step_60', 'step_120', 'step_180', 'step_270']
    arm_ramps = ['ramp_2pi_10', 'ramp_2pi_7.5', 'ramp_2pi_5', 'ramp_2pi_2.5']
    arm_cos_60s = ['cos_60_2', 'cos_60_3', 'cos_60_4']
    arm_cos_90s = ['cos_90_2', 'cos_90_3', 'cos_90_4']

    beam_steps = ['step_0.1', 'step_0.2', 'step_0.3', 'step_0.4']
    beam_ramps = ['ramp_0.2', 'ramp_0.3', 'ramp_0.4']
    beam_cos = ['cos_0.2_1', 'cos_0.2_2', 'cos_0.2_3', 'cos_0.2_4', 'cos_0.2_5']

    pendulum_steps = ['step_5', 'step_15', 'step_30', 'step_45']
    pendulum_ramps = ['ramp_5', 'ramp_15', 'ramp_30', 'ramp_45']
    pendulum_cos_15s = ['cos_15_1', 'cos_15_2', 'cos_15_3', 'cos_15_4']
    pendulum_cos_25s = ['cos_25_1', 'cos_25_2', 'cos_25_3', 'cos_25_4']

    cart_steps = ['step_1', 'step_2', 'step_5', 'step_10']
    cart_ramps = ['ramp_2', 'ramp_3', 'ramp_4', 'ramp_5']
    cart_cos_2s = ['cos_2_1', 'cos_2_2', 'cos_2_3', 'cos_2_4']
    cart_cos_5s = ['cos_5_1', 'cos_5_2', 'cos_5_3', 'cos_5_4']

    uas_steps = ['step_1_pi2_q2', 'step_2_pi1.5_q2', 'step_5_pi_q2', 'step_10_2pi_q2']
    uas_ramp1s = ['ramp1_5', 'ramp1_10', 'ramp1_15', 'ramp1_20', 'ramp1_25']
    uas_ramp3s = ['ramp3_6', 'ramp3_7', 'ramp3_8', 'ramp3_9', 'ramp3_10']
    uas_wavy = ['wavy_1_5_2_6_q2', 'wavy_1_5_4_6_q2', 'wavy_2_5_2_6_q2', 'wavy_2_4_5_4_q2']

    ref_cmds = {
        'arm': arm_steps + arm_ramps + arm_cos_60s + arm_cos_90s,
        'beam': beam_steps + beam_ramps + beam_cos,
        'pendulum': pendulum_steps + pendulum_ramps + pendulum_cos_15s + pendulum_cos_25s,
        'cart': cart_steps + cart_ramps + cart_cos_2s + cart_cos_5s,
        'multirotor': uas_steps + uas_ramp1s + uas_ramp3s + uas_wavy
    }

    for system in systems:
        refs = ref_cmds[system]

        table = AnalysisTable()

        for ref in refs:
            load_dir = f'{base_dir}{system}/{ref}/'
            data = SimData(load_dir)
            cAnalysis(data, table)
            kAnalysis(data, table)
            summaryAnalysis(data, table)
        table.writeCSV(save_dir, refs, system)
        table.writeNpz(save_dir, system)

        with open(f'{save_dir}/refs.pkl', 'wb') as file:
            pickle.dump(ref_cmds, file, protocol=pickle.HIGHEST_PROTOCOL)

    return

def cAnalysis(data: SimData, table: AnalysisTable):
    k_nom = 0
    for p in C.ANCHOR_POINTS:
        costs = data.costs[p]
        m_table: MethodTable = table.m_table[p]

        c_idx = np.argmin(costs[k_nom])
        cost_min = costs[k_nom,c_idx]
        m_table.k1_min_cost.append(cost_min)
        m_table.c_at_k1.append(data.c_list[c_idx])

        cost_c0 = costs[k_nom,0]
        m_table.nominal_cost.append(cost_c0)

        m_table.c_reduction.append(getReduction(cost_min, cost_c0))
        m_table.c_improvement.append(getImprovement(cost_min, cost_c0))
        m_table.c_times_better.append(getTimesBetter(cost_min, cost_c0))
    return

def kAnalysis(data: SimData, table: AnalysisTable):
    for p in C.ANCHOR_POINTS:
        costs = data.costs[p]
        m_table: MethodTable = table.m_table[p]

        min_cost = np.min(costs)
        idx = np.argmin(costs)
        k_idx = idx // costs.shape[1]
        c_idx = idx % costs.shape[1]
        assert min_cost == costs[k_idx, c_idx]
        m_table.min_cost.append(min_cost)
        m_table.k_best.append(k_idx+1)
        m_table.c_best.append(data.c_list[c_idx])

        nominal_cost = m_table.k1_min_cost[-1]
        m_table.k_reduction.append(getReduction(min_cost, nominal_cost))
        m_table.k_improvement.append(getImprovement(min_cost, nominal_cost))
        m_table.k_times_better.append(getTimesBetter(min_cost, nominal_cost))

        nominal_cost = costs[0,0]
        m_table.ck_improvement.append(getImprovement(min_cost, nominal_cost))
        m_table.ck_reduction.append(getReduction(min_cost, nominal_cost))
        m_table.ck_times_better.append(getTimesBetter(min_cost, nominal_cost))
    return

def summaryAnalysis(data: SimData, table: AnalysisTable):
    min_costs = np.empty(len(C.ANCHOR_POINTS))
    for i,p in enumerate(C.ANCHOR_POINTS):
        m_table: MethodTable = table.m_table[p]
        min_costs[i] = m_table.min_cost[-1]

    best = np.min(min_costs) # best of all 4 methods
    lin_best = min_costs[-1] # best using (xe,ue)
    aff_nominal = table.m_table['(xt,ut)'].nominal_cost[-1] # @ c=0, k=1
    lin_nominal = table.m_table['(xe,ue)'].nominal_cost[-1] # @ c=0, k=1

    table.best_aff_cost.append(best)
    table.best_lin_cost.append(lin_best)
    table.nominal_aff_cost.append(aff_nominal)
    table.nominal_lin_cost.append(lin_nominal)

    table.aff_improvement.append(getImprovement(best, aff_nominal))
    table.aff_times_better.append(getTimesBetter(best, aff_nominal))
    table.aff_reduction.append(getReduction(best, aff_nominal))

    table.best_lin_improvement.append(getImprovement(best, lin_best))
    table.best_lin_times_better.append(getTimesBetter(best, lin_best))
    table.best_lin_reduction.append(getReduction(best, lin_best))

    table.nom_lin_improvement.append(getImprovement(best, lin_nominal))
    table.nom_lin_times_better.append(getTimesBetter(best, lin_nominal))
    table.nom_lin_reduction.append(getReduction(best, lin_nominal))

    table.best_method.append(C.ANCHOR_POINTS_LATEX[np.argmin(min_costs)])
    return

def getImprovement(best, nominal):
    return (nominal/best - 1) * 100

def getTimesBetter(best, nominal):
    return nominal/best

def getReduction(best, nominal):
    return (1 - best/nominal) * 100



if __name__ == '__main__':
    main()
