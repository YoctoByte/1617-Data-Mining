import numpy as np
from math import pi


def ass1_1_1():
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

ass1_1_1()
