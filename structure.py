import math


def distance_from(structure, position: tuple):
    """Gives the distance of a structure from the position given"""
    x1, y1 = position
    if isinstance(structure, Node):  # if the structure is a node or fixed node
        x2, y2 = structure.position
    else:
        x2, y2 = structure.centre
    return ((x1 - x2)**2 + (y1 - y2)**2)**(1/2)


def nearest_structure(structures: list, position: tuple):
    """Gives the nearest structure to the position given"""
    struc = None
    distance = math.inf
    for i in structures:
        if distance_from(i, position) < distance:
            struc = i
            distance = distance_from(i, position)
    return struc


class Node:
    def __init__(self, position: tuple):
        self._position = position

    @property
    def position(self):
        """Returns the position of the node"""
        return self._position

    @position.setter
    def position(self, position: tuple):
        """Allows for assignment of the position of the node"""
        if not isinstance(position, tuple):
            raise TypeError(f"The attempted position change was an invalid data type ({type(position)})")
        if len(position) != 2:
            raise TypeError("The attempted position change was an invalid length")
        self._position = position


class FixedNode(Node):
    def __init__(self, position: tuple):
        super().__init__(position)
        self.vertical_force = 0
        self.horizontal_force = 0


MASS_PER_LENGTH = 1
GRAVITY = 9.81


class Beam:
    def __init__(self, node1: Node, node2: Node):
        self.node1 = node1
        self.node2 = node2
        self.mass = ((node1.position[0] - node2.position[0])**2 +
                     (node1.position[1] - node2.position[1])**2)**(1/2) * MASS_PER_LENGTH

    def __eq__(self, other):
        if not isinstance(other, Beam):
            return False

        return (self.node1 is other.node1 and self.node2 is other.node2) \
               or (self.node1 is other.node2 and self.node2 is other.node1)

    @property
    def centre(self):
        """Returns the position of the centre of the beam"""
        x1, y1 = self.node1.position
        x2, y2 = self.node2.position
        return (x1 + x2)/2, (y1 + y2)/2

    @property
    def ends(self):
        """Returns the positions of the ends of the nodes the beam joins"""
        return self.node1.position, self.node2.position

    @property
    def weight(self):
        """Returns the weight of the beam"""
        return self.mass * GRAVITY
