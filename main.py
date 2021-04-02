"""A Scheme interpreter and its read-eval-print loop."""

from scheme_reader import *

from opengl_logic import *

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

    openglFunc=OpenGLFunc(raw_expressions)

    glutInit()
    glutInitDisplayMode(GLUT_SINGLE | GLUT_RGBA)
    glutInitWindowSize(600, 600)
    glutCreateWindow(b"First")
    glOrtho(0.0, 1.0, 0.0, 1.0, -1.0, 1.0)
    glutDisplayFunc(openglFunc.drawFunc)
    glutMouseFunc(openglFunc.mouseClick)
    glutMotionFunc(openglFunc.mousePressMove)
    glutMainLoop()

