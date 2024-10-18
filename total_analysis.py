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
    min_cost = []
    k_best = []
    c_best = []
    k1_min_cost = []
    c_at_k1 = []
    nominal_cost = []

class AnalysisTable:
    uk = MethodTable()
    ueq = MethodTable()
    xeq = MethodTable()
    lin = MethodTable()


class SimData:
    def __init__(self, load_dir: str):
        self.load_dir = load_dir
        self.time = np.load(load_dir + 'time.npy')
        self.costs = {
            'aff_uk': np.load(load_dir + 'aff_uk_costs.npy'),
            'aff_ueq': np.load(load_dir + 'aff_ueq_costs.npy'),
            'aff_xeq': np.load(load_dir + 'aff_xeq_costs.npy'),
            'lin': np.load(load_dir + 'lin_costs.npy')
        }
        self.states = {
            'aff_uk': np.load(load_dir + 'aff_uk_states.npy'),
            'aff_ueq': np.load(load_dir + 'aff_ueq_states.npy'),
            'aff_xeq': np.load(load_dir + 'aff_xeq_states.npy'),
            'lin': np.load(load_dir + 'lin_states.npy')
        }
        self.inputs = {
            'aff_uk': np.load(load_dir + 'aff_uk_inputs.npy'),
            'aff_ueq': np.load(load_dir + 'aff_ueq_inputs.npy'),
            'aff_xeq': np.load(load_dir + 'aff_xeq_inputs.npy'),
            'lin': np.load(load_dir + 'lin_inputs.npy')
        }

        self.ref_states = np.load(load_dir + 'ref_states.npy')
        self.Q = np.load(load_dir + 'Q.npy')
        self.k_list = np.load(load_dir + 'k_list.npy')

        with open(load_dir + 'system.txt', 'r') as f:
            self.system = f.readline()

        self.num_c = len(self.costs['aff_uk'][0])
        self.c_list = np.linspace(0, 1, self.num_c)


