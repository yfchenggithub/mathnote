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


class C057Animation(Scene):
    def construct(self):
        t=ValueTracker(1.15); xy=lambda p:np.array([1.1*p[0],1.1*p[1]+.7,0])
        title=cn('同支求和，异支求差',31).move_to([0,6.9,0])
        caption=cn('先看同一支上的两个交点').move_to([0,5.6,0])
        curve=VGroup(*[ParametricFunction(lambda u,sign=sign:xy((sign*a*np.cosh(u),b*np.sinh(u))),t_range=[-1.25,1.25],color=BLUE) for sign in (-1,1)])
        moving=always_redraw(lambda:VGroup(Line(*[xy(p) for p in endpoints(t.get_value())],color=ORANGE,stroke_width=3),*[Dot(xy(p),color=GREEN,radius=.07) for p in endpoints(t.get_value())]))
        focus=VGroup(Dot(xy((c,0)),radius=.055,color=INK),eq('F',25,MUTED).move_to(xy((c,0))+DOWN*.3))
        read=number('R',lambda:reciprocal(t.get_value()),[0,-3.6,0],GREEN)
        formula=eq(r'\frac1{AF}+\frac1{BF}=\frac{2a}{b^2}',36,GREEN).move_to([0,-5,0])
        note=cn('两个情形分开展示，避开无穷远交点',23,MUTED).move_to([0,-6.5,0])
        self.add(title,caption,axes(xy,(-3.3,3.3),(-2.7,2.7)),curve,moving,focus,read,formula,note)
        self.wait(.8); self.play(t.animate.set_value(PI-1.15),run_time=3)
        self.play(FadeOut(moving),FadeOut(read),run_time=.3)
        t.set_value(-.2)
        swap(self,(caption,cn('再看两个不同分支上的交点').move_to(caption)),(formula,eq(r'\left|\frac1{AF}-\frac1{BF}\right|=\frac{2a}{b^2}',35,GREEN).move_to(formula)))
        self.play(FadeIn(moving),FadeIn(read),run_time=.3)
        self.play(t.animate.set_value(.2),run_time=3); self.wait(1)
        self.play(FadeOut(moving),FadeOut(read),run_time=.3); t.set_value(1.15)
        swap(self,(caption,cn('先看同一支上的两个交点').move_to(caption)),(formula,eq(r'\frac1{AF}+\frac1{BF}=\frac{2a}{b^2}',36,GREEN).move_to(formula)))
        self.play(FadeIn(moving),FadeIn(read),run_time=.3); self.wait(.5)
