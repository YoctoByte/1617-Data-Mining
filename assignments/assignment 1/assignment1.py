import numpy as np
from math import pi
from packages import xlrd
import matplotlib.pyplot as plt


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


def ass1_2_1():
    print('assignment 1.2.1')
    # a.
    filename = 'data/nanonose.xls'
    workbook = xlrd.open_workbook(filename)
    sheet = workbook.sheet_by_index(0)
    x = np.zeros((90, 8))
    for col_nr in range(8):
        col = sheet.col_values(col_nr+3)[2:]
        x[:, col_nr] = col
    print('a. X =\n', x)

    # b.
    plt.scatter(x[:, 0], x[:, 1])
    plt.show()
    plt.scatter(x[:, 2], x[:, 3])
    plt.show()
    plt.scatter(x[:, 4], x[:, 5])
    plt.show()
    plt.scatter(x[:, 6], x[:, 7])
    plt.show()


def ass1_2_2():
    print('assignment 1.2.2')

    def pca(matrix):
        mu = np.mean(matrix, axis=0)
        zero_mean_data = matrix - (mu * np.ones((matrix.shape[0], 1)))
        u, s, v = np.linalg.svd(zero_mean_data)
        print(u.shape, s.shape, v.shape)
        print(s)
        for _ in range(matrix.shape[1]):
            pass

    filename = 'data/nanonose.xls'
    workbook = xlrd.open_workbook(filename)
    sheet = workbook.sheet_by_index(0)
    x = np.zeros((90, 8))
    for col_nr in range(8):
        col = sheet.col_values(col_nr + 3)[2:]
        x[:, col_nr] = col

    pca(x)
    # todo: Ask student assistant about PCA


def ass1_3_1():
    pass


def ass1_3_2():
    pass


if __name__ == '__main__':
    # ass1_1_1()
    # ass1_1_2()
    # ass1_2_1()
    ass1_2_2()
