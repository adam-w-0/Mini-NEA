import matrix_maths
import math
import structure

SEX = True

def check_complete(nodes: list, fixed: list, beams: list):
    """Checks if all the nodes are connected into one structure"""
    # the bridge needs at least 2 fixed nodes
    if len(fixed) < 2:
        return False

    # setting up the dictionary of conections
    connections = {i: [] for i in nodes + fixed}
    for beam in beams:
        connections[beam.node1].append(beam.node2)
        connections[beam.node2].append(beam.node1)

    frontier = [(nodes + fixed)[0]]  # add a starting node to the frontier
    explored = set()

    # complete a breadth first search on the nodes
    while len(frontier) != 0:
        next = frontier.pop(0)
        for i in connections[next]:
            if i not in explored:
                frontier.append(i)
        explored.add(next)

    # If the length of the explored is the same as all the nodes (and fixed)
    # then all the nodes are connected.
    # So return true if all the nodes are connected and there is at least 2 nodes.
    return len(explored) == len(nodes+fixed)


def calculate_fixed(nodes: list, fixed: list, beams: list):
    """Calculates the vertical forces of the fixed nodes if they are on the same y level"""
    equations = []
    solutions = []
    for node in fixed:
        row = [node.position[0] - i.position[0] for i in fixed]
        equations.append(row)
        solutions.append(sum([(node.position[0] - i.centre[0])*i.weight for i in beams]))

    solutions = matrix_maths.solve_simultaneous(equations, solutions)
    for node, sol in zip(fixed, solutions):
        node.vertical_force = sol


