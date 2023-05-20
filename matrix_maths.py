

def increase_index(value):
    if isinstance(value, slice):
        value = slice(None if value.start is None else value.start - 1,
                      None if value.stop is None else value.stop - 1,
                      value.step)
    else:
        value -= 1
    return value


class Matrix:
    def __init__(self, values):
        size = len(values), len(values[0])
        self._size = size
        self._values = values

    @property
    def size(self):
        return self._size

    def __getitem__(self, item):
        i, j = item
        if not isinstance(item, tuple):
            raise Exception("The matrix has been incorrectly indexed")
        if len(item) != 2:
            raise Exception("The indexing requires 2 arguments")
        i, j = increase_index(i), increase_index(j)
        if isinstance(i, int) and isinstance(j, int):
            return self._values[i][j]
        return [list(m[j]) for m in self._values[i]]

    def __setitem__(self, item, value):
        i, j = item
        if not (isinstance(i, int) and isinstance(j, int)):
            if isinstance(j, slice):
                value = [a + b + c for a, b, c in zip(self[i, :(1 if j.start is None else j.start)], value, self[i, j.stop:(None if j.stop is not None else 1)])]
            else:
                value = [a + b + c for a, b, c in zip(self[i, :j], value, self[i, j+1:])]

        if not isinstance(item, tuple):
            raise Exception("The matrix has been incorrectly indexed")
        if len(item) != 2:
            raise Exception("The indexing requires 2 arguments")
        i, j = increase_index(i), increase_index(j)
        if isinstance(i, int) and isinstance(j, int):
            self._values[i][j] = value
        self._values[i] = value

    def __iter__(self):
        for row in self._values:
            yield row

    def __repr__(self):
        return f"Matrix({self._values})"

    def __str__(self):
        return '\n'.join([' '.join(map(str, row)) for row in self._values])

    def __mul__(self, other):
        if isinstance(other, Matrix):
            if self._size[1] != other._size[0]:
                raise Exception("The matrices cannot be multiplies as the dimensions are incompatible.")

            return Matrix([[sum(a * b for a, b in zip(a_row, b_col))
                            for b_col in zip(*other._values)]
                           for a_row in self._values])
        if isinstance(other, float) or isinstance(other, int):
            return Matrix([[other * value for value in row] for row in self._values])
        raise Exception("Incompatible type for multiplication with a matrix")

    def __rmul__(self, other):
        if isinstance(other, float) or isinstance(other, int):
            return Matrix([[other * value for value in row] for row in self._values])
        raise Exception("Incompatible type for multiplication with a matrix")

    def __add__(self, other):
        return Matrix([[a+b for a, b in zip(a_row, b_row)] for a_row, b_row in zip(self._values, other._values)])

    def __sub__(self, other):
        return Matrix([[a - b for a, b in zip(a_row, b_row)] for a_row, b_row in zip(self._values, other._values)])

    @staticmethod
    def minor(matrix_values, position):
        i, j = position
        m = matrix_values[:i-1] + matrix_values[i:]  # remove the row
        m = [a[:j - 1] + a[j:] for a in m]  # remove the column
        return Matrix(m)

    def determinant(self):
        if self._size[0] != self._size[1]:
            raise Exception("Matrix is not square so determinant cannot be taken")
        if self._size[0] == 1:
            return self._values[0][0]
        total = 0
        for index, i in enumerate(self._values[0]):
            minor = Matrix.minor(self._values, (1, index+1))
            total += i * minor.determinant() * (-1)**index
        return total

    def transposed(self):
        return Matrix([[self._values[j][i]
                        for j in range(self._size[1])]
                       for i in range(self._size[0])])

    def inverse(self):
        det = self.determinant()
        if det == 0:
            raise Exception("Matrix is singular so no inverse exists")
        m = [[Matrix.minor(self._values, (i, j)).determinant()
              for j in range(1, self._size[1]+1)]
             for i in range(1, self._size[0]+1)]
        m = [[value * (-1)**(i+j)
              for j, value in enumerate(row)]
             for i, row in enumerate(m)]
        m = Matrix(m).transposed()
        return (1/det) * m


def solve_simultaneous(equations: list, solutions: list) -> list:
    """Takes a 2d array of the equations with each position representing a coefficient of a variable
    and a 1d array of the answers to the equations and returns the solutions in a 1d array.
    i.e. 2x + 3y = 5 and 3x + y = 2 would be input as solve_simultaneous([[2, 3], [3, 1]], [5, 2])"""
    equations, solutions = Matrix(equations), Matrix([[i] for i in solutions])  # Turning the inputs into 2d matrices
    solns = equations.inverse() * solutions  # gets the solutions as a 2d array
    return [i[0] for i in solns]

