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


class C027Animation(Scene):
    def construct(self):
        t=ValueTracker(.25); xy=lambda p:np.array([1.05*p[0],1.05*p[1]+.7,0])
        title=cn('焦点弦旋转，何时最短？',31).move_to([0,6.9,0])
        caption=cn('直线始终经过右焦点 F').move_to([0,5.6,0])
        curve=ParametricFunction(lambda s:xy((a*np.cos(s),b*np.sin(s))),t_range=[0,TAU],color=BLUE)
        chord=always_redraw(lambda:Line(*[xy(p) for p in endpoints(t.get_value())],color=ORANGE,stroke_width=3.5))
        marks=always_redraw(lambda:VGroup(*[Dot(xy(p),radius=.07,color=GREEN) for p in endpoints(t.get_value())]))
        focus=VGroup(Dot(xy((c,0)),color=INK,radius=.055),eq('F',26,MUTED).move_to(xy((c,0))+DOWN*.3))
        read=number('L',lambda:length(t.get_value()),[0,-3.5,0],ORANGE)
        formula=eq(r'L=\frac{2ab^2}{a^2\sin^2\theta+b^2\cos^2\theta}',32,GREEN).move_to([0,-5,0])
        note=cn('垂直于长轴时为通径',25,MUTED).move_to([0,-6.5,0])
        self.add(title,caption,axes(xy,(-3.6,3.6),(-2.8,2.8)),curve,chord,marks,focus,read,formula,note)
        self.wait(.8)
        self.play(t.animate.set_value(PI/2),run_time=3)
        swap(self,(caption,cn('通径最短：L = 2b²/a',28,GREEN).move_to(caption)))
        self.wait(1.4)
        swap(self,(caption,cn('继续旋转，弦长再次增大').move_to(caption)))
        self.play(t.animate.set_value(PI),run_time=3)
        swap(self,(caption,cn('沿长轴时，焦点弦最长').move_to(caption)))
        self.wait(1)
        self.play(t.animate.set_value(.25),run_time=3)
        swap(self,(caption,cn('直线始终经过右焦点 F').move_to(caption)))
        self.wait(.5)
