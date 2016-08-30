import numpy as np
from math import pi


def ass1_1_1():
    print('assignment 1.1.1')
    # vector generation:
    x = np.array(list(range(6, 13)))
    y = np.array(list(range(3, 28, 4)))
    w = np.array([1, 1, 0, 0.5, 1, 1.5, 2, 0, 0])
    s = np.array(np.arange(100, 95, -1.2))
    z = np.array(np.arange(0.7, 3, 0.3))

    # a.
    v = 3*x + y
    print('a. v =', v)

    # b.
    dot_x_y = np.dot(x, y)
    print('b. dot x, y =', dot_x_y)

    # c.
    t = pi*(s+4)
    print('c. t =', t)

    # d.
    z -= 1
    print('d. z =', z)

    # e.
    x[-3:] = 4
    print('e. x =', x)

    # f.
    r = 2*w - 5
    print('f. r =', r)
    print()


def ass1_1_2():
    print('assignment 1.1.2')
    # matrix generation:
    m = np.array([[1, 2, 3],
                  [6, 8, 4],
                  [6, 7, 5]])
    n = np.array([[4, 6],
                  [7, 2],
                  [5, 1]])
    p = np.array([[2, 5],
                  [5, 5]])

    # a.
    a = np.dot(m, n) + n
    print('a. A =\n', a)

    # b.
    b = np.dot(n.T, m)
    print('b. B =\n', b)

    # c.
    c = np.linalg.inv(p) + p
    print('c. C =\n', c)

    # d.
    try:
        d = np.dot(np.dot(a, c), (c + b))
    except ValueError:
        d = 'D could not be calculated.'
    print('d. D =\n', d)

    # e.
    print('e. ')
    for matrix_name, matrix in [('M', m), ('N', n), ('P', p)]:
        try:
            eig_val, eig_vec = np.linalg.eig(matrix)
        except np.linalg.linalg.LinAlgError:
            eig_val, eig_vec = 'Could not be calculated', 'Could not be calculated'
        print('Eigen value ' + matrix_name + ' =', eig_val)
        print('Eigen vector ' + matrix_name + ' =\n', eig_vec)

    print()


if __name__ == '__main__':
    ass1_1_1()
    ass1_1_2()
