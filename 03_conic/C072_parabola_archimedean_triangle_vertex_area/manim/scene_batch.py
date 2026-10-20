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


class C072Animation(Scene):
    def construct(self):
        t=ValueTracker(.45);d=ValueTracker(.8)
        xy=lambda p:np.array([1.5*p[0],1.5*p[1]-.5,0])
        title=cn('两条切线，围出怎样的三角形？',28).move_to([0,6.9,0])
        caption=cn('切点弦中点 M 与交点 P 竖直对齐',24).move_to([0,5.6,0])
        curve=ParametricFunction(lambda u:xy((u,u*u/(2*p))),t_range=[-2,2],color=BLUE)
        def geometry():
            A,B,P,M=state(t.get_value(),d.get_value())
            return VGroup(Polygon(xy(A),xy(B),xy(P),stroke_opacity=0,fill_color=ORANGE,fill_opacity=.1),
                Line(xy(P),xy(A),color=ORANGE),Line(xy(P),xy(B),color=ORANGE),Line(xy(A),xy(B),color=PURPLE),
                DashedLine(xy(P),xy(M),color=GREEN),
                *[VGroup(Dot(xy(Q),color=col,radius=.065),eq(name,24,col).move_to(xy(Q)+offset)) for Q,name,col,offset in [(A,'A',BLUE,LEFT*.25),(B,'B',BLUE,RIGHT*.25),(P,'P',ORANGE,DOWN*.3),(M,'M',GREEN,UP*.3)]])
        moving=always_redraw(geometry)
        self.add(title,caption,curve,moving,number('S',lambda:area(t.get_value(),d.get_value()),[0,-3.5,0],ORANGE),
            eq(r'S_{\triangle PAB}=\frac{|x_1-x_2|^3}{8p}',35,GREEN).move_to([0,-4.9,0]),
            eq(r'x_P=x_M=\frac{x_1+x_2}{2}',31,MUTED).move_to([0,-6.3,0]))
        self.wait(.8);self.play(d.animate.set_value(1.3),run_time=3)
        self.play(t.animate.set_value(-.45),run_time=3)
        self.wait(1);self.play(t.animate.set_value(.45),d.animate.set_value(.8),run_time=3);self.wait(.5)
