"""A Scheme interpreter and its read-eval-print loop."""

from interpretor_autodiff import  *


def parse_dsl(buffer):
    expressions=[]
    while buffer.more_on_line:
                expressions.append(scheme_read( buffer))
    return expressions


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Garment DSL Demo')
    parser.add_argument('file', nargs='?',
                        type=argparse.FileType('r'), default=None,
                        help='Scheme file to run')
    args = parser.parse_args()
    lines = args.file.readlines()

    raw_expressions = parse_dsl(buffer_lines(lines))

    env=create_global_frame()
    for expr in raw_expressions:
        print(calc(expr,env))
        print(diff(expr,env))














































