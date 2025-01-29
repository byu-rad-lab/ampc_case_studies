import numpy as np
import os
import csv
from tabulate import tabulate

import examples.single_link_arm.plotter as arm_plotter
import examples.block_beam.plotter as beam_plotter
import examples.cart_pendulum.plotter as pendulum_plotter
import examples.multirotor.plotter as multirotor_plotter
from parsing import getParsedArgs_plot


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

    def writeCSV(self, writer: csv.writer, method: str):
        writer.writerow([f'{method} min cost'] + self.min_cost)
        writer.writerow([f'{method} best k'] + self.k_best)
        writer.writerow([f'{method} best c'] + self.c_best)
        writer.writerow([f'{method} cost @ k1'] + self.k1_min_cost)
        writer.writerow([f'{method} c @ k1'] + self.c_at_k1)
        writer.writerow([f'{method} nominal cost'] + self.nominal_cost)
        writer.writerow([f'{method} c % reduction'] + self.c_reduction)
        writer.writerow([f'{method} c % improvement'] + self.c_improvement)
        writer.writerow([f'{method} c X better'] + self.c_times_better)

class AnalysisTable:
    def __init__(self):
        self.uk = MethodTable()
        self.ueq = MethodTable()
        self.xeq = MethodTable()
        self.lin = MethodTable()
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
            self.uk.writeCSV(writer, 'aff (x0,u0)')
            writer.writerow(['']*len(headers))
            self.ueq.writeCSV(writer, 'aff (x0,ueq)')
            writer.writerow(['']*len(headers))
            self.xeq.writeCSV(writer, 'aff (xeq,u0)')
            writer.writerow(['']*len(headers))
            self.lin.writeCSV(writer, 'lin (xeq,ueq)')
            writer.writerow(['']*len(headers))
            writer.writerow(['best cost'] + self.best_aff_cost)
            writer.writerow(['aff nominal cost'] + self.nominal_aff_cost)
            writer.writerow(['lin best cost'] + self.best_lin_cost)
            writer.writerow(['lin nominal cost'] + self.nominal_lin_cost)
            writer.writerow([f'% improvement over nom aff'] + self.aff_improvement)
            writer.writerow(['X better than nom aff'] + self.aff_times_better)
            writer.writerow([f'% reduction over nom aff'] + self.aff_reduction)
            writer.writerow([f'% improvement over best lin'] + self.best_lin_improvement)
            writer.writerow(['X better than best lin'] + self.best_lin_times_better)
            writer.writerow([f'% reduction over best lin'] + self.best_lin_reduction)
            writer.writerow([f'% improvement over nom lin'] + self.nom_lin_improvement)
            writer.writerow(['X better than nom lin'] + self.nom_lin_times_better)
            writer.writerow([f'% reduction over nom lin'] + self.nom_lin_reduction)
            writer.writerow(['best method'] + self.best_method)
        return


class SimData:
    def __init__(self, load_dir: str):
        self.load_dir = load_dir
        self.time = np.load(load_dir + 'time.npy')

        self.uk_costs = np.load(load_dir + 'aff_uk_costs.npy')
        self.ueq_costs = np.load(load_dir + 'aff_ueq_costs.npy')
        self.xeq_costs = np.load(load_dir + 'aff_xeq_costs.npy')
        self.lin_costs = np.load(load_dir + 'lin_costs.npy')

        self.uk_states = np.load(load_dir + 'aff_uk_states.npy')
        self.ueq_states = np.load(load_dir + 'aff_ueq_states.npy')
        self.xeq_states = np.load(load_dir + 'aff_xeq_states.npy')
        self.lin_states = np.load(load_dir + 'lin_states.npy')

        self.uk_inputs = np.load(load_dir + 'aff_uk_inputs.npy')
        self.ueq_inputs = np.load(load_dir + 'aff_ueq_inputs.npy')
        self.xeq_inputs = np.load(load_dir + 'aff_xeq_inputs.npy')
        self.lin_inputs = np.load(load_dir + 'lin_inputs.npy')

        self.ref_states = np.load(load_dir + 'ref_states.npy')
        self.Q = np.load(load_dir + 'Q.npy')
        self.k_list = np.load(load_dir + 'k_list.npy')

        with open(load_dir + 'system.txt', 'r') as f:
            self.system = f.readline()

        self.num_c = len(self.uk_costs[0])
        self.c_list = np.linspace(0, 1, self.num_c)


