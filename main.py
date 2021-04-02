"""A Scheme interpreter and its read-eval-print loop."""

from scheme_interpretor import *

from Patch import *

expressions=[]
def parse_dsl(next_line):
    while True:
        try:
            src = next_line()
            while src.more_on_line:
                expressions.append(scheme_read(src))
        except EOFError:  # <Control>-D, etc.
            return expressions

def eval_expressions(expressions, env,outPutVals):
     for expr in expressions:
         scheme_eval(expr, env)

     patches=[]
     for ov in outPutVals:
         patchPairChain=scheme_eval(ov.toExpression(),env)
         patches.append(Patch(patchPairChain))
     return patches

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *


def drawFunc():
    glClearColor(1.0, 1.0, 1.0, 0.0)
    glClear(GL_COLOR_BUFFER_BIT)
    # 设置点大小

    # 只绘制端点
    def beizer(x0,x1,x2,x3,t):
        return x0*(1-t)**3+3*x1*t*(1-t)**2+3*x2*t**2*(1-t)+x3*t**3

    def drawBeizerCurve(p1,p2):
        d=p1.distance(p2)
        ulen=0.005
        n=int(d/ulen)
        glColor(0,0,0,1)
        for i in range(n):
            x=beizer(p1.x,p1.nextBcp.x,p2.preBcp.x,p2.x,i/n)
            y=beizer(p1.y,p1.nextBcp.y,p2.preBcp.y,p2.y,i/n)
            glVertex3f(x, y, 0)


    def drawAcpAcp(p1,p2):
        if p1.nextBcp!=None and p2.preBcp!=None:
            drawBeizerCurve(p1,p2)
        else:
            drawLine(p1,p2)

    def drawLine(p1,p2):
        d=p1.distance(p2)
        ulen=0.01
        n=int(d/ulen)
        deltax=(p2.x-p1.x)/n
        deltay=(p2.y-p1.y)/n
        glColor(0,0,0,1)
        for i in range(n):
            x=p1.x+i*deltax
            y=p1.y+i*deltay
            glVertex3f(x, y, 0)

    def drawAcpBcpLine(acp,nacp):
        glColor(0,0,0,1)
        if acp.preBcp!=None:
            drawLine(acp,acp.preBcp)
        if acp.nextBcp!=None:
            drawLine(acp,acp.nextBcp)
        drawAcpAcp(acp,nacp)


    def drawAcp(acp,_):
        glColor(1.0,0.0,0.0,1)
        glVertex3f(acp.x,acp.y,0)
        glColor(0.8,0.8,0,1)
        if acp.preBcp!=None:
            glVertex3f(acp.preBcp.x, acp.preBcp.y, 0)
        if acp.nextBcp!=None:
            glVertex3f(acp.nextBcp.x, acp.nextBcp.y, 0)


    glPointSize(8)
    glBegin(GL_POINTS)
    for patch in patches:
        patch.travel(drawAcp)
    glEnd()
    glPointSize(3)
    glBegin(GL_POINTS)
    for patch in patches:
        patch.travel(drawAcpBcpLine)
    glEnd()

    glFlush()

def unproject(x,y):
    modelview= glGetDoublev( GL_MODELVIEW_MATRIX);
    projection=glGetDoublev( GL_PROJECTION_MATRIX);
    viewport=glGetIntegerv( GL_VIEWPORT)
    winX = x;
    winY = viewport[3] - y;
    winZ=glReadPixels( x, int(winY), 1, 1, GL_DEPTH_COMPONENT, GL_FLOAT)
    x,y,z=gluUnProject( winX, winY, winZ,modelview, projection, viewport)
    return x,y,winZ

def unprojectWinz(x, y,winZ):
    modelview= glGetDoublev( GL_MODELVIEW_MATRIX);
    projection=glGetDoublev( GL_PROJECTION_MATRIX);
    viewport=glGetIntegerv( GL_VIEWPORT)
    winX = x;
    winY = viewport[3] - y;
    x,y,z=gluUnProject( winX, winY, winZ,modelview, projection, viewport)
    return x,y,winZ



selectedAcp=None
winZ=None
def mousePress(button,  state,x,y):
    global selecetedAcp
    global winZ
    selectedAcp = None
    if button!=0:
        return
    posx, posy, winZ= unproject(x,y)

    def fn(acp, _):
        global selectedAcp
        if math.sqrt((acp.x - posx) ** 2) < 0.02 and math.sqrt((acp.y - posy) ** 2) < 0.02:
            selectedAcp = acp

    for patch in patches:
        patch.travel(fn)

def mousePressMove(x, y):
    if selectedAcp==None:
        return 
    posx,posy,_=unprojectWinz(x,y,winZ)
    selectedAcp.x=posx
    selectedAcp.y=posy
    pass


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


    expressions = parse_dsl(next_line)
    inPutvals, outPutVals = getInputAndOutPutValList(expressions)

    for iv in inPutvals:
        expressions.insert(0, iv.toExpression())

    patches = eval_expressions(expressions, create_global_frame(), outPutVals)
    print(patches)

    glutInit()
    glutInitDisplayMode(GLUT_SINGLE | GLUT_RGBA)
    glutInitWindowSize(600, 600)
    glutCreateWindow(b"First")
    glOrtho(0.0, 1.0, 0.0, 1.0, -1.0, 1.0)
    glutDisplayFunc(drawFunc)
    glutMouseFunc(mousePress)
    glutMotionFunc(mousePressMove)
    glutMainLoop()

