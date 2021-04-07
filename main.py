"""A Scheme interpreter and its read-eval-print loop."""

#from scheme_interpretor import *
from scheme_reader import *
from interpretor_autodiff import  *


def parse_dsl(next_line):
    expressions=[]
    while True:
        try:
            src = next_line()
            while src.more_on_line:
                expressions.append(scheme_read(src))
        except EOFError:  # <Control>-D, etc.
            return expressions


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Garment DSL Demo')
    parser.add_argument('file', nargs='?',
                        type=argparse.FileType('r'), default=None,
                        help='Scheme file to run')
    args = parser.parse_args()
    lines = args.file.readlines()

    def next_line():
        return buffer_lines(lines)
    raw_expressions = parse_dsl(next_line)

    env=create_global_frame()
    for expr in raw_expressions:
        print(calc(expr,env))
        print(diff(expr,env))
        print(expr)














































