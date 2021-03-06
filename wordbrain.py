import argparse
import copy
import math
from collections import namedtuple


class Node(object):
    def __init__(self):
        self.children = dict()
        self.depths = set()

    def add_word(self, word):
        self.depths.add(len(word))

        c, rest = word[0], word[1:]

        node = self.children.get(c)

        if node is None:
            node = Node()
            self.children[c] = node

        if len(rest) == 0:
            node.depths.add(0)
        else:
            node.add_word(rest)

    def is_word(self, word):
        c, rest = word[0], word[1:]

        node = self.children.get(c)

        if node is None:
            return False

        if len(rest) == 0:
            return 0 in node.depths
        else:
            return node.is_word(rest)

    def is_prefix(self, word, n):
        if n not in self.depths:
            return False

        if len(word) == 0:
            return True

        c, rest = word[0], word[1:]

        node = self.children.get(c)

        if node is None:
            return False

        return node.is_prefix(rest, n - 1)


Point = namedtuple('Point', ['x', 'y'])


def chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i:i+n]


class Grid(object):
    def __init__(self, grid):
        self.grid = copy.deepcopy(grid)

    @classmethod
    def from_string(cls, grid):
        n = len(grid)

        if n == 0:
            raise ValueError('Empty grid!')

        size = int(math.sqrt(n))

        if size * size != n:
            raise ValueError('Must be a square grid!')

        grid = [list(x) for x in chunks(grid, size)]

        return cls(grid)

    @property
    def width(self):
        return len(self.grid[0])

    @property
    def height(self):
        return len(self.grid)

    def get_letter(self, point):
        return self.grid[point.y][point.x]

    def set_letter(self, point, letter):
        self.grid[point.y][point.x] = letter

    def get_word(self, path):
        letters = []

        for point in path:
            letter = self.get_letter(point)
            assert letter is not None
            letters.append(letter)

        return ''.join(letters)

    def get_words(self, paths):
        words = []
        grid = self

        for path in paths:
            word = grid.get_word(path)
            words.append(word)
            grid = grid.clone()
            grid.remove_path(path)

        return words

    def remove_path(self, path):
        for point in path:
            self.remove_letter(point)

    def remove_letter(self, point):
        x = point.x
        y = point.y

        while y >= 0:
            if y == 0:
                new_letter = None
            else:
                new_letter = self.get_letter(Point(x, y - 1))

            self.set_letter(Point(x, y), new_letter)
            y -= 1

    def clone(self):
        return self.__class__(self.grid)

    def solve(self, dictionary, ns, permute=False, first=False):
        if len(ns) == 1:
            paths = self.search(dictionary, ns[0], first=first)
            solutions = [[path] for path in paths]
        else:
            if permute:
                indexes = xrange(len(ns))
            else:
                indexes = [0]

            solutions = []

            for index in indexes:
                n = ns[index]
                new_ns = ns[0:index] + ns[index+1:]

                paths = self.search(dictionary, n)

                for path in paths:
                    new_grid = self.clone()
                    new_grid.remove_path(path)
                    sub_solutions = new_grid.solve(dictionary, new_ns, permute=permute, first=first)

                    if first and sub_solutions:
                        return [[path] + sub_solutions[0]]

                    for solution in sub_solutions:
                        solutions.append([path] + solution)

        return solutions

    def search(self, dictionary, n, path=None, first=False):
        if path is None:
            path = list()
            min_x = 0
            max_x = self.width
            min_y = 0
            max_y = self.height
        else:
            point = path[-1]
            min_x = max(0, point.x - 1)
            max_x = min(point.x + 2, self.width)
            min_y = max(0, point.y - 1)
            max_y = min(point.y + 2, self.height)

        paths = list()

        for x in xrange(min_x, max_x):
            for y in xrange(min_y, max_y):
                point = Point(x, y)

                # Already used this letter
                if point in path:
                    continue

                # Blank letter
                if self.get_letter(point) is None:
                    continue

                new_path = list(path) + [point]
                word = self.get_word(new_path)

                if n == 1:
                    if dictionary.is_word(word):
                        if first:
                            return [new_path]
                        else:
                            paths.append(new_path)
                else:
                    if dictionary.is_prefix(word, len(path) + n):
                        paths.extend(self.search(dictionary, n - 1, new_path, first))

        return paths


def build_dictionary(n):
    dictionary = Node()

    with open('/usr/share/dict/words') as f:
        for line in f:
            word = line.rstrip()

            if len(word) in n:
                word = word.upper()
                dictionary.add_word(word)

    return dictionary


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('grid')
    parser.add_argument('n', type=int, nargs='+')
    parser.add_argument('--permute', action='store_true')
    parser.add_argument('--first', action='store_true')
    args = parser.parse_args()

    dictionary = build_dictionary(args.n)

    grid = Grid.from_string(args.grid.upper())

    solutions = grid.solve(dictionary, args.n, permute=args.permute, first=args.first)

    for solution in solutions:
        words = grid.get_words(solution)
        print ' '.join(words)
