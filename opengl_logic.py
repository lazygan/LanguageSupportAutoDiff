from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

from optimization import *
from dsl_eval import *
from patch import *


class OpenGLFunc:
    def __init__(self,expressions):

        inPutvals,outPutVals = getInputAndOutPutValList(expressions)

        for iv in inPutvals:
            expressions.insert(0, iv.toExpression())

        patches = eval_expressions(expressions, create_global_frame(), outPutVals)

        self.expressions=expressions

        self.patches=patches
    def unproject(self,x,y):
        modelview= glGetDoublev( GL_MODELVIEW_MATRIX);
        projection=glGetDoublev( GL_PROJECTION_MATRIX);
        viewport=glGetIntegerv( GL_VIEWPORT)
        winX = x;
        winY = viewport[3] - y;
        winZ=glReadPixels( x, int(winY), 1, 1, GL_DEPTH_COMPONENT, GL_FLOAT)
        x,y,z=gluUnProject( winX, winY, winZ,modelview, projection, viewport)
        return x,y,winZ

    def unprojectWinz(self,x,y,winZ):
        modelview= glGetDoublev( GL_MODELVIEW_MATRIX);
        projection=glGetDoublev( GL_PROJECTION_MATRIX);
        viewport=glGetIntegerv( GL_VIEWPORT)
        winX = x;
        winY = viewport[3] - y;
        x,y,z=gluUnProject( winX, winY, winZ,modelview, projection, viewport)
        return x,y,winZ

    def drawFunc(self):
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
        for patch in self.patches:
            patch.travel(drawAcp)
        glEnd()
        glPointSize(3)
        glBegin(GL_POINTS)
        for patch in self.patches:
            patch.travel(drawAcpBcpLine)
        glEnd()

        glFlush()


    selectedAcp=None
    winZ=None
    def mouseClick(self, button, state, x, y):
        global selectedAcp
        global winZ
        selectedAcp = None
        if button!=0:
            return
        if state==0:
            posx, posy, winZ= self.unproject(x,y)

            def fn(acp, _):
                global selectedAcp
                if math.sqrt((acp.x - posx) ** 2) < 0.02 and math.sqrt((acp.y - posy) ** 2) < 0.02:
                    selectedAcp = acp

            for patch in self.patches:
                patch.travel(fn)
        elif state==1:
            for patch in self.patches:
                theta = optimization(patch.P)
                print(theta)


    def mousePressMove(self,x, y):

        if selectedAcp==None:
            return
        posx,posy,_=self.unprojectWinz(x,y,winZ)
        selectedAcp.x=posx
        selectedAcp.y=posy
