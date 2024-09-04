from .. import ampc_py as ampc

class Test(ampc.ImplicitMPC):
    def __init__(self, num_states: int, num_inputs: int, horizon_length: int, num_knot_points: int, use_input_cost: bool = False, use_slew_rate: bool = False, saturate_states: bool = False) -> None:
        super().__init__(num_states, num_inputs, horizon_length, num_knot_points, use_input_cost, use_slew_rate, saturate_states)
        print('success')

if __name__ == '__main__':
    print('main')
