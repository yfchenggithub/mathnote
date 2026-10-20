from pathlib import Path
import sys
import numpy as np
from manim import *
sys.path.insert(0,str(Path(__file__).resolve().parent))
from model import *
config.background_color='#F7F8FA'
config.frame_width,config.frame_height=9,16
INK,MUTED,BLUE,ORANGE,GREEN,PURPLE,AXIS='#213044','#526275','#2778BD','#CD6031','#158068','#8055B2','#A7B4C2'
def cn(s,size=26,color=INK): return Text(s,font='Microsoft YaHei',font_size=size,color=color)
def eq(s,size=32,color=INK): return MathTex(s,font_size=size,color=color)
def swap(scene,*pairs):
    scene.play(*[FadeOut(a) for a,b in pairs],run_time=.15)
    for a,b in pairs: a.become(b)
    scene.play(*[FadeIn(a) for a,b in pairs],run_time=.15)
def number(symbol,value,pos,color=INK,places=2):
    d=DecimalNumber(-88.888,num_decimal_places=places,font_size=31,color=color)
    g=VGroup(eq(symbol+r"\approx",31,color),d).arrange(RIGHT,buff=.12).move_to(pos)
    anchor=d.get_right().copy()
    def update(m):
        v=value(); m.set_value(0 if abs(v)<.00001 else v).align_to(anchor,RIGHT)
    d.add_updater(update); d.update(0); return g
def axes(xy,xlim,ylim):
    return VGroup(Line(xy((xlim[0],0)),xy((xlim[1],0)),color=AXIS,stroke_width=1.3),Line(xy((0,ylim[0])),xy((0,ylim[1])),color=AXIS,stroke_width=1.3),eq('O',21,MUTED).move_to(xy((0,0))+LEFT*.2+DOWN*.23))


class C062Animation(Scene):
    def construct(self):
        lo,hi=(.55,PI-.55) if KIND=='ellipse' else (-.7,.7) if KIND=='hyperbola' else (.7,1.5)
        t=ValueTracker(lo); shift=-1.2 if KIND=='parabola' else 0
        xy=lambda p:np.array([1.15*p[0]+shift,1.15*p[1]+.45,0])
        title=cn('中点坐标，决定弦的斜率',30).move_to([0,6.9,0])
        caption=cn('连接两端点，标出弦中点 M').move_to([0,5.6,0])
        if KIND=='ellipse':curveplot=ParametricFunction(lambda u:xy(curve(u)),t_range=[0,TAU],color=BLUE)
        elif KIND=='hyperbola':curveplot=VGroup(*[ParametricFunction(lambda u,s=s:xy(curve(u,s)),t_range=[-1.3,1.3],color=BLUE) for s in (-1,1)])
        else:curveplot=ParametricFunction(lambda u:xy(curve(u)),t_range=[-1.5,2.6],color=BLUE)
        def moving():
            A,B=endpoints(t.get_value());M=midpoint(t.get_value())
            return VGroup(Line(xy(A),xy(B),color=ORANGE,stroke_width=3),Dot(xy(A),color=ORANGE,radius=.06),Dot(xy(B),color=ORANGE,radius=.06),Dot(xy(M),color=GREEN,radius=.08),eq('M',26,GREEN).move_to(xy(M)+DOWN*.3))
        construct=always_redraw(moving)
        read=number('k',lambda:slope(t.get_value()),[0,-3.7,0],ORANGE)
        formula=eq(r'k=\frac{p}{y_0}',38,GREEN).move_to([0,-5.1,0])
        note=eq(r'M=(x_0,y_0),\quad y_0\ne0',29,MUTED).move_to([0,-6.5,0])
        self.add(title,caption,curveplot,construct,read,formula,note)
        self.wait(.8)
        self.play(t.animate.set_value(hi),run_time=4)
        swap(self,(caption,cn('弦在变化，中点式始终成立',26,GREEN).move_to(caption)))
        self.wait(1.3)
        self.play(t.animate.set_value(lo),run_time=4)
        swap(self,(caption,cn('连接两端点，标出弦中点 M').move_to(caption)))
        self.wait(.5)
