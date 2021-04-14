"""A Scheme interpreter and its read-eval-print loop."""

from interpretor_autodiff import  *


def parse_dsl(buffer:Buffer):
    expressions=[]
    while buffer.more_on_line:
                expressions.append(scheme_read( buffer))
    return expressions


import argparse
from sugar_parser import Lexer,AbrvalgSyntaxError,report_syntax_error,TokenStream,Parser

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Garment DSL Demo')

    parser.add_argument('file', nargs='?',
                        type=argparse.FileType('r'), default=None,
                        help='Scheme file to run')
    args = parser.parse_args()
    buffer=None
    if args.file.name.endswith(".scm") :
        lines = args.file.readlines()
        for i in range(len(lines)):
            lines[i]=lines[i].strip('\n')
            lines[i]=tokenize_line(lines[i])
        buffer=Buffer(lines)
    elif args.file.name.endswith(".gan"):
        lines = args.file.read()
        lexer = Lexer()
        try:
            tokens = lexer.tokenize(lines)
        except AbrvalgSyntaxError as err:
            report_syntax_error(lexer, err)
            exit()
        token_stream = TokenStream(tokens)
        try:
            program = Parser().parse(token_stream)
        except AbrvalgSyntaxError as err:
            report_syntax_error(lexer, err)

    if buffer==None:
        exit()

    raw_expressions = parse_dsl(buffer)

    env=create_global_frame()
    for expr in raw_expressions:
        print("----------")
        print(calc(expr,env))
        print(diff(expr,env))

        res={"x1":0,"x2":0}
        print(reverse_diff(expr,env,res,1))
        print(res)
        #print("========")














































