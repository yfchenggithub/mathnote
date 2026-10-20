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


class C076Animation(Scene):
    def construct(self):
        t=ValueTracker(-1.7);xy=lambda p:np.array([.9*p[0]-.7,.9*p[1]+.4,0])
        title=cn('点与极线，可以互换',31).move_to([0,6.9,0])
        caption=cn('Q 沿 P 的极线移动',26).move_to([0,5.6,0])
        ellipse=ParametricFunction(lambda u:xy((a*np.cos(u),b*np.sin(u))),t_range=[0,TAU],color=BLUE)
        # Clip both mathematical lines to the fixed plot rectangle, preserving the exact equations.
        def clipped(U):
            A,B=U[0]/a**2,U[1]/b**2;hits=[]
            if abs(B)>1e-9:
                for x in (-3.5,4.2):
                    y=(1-A*x)/B
                    if -3.2<=y<=3.6:hits.append((x,y))
            if abs(A)>1e-9:
                for y in (-3.2,3.6):
                    x=(1-B*y)/A
                    if -3.5<=x<=4.2:hits.append((x,y))
            return hits[0],hits[1]
        lP=Line(*[xy(v) for v in clipped(P)],color=PURPLE)
        moving=always_redraw(lambda:VGroup(Line(*[xy(v) for v in clipped(Q(t.get_value()))],color=ORANGE),
            Dot(xy(Q(t.get_value())),color=PURPLE,radius=.075),
            eq('Q',26,PURPLE).move_to(xy(Q(t.get_value()))+RIGHT*.3)))
        self.add(title,caption,ellipse,lP,moving,Dot(xy(P),color=ORANGE,radius=.075),eq('P',26,ORANGE).move_to(xy(P)+UP*.3),
            eq(r'Q\in l_P\ \Longleftrightarrow\ P\in l_Q',35,GREEN).move_to([0,-4.4,0]),
            eq(r'l_P:\ \frac{x_Px}{a^2}+\frac{y_Py}{b^2}=1',31,MUTED).move_to([0,-6,0]))
        self.wait(.8);self.play(t.animate.set_value(1.7),run_time=4)
        swap(self,(caption,cn('Q 的极线始终经过固定点 P',26,GREEN).move_to(caption)))
        self.wait(1);self.play(t.animate.set_value(-1.7),run_time=4)
        swap(self,(caption,cn('Q 沿 P 的极线移动',26).move_to(caption)));self.wait(.5)
