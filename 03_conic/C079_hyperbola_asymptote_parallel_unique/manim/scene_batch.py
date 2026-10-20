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


class C079Animation(Scene):
    def construct(self):
        m=ValueTracker(.8);xy=lambda p:np.array([1.15*p[0],1.15*p[1]+.6,0])
        title=cn('只有一个交点，也未必是切线',29).move_to([0,6.9,0])
        caption=cn('直线平行于渐近线，但不与它重合',24).move_to([0,5.6,0])
        curve=VGroup(*[ParametricFunction(lambda u,s=s:xy((s*a*np.cosh(u),b*np.sinh(u))),t_range=[-1,1],color=BLUE) for s in (-1,1)])
        asym=DashedLine(xy((-3.4,-3.4*k)),xy((3.4,3.4*k)),color=AXIS)
        def geometry():
            P=point(m.get_value())
            return VGroup(Line(xy((-3.4,-3.4*k+m.get_value())),xy((3.4,3.4*k+m.get_value())),color=ORANGE),
                Dot(xy(P),color=GREEN,radius=.085),eq('P',26,GREEN).move_to(xy(P)+DOWN*.3))
        moving=always_redraw(geometry)
        self.add(title,caption,curve,asym,moving,
            number('m',m.get_value,[0,-3.5,0],ORANGE),
            eq(r'y=\frac ba x+m,\quad m\ne0',35,GREEN).move_to([0,-4.9,0]),
            cn('代入后 x² 项抵消，剩下一次方程',24,MUTED).move_to([0,-6.3,0]))
        self.wait(.8);self.play(m.animate.set_value(1.6),run_time=3);self.wait(.8)
        self.play(FadeOut(moving),run_time=.2);m.set_value(-1.6);self.play(FadeIn(moving),run_time=.2)
        self.play(m.animate.set_value(-.8),run_time=3);self.wait(.8)
        self.play(FadeOut(moving),run_time=.2);m.set_value(.8);self.play(FadeIn(moving),run_time=.2);self.wait(.5)