def main():
    base_dir = f'{os.environ["HOME"]}/data/ampc24/analysis/'
    systems = ['arm', 'beam', 'pendulum', 'multirotor']
    ref_cmds = {}

    def createTableData():
        table = {}
        table['min_cost'] = []
        table['k_best'] = []
        table['c_best'] = []
        table['k1_min_cost'] = []
        table['c_at_k1'] = []
        table['nominal_cost'] = []


    for system in systems:
        refs = os.listdir(base_dir + system)
        ref_cmds[system] = refs
        aff_uk_min_cost = []
        aff_uk_k_at_min = []
        aff_uk_c_at_min = []
        aff_uk_k1_min_cost = []
        aff_uk_c_at_k1 = []
        aff_uk_nominal_cost = []
        aff_uk_c_improvement = []
        aff_uk_k_improvement = []
        aff_uk_ck_improvement = []

        aff_ueq_min_cost = []
        aff_ueq_k_at_min = []
        aff_ueq_c_at_min = []
        aff_ueq_k1_min_cost = []
        aff_ueq_c_at_k1 = []
        aff_ueq_nominal_cost = []
        aff_ueq_c_improvement = []
        aff_ueq_k_improvement = []
        aff_ueq_ck_improvement = []

        aff_xeq_min_cost = []
        aff_xeq_k_at_min = []
        aff_xeq_c_at_min = []
        aff_xeq_k1_min_cost = []
        aff_xeq_c_at_k1 = []
        aff_xeq_nominal_cost = []
        aff_xeq_c_improvement = []
        aff_xeq_k_improvement = []
        aff_xeq_ck_improvement = []

        lin_min_cost = []
        lin_k_at_min = []
        lin_c_at_min = []
        lin_k1_min_cost = []
        lin_c_at_k1 = []
        lin_nominal_cost = []
        lin_c_improvement = []
        lin_k_improvement = []
        lin_ck_improvement = []

        best_aff_cost = []
        nominal_aff_cost = []
        best_lin_cost = []
        nominal_lin_cost = []
        aff_pt_improvement = []
        aff_best_lin_improvement = []
        aff_nom_lin_improvement = []
        best_method = []


        for ref in refs:
            load_dir = f'{base_dir}{system}/{ref}/'
            time = np.load(load_dir + 'time.npy')

            data = SimData(load_dir)
            # aff_uk_costs = np.load(load_dir + 'aff_uk_costs.npy')
            # aff_uk_states = np.load(load_dir + 'aff_uk_states.npy')
            # aff_uk_inputs = np.load(load_dir + 'aff_uk_inputs.npy')

            # aff_ueq_costs = np.load(load_dir + 'aff_ueq_costs.npy')
            # aff_ueq_states = np.load(load_dir + 'aff_ueq_states.npy')
            # aff_ueq_inputs = np.load(load_dir + 'aff_ueq_inputs.npy')

            # aff_xeq_costs = np.load(load_dir + 'aff_xeq_costs.npy')
            # aff_xeq_states = np.load(load_dir + 'aff_xeq_states.npy')
            # aff_xeq_inputs = np.load(load_dir + 'aff_xeq_inputs.npy')

            # lin_costs = np.load(load_dir + 'lin_costs.npy')
            # lin_states = np.load(load_dir + 'lin_states.npy')
            # lin_inputs = np.load(load_dir + 'lin_inputs.npy')

            # xr_hist = np.load(load_dir + 'ref_states.npy')
            # k_list = np.load(load_dir + 'k_list.npy')
            # num_c = len(aff_uk_costs[0])
            # c_list = np.linspace(0, 1, num_c)

            k = 0
            aff_uk_idx = np.argmin(aff_uk_costs[k])
            aff_uk_mc = aff_uk_costs[k,aff_uk_idx]
            aff_uk_c0 = aff_uk_costs[k,0]
            aff_uk_c_improve = (1 - aff_uk_mc / aff_uk_c0) * 100
            aff_uk_c_at_k1.append(c_list[aff_uk_idx])
            aff_uk_k1_min_cost.append(aff_uk_mc)
            aff_uk_nominal_cost.append(aff_uk_c0)
            aff_uk_c_improvement.append(aff_uk_c_improve)

            aff_ueq_idx = np.argmin(aff_ueq_costs[k])
            aff_ueq_mc = aff_ueq_costs[k,aff_ueq_idx]
            aff_ueq_c0 = aff_ueq_costs[k,0]
            aff_ueq_c_improve = (1 - aff_ueq_mc / aff_ueq_c0) * 100
            aff_ueq_c_at_k1.append(c_list[aff_ueq_idx])
            aff_ueq_k1_min_cost.append(aff_ueq_mc)
            aff_ueq_nominal_cost.append(aff_ueq_c0)
            aff_ueq_c_improvement.append(aff_ueq_c_improve)

            aff_xeq_idx = np.argmin(aff_xeq_costs[k])
            aff_xeq_mc = aff_xeq_costs[k,aff_xeq_idx]
            aff_xeq_c0 = aff_xeq_costs[k,0]
            aff_xeq_c_improve = (1 - aff_xeq_mc / aff_xeq_c0) * 100
            aff_xeq_c_at_k1.append(c_list[aff_xeq_idx])
            aff_xeq_k1_min_cost.append(aff_xeq_mc)
            aff_xeq_nominal_cost.append(aff_xeq_c0)
            aff_xeq_c_improvement.append(aff_xeq_c_improve)

            lin_idx = np.argmin(lin_costs[k])
            lin_mc = lin_costs[k,lin_idx]
            lin_c0 = lin_costs[k,0]
            lin_c_improve = (1 - lin_mc / lin_c0) * 100
            lin_c_at_k1.append(c_list[lin_idx])
            lin_k1_min_cost.append(lin_mc)
            lin_nominal_cost.append(lin_c0)
            lin_c_improvement.append(lin_c_improve)

            methods = ['aff (x0,u0)', 'aff (x0,ueq)', 'aff (xeq,u0)', 'lin (xeq,ueq)']
            aff_mc = np.array([aff_uk_mc, aff_ueq_mc, aff_xeq_mc])
            aff_c0 = np.array([aff_uk_c0, aff_ueq_c0, aff_xeq_c0])
            # aff_c_improve = (1 - aff_mc / aff_c0) * 100
            # lin_c_improve = (1 - lin_mc / lin_c0) * 100
            idx = np.argmin(aff_mc)
            best_aff = aff_mc[idx]


        # print(os.listdir(base_dir + system))
    print(ref_cmds)
    return

def cAnalysis(costs):
    k = 0
    c = np.argmin(costs[k])
    cost_min = costs[k,c]
    cost_c0 = costs[k,0]
    return getImprovement(cost_min, cost_c0)

def getImprovement(best, nominal):
    return (nominal/best - 1) * 100

def getTimesBetter(best, nominal):
    return nominal/best

def getReduction(best, nominal):
    return (1 - best / nominal) * 100



if __name__ == '__main__':
    main()