def main():
    base_dir = f'{os.environ["HOME"]}/data/ampc24/analysis/'
    save_dir = f'{base_dir}summary'
    systems = ['arm', 'beam', 'pendulum', 'pendulumz', 'multirotor']
    # ref_cmds = {}
    arm_steps = ['step_30', 'step_60', 'step_120', 'step_180', 'step_270']
    arm_ramps = ['ramp_2pi_10', 'ramp_2pi_7.5', 'ramp_2pi_5', 'ramp_2pi_2.5']
    arm_cos_60s = ['cos_60_2', 'cos_60_3', 'cos_60_4']
    arm_cos_90s = ['cos_90_2', 'cos_90_3', 'cos_90_4']

    beam_steps = ['step_0.1', 'step_0.2', 'step_0.3', 'step_0.4']
    beam_ramps = ['ramp_0.2', 'ramp_0.3', 'ramp_0.4']
    beam_cos = ['cos_0.2_1', 'cos_0.2_2', 'cos_0.2_3', 'cos_0.2_4', 'cos_0.2_5']

    # pendulum_steps = ['step_1', 'step_5', 'step_10', 'step_15', 'step_20', 'step_30', 'step_45']
    pendulum_steps = ['step_5', 'step_15', 'step_30', 'step_45']
    # pendulum_cos_5s = ['cos_5_1', 'cos_5_2', 'cos_5_3', 'cos_5_4']
    pendulum_cos_15s = ['cos_15_1', 'cos_15_2', 'cos_15_3', 'cos_15_4']
    pendulum_cos_25s = ['cos_25_1', 'cos_25_2', 'cos_25_3', 'cos_25_4']
    # pendulum_ramps = ['ramp_1', 'ramp_5', 'ramp_10', 'ramp_15', 'ramp_30', 'ramp_45']
    pendulum_ramps = ['ramp_5', 'ramp_15', 'ramp_30', 'ramp_45']

    pendulumz_steps = ['stepz_1', 'stepz_2', 'stepz_5', 'stepz_10']
    # pendulumz_cos_0_5s = ['cosz_0.5_1', 'cosz_0.5_2', 'cosz_0.5_3', 'cosz_0.5_4']
    # pendulumz_cos_1s = ['cosz_1_1', 'cosz_1_2', 'cosz_1_3', 'cosz_1_4']
    pendulumz_cos_2s = ['cosz_2_1', 'cosz_2_2', 'cosz_2_3', 'cosz_2_4']
    pendulumz_cos_5s = ['cosz_5_1', 'cosz_5_2', 'cosz_5_3', 'cosz_5_4']
    # pendulumz_ramps = ['rampz_1', 'rampz_2', 'rampz_3', 'rampz_4', 'rampz_5']
    pendulumz_ramps = ['rampz_2', 'rampz_3', 'rampz_4', 'rampz_5']

    # multirotor_steps = ['step_1_pi2', 'step_2_pi1.5', 'step_5_pi', 'step_10_2pi']
    multirotor_steps_q2 = ['step_1_pi2_q2', 'step_2_pi1.5_q2', 'step_5_pi_q2', 'step_10_2pi_q2']
    # multirotor_wavy = ['wavy_1_5_2_6', 'wavy_1_5_4_6', 'wavy_2_5_2_6', 'wavy_2_4_5_4']
    multirotor_wavy_q2 = ['wavy_1_5_2_6_q2', 'wavy_1_5_4_6_q2', 'wavy_2_5_2_6_q2', 'wavy_2_4_5_4_q2']
    multirotor_ramp1s = ['ramp1_5', 'ramp1_10', 'ramp1_15', 'ramp1_20', 'ramp1_25']
    # multirotor_ramp3s = ['ramp3_5', 'ramp3_6', 'ramp3_7', 'ramp3_8', 'ramp3_9', 'ramp3_10']
    multirotor_ramp3s = ['ramp3_6', 'ramp3_7', 'ramp3_8', 'ramp3_9', 'ramp3_10']

    ref_cmds = {
        'arm': arm_steps + arm_ramps + arm_cos_60s + arm_cos_90s,
        'beam': beam_steps + beam_ramps + beam_cos,
        'pendulum': pendulum_steps + pendulum_cos_15s + pendulum_cos_25s + pendulum_ramps,
        'pendulumz': pendulumz_steps + pendulumz_cos_2s + pendulumz_cos_5s + pendulumz_ramps,
        'multirotor': [*multirotor_steps_q2, *multirotor_wavy_q2,
                       *multirotor_ramp1s, *multirotor_ramp3s]
    }

    for system in systems:
        # refs = os.listdir(base_dir + system)
        # refs.sort()
        # ref_cmds[system] = refs
        refs = ref_cmds[system]

        table = AnalysisTable()

        for ref in refs:
            load_dir = f'{base_dir}{system}/{ref}/'
            data = SimData(load_dir)
            cAnalysis(data, table)
            kAnalysis(data, table)
            summaryAnalysis(data, table)
        table.writeCSV(base_dir, refs, system)
    return

