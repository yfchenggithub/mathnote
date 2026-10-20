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


class C081Animation(Scene):
    def construct(self):
        s=ValueTracker(1);xy=lambda p:np.array([1.05*p[0],1.05*p[1]+.2,0])
        title=cn('竖直拉伸，把椭圆变成圆',30).move_to([0,6.9,0])
        caption=cn('横坐标保留，所有纵坐标乘以 s',25).move_to([0,5.6,0])
        original=ParametricFunction(lambda u:xy(point(u,1)),t_range=[0,TAU],color=AXIS,stroke_opacity=.5)
        def geometry():
            q=s.get_value();tri=[transform(P,q) for P in triangle]
            return VGroup(ParametricFunction(lambda u:xy(point(u,q)),t_range=[0,TAU],color=BLUE),
                Polygon(*[xy(P) for P in tri],color=ORANGE,fill_color=ORANGE,fill_opacity=.12),
                Line(xy(transform((-2.,-1.),q)),xy(transform((2.,1.),q)),color=PURPLE))
        moving=always_redraw(geometry)
        self.add(title,caption,original,moving,number('s',s.get_value,[0,-3.5,0],GREEN),
            eq(r'S_s=sS,\quad k_s=sk',35,GREEN).move_to([0,-4.9,0]),
            eq(r's=a/b\ \Rightarrow\ x_s^2+y_s^2=a^2',31,MUTED).move_to([0,-6.3,0]))
        self.wait(.8);self.play(s.animate.set_value(a/b),run_time=4)
        swap(self,(caption,cn('此时 s=a/b，蓝色曲线成为圆',25,GREEN).move_to(caption)))
        self.wait(1.4)
        swap(self,(caption,cn('恢复原来的椭圆，拉伸倍数逐渐减小',24).move_to(caption)))
        self.play(s.animate.set_value(1),run_time=4)
        swap(self,(caption,cn('横坐标保留，所有纵坐标乘以 s',25).move_to(caption)));self.wait(.5)
