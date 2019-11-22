import itertools


def elder_age_naive(m, n, l, t):
    return sum(filter(lambda z: z > 0, ((x ^ y) - l for x, y in itertools.product(range(m), range(n))))) % t



def decompose(width, height):
    """Decompose a rectangle in tiles

    Try to extract biggest squares of size % 8 == 0, then the remaining rectangles

    :param width: Width of the rectangle
    :param height: Height of the rectangle
    :return: an iterable list of tiles
    """
    pass


def solve(m, n, l, t):
    # If m is smaller than n, swap the values
    # Thit step is optional, but it give me less brain knots ;)
    if m < n:
        m, n = n, m

    for tile in decompose(m, n):
        print(tile)



if __name__ == '__main__':
    m = 8
    n = 5
    l = 1
    t = 100
    print(solve(m, n, l, t), elder_age_naive(m, n, l, t))