def cAnalysis(data: SimData, table: AnalysisTable):
    k = 0
    all_costs = [data.uk_costs, data.ueq_costs, data.xeq_costs, data.lin_costs]
    tables = [table.uk, table.ueq, table.xeq, table.lin]
    for i in range(4):
        costs = all_costs[i]
        table: MethodTable = tables[i]

        c_idx = np.argmin(costs[k])
        cost_min = costs[k,c_idx]
        table.k1_min_cost.append(cost_min)
        table.c_at_k1.append(data.c_list[c_idx])

        cost_c0 = costs[k,0]
        table.nominal_cost.append(cost_c0)

        table.c_reduction.append(getReduction(cost_min, cost_c0))
        table.c_improvement.append(getImprovement(cost_min, cost_c0))
        table.c_times_better.append(getTimesBetter(cost_min, cost_c0))
    return

def kAnalysis(data: SimData, table: AnalysisTable):
    all_costs = [data.uk_costs, data.ueq_costs, data.xeq_costs, data.lin_costs]
    tables = [table.uk, table.ueq, table.xeq, table.lin]
    for i in range(4):
        costs = all_costs[i]
        table: MethodTable = tables[i]

        min_cost = np.min(costs)
        idx = np.argmin(costs)
        k_idx = idx // costs.shape[1]
        c_idx = idx % costs.shape[1]
        assert min_cost == costs[k_idx, c_idx]
        table.min_cost.append(min_cost)
        table.k_best.append(k_idx+1)
        table.c_best.append(data.c_list[c_idx])

        nominal_cost = costs[0,0]
        table.k_improvement.append(getImprovement(min_cost, nominal_cost))
        table.k_reduction.append(getReduction(min_cost, nominal_cost))
        table.k_times_better.append(getTimesBetter(min_cost, nominal_cost))
    return

def summaryAnalysis(data: SimData, table: AnalysisTable):
    min_costs = np.array([table.uk.min_cost[-1], table.ueq.min_cost[-1],
                          table.xeq.min_cost[-1], table.lin.min_cost[-1]])
    uk_k1_cost = table.uk.k1_min_cost[-1]

    best = np.min(min_costs) # best of all 4 methods
    lin_best = min_costs[-1] # best using lin (xeq, ueq)
    aff_nominal = table.uk.nominal_cost[-1] # aff (x0, u0) @ c=0, k=1
    lin_nominal = table.lin.nominal_cost[-1] # lin (xeq, ueq) @ c=0, k=1

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

    method = np.argmin(min_costs)
    if method == 0:
        table.best_method.append('aff (x0,u0)')
    elif method == 1:
        table.best_method.append('aff (x0,ueq)')
    elif method == 2:
        table.best_method.append('aff (xeq,u0)')
    else:
        table.best_method.append('lin (xeq,ueq)')
    return

def getImprovement(best, nominal):
    return (nominal/best - 1) * 100

def getTimesBetter(best, nominal):
    return nominal/best

def getReduction(best, nominal):
    return (1 - best/nominal) * 100



if __name__ == '__main__':
    main()
