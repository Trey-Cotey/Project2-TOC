from src.helpers.turing_machine import TuringMachineSimulator

# ==========================================
# PROGRAM 1: Nondeterministic TM [cite: 137]
# ==========================================
class NTM_Tracer(TuringMachineSimulator):
    # Make a new initializer to set up the NTM correctly (better transition format)
    def __init__ (self, filename):
        super().__init__(filename)
        self.accepting = [self.accept_state]
        self.rejecting = [self.reject_state]
        # Change transition format, should look like: (state, symbol) -> [(next state, write, direction), ...]
        self.new_transitions = {}
        for state, transition_list in self.transitions.items():
            for transition in transition_list:
                read_symbol = transition['read'][0]  # single tape
                next_state = transition['next']
                write_symbol = transition['write'][0]
                direction = transition['move'][0]
                key = (state, read_symbol)
                if key not in self.new_transitions:
                    self.new_transitions[key] = []
                self.new_transitions[key].append((next_state, write_symbol, direction))

        self.transitions = self.new_transitions

    # Run function to actually find the configurations
    def run(self, input_string, max_depth):
        print(f"Tracing NTM: {self.machine_name} on input '{input_string}'")
        print()

        # Initial Configuration: ["", start_state, input_string] - this is the root
        initial_config = ["", self.start_state, input_string]

        # The tree is a list of lists of configurations
        tree = [[initial_config]] # tree[0] is just initial config, which makes sense because it is the root
        parents = [[(-1, -1)]] # root has no parent, so first parent has nothing

        depth = 0
        num_transitions = 0
        edge_count = 0
        internal_node_count = 0
        solution = None
        accepted = False

        while depth < max_depth and not accepted:
            current_level = tree[-1]
            next_level = []
            all_rejected = True
            next_parent = []

            # TODO: STUDENT IMPLEMENTATION NEEDED
            # 1. Iterate through every config in current_level.
            # 2. Check if config is Accept (Stop and print success) [cite: 179]
            # 3. Check if config is Reject (Stop this branch only) [cite: 181]
            # 4. If not Accept/Reject, find valid transitions in self.transitions.
            # 5. If no explicit transition exists, treat as implicit Reject.
            # 6. Generate children configurations and append to next_level[cite: 148].

            for i, config in enumerate(current_level):
                left, state, right = config

                # If accept state, we found a solution - break
                if state in self.accepting:
                    accepted = True
                    solution = (depth, i)
                    break
                # If reject state, continue to next config - this one didn't work
                elif state in self.rejecting:
                    continue
                
                # If neither accepting or rejecting, can branch
                all_rejected = False
                internal_node_count += 1

                head = '_'
                if right:
                    head = right[0]

                key = (state, head)
                
                # If no transition exists, reject
                if key not in self.transitions:
                    next_level.append([left, self.rejecting[0], right if right else '_'])
                    next_parent.append((i, -1))
                    num_transitions += 1
                    edge_count += 1
                    continue

                edge_count += len(self.transitions[key])
                # Add all possible branches to next level
                for index, (new_state, write_symbol, direction) in enumerate(self.transitions[key]):
                    if right:
                        new_right = write_symbol + right[1:]
                    else:
                        new_right = write_symbol

                    new_left = left
                    if direction == "R":
                        if new_right:
                            new_left = left + new_right[0]
                            new_right = new_right[1:]
                        else:
                            new_left = left + "_"
                            new_right = ""
                    elif direction == "L":
                        if new_left:
                            new_head = new_left[-1]
                            new_left = new_left[:-1]
                            new_right = new_head + new_right
                        else:
                            new_right = "_" + new_right

                    if new_right == "":
                        new_right = "_"

                    num_transitions += 1
                    next_level.append([new_left, new_state, new_right])
                    next_parent.append((i, index))

            # If a solution is found (accepted), print correctly and determine degree
            if accepted:
                depth_idx, config_idx = solution
                print(f"String accepted in {depth} steps")
                print(f"Total transitions: {num_transitions}")

                if internal_node_count > 0:
                    degree = edge_count / internal_node_count
                else:
                    degree = 1.0
                print(f"Nondeterminism degree: {degree:.3f}")

                self.print_trace_path(tree, parents, depth_idx, config_idx)
                return
            # If no solution, reject and print correctly
            if all_rejected:
                # TODO: Handle "String rejected" output [cite: 258]
                print(f"String rejected in {depth} steps")
                print(f"Total transitions: {num_transitions}")

                if internal_node_count > 0:
                    degree = edge_count / internal_node_count
                else:
                    degree = 1.0
                print(f"Nondeterminism degree: {degree:.3f}")
                return
            # If neither, go to the next level
            tree.append(next_level)
            parents.append(next_parent)
            depth += 1
        
        print(f"Execution stopped after {max_depth} steps.")  # [cite: 259]

    # Function to properly print the path if a solution is found
    def print_trace_path(self, tree, parents, level, index):
        """
        Backtrack and print the path from root to the accepting node.
        Ref: Section 4.2 [cite: 165]
        """
        path = []
        # Logic of constructing the path
        while level >= 0:
            config = tree[level][index]
            path.append(config)

            parent_index, _ = parents[level][index]
            if parent_index == -1:
                break

            index = parent_index
            level -= 1
        path.reverse()
        # Actual printing
        print("\nTrace (root → accept):")
        for left, state, right in path:
            if right == "":
                right = "_"
            head = right[0]
            tail = right[1:] if len(right) > 1 else ""
            if tail == "":
                print(f"{left}  {state}  {head}")
            else:
                print(f"{left}  {state}  {head}{tail}")