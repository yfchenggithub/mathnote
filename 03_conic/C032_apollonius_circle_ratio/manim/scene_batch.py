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


class C032Animation(Scene):
    def construct(self):
        t=ValueTracker(0); xy=lambda p:np.array([1.45*(p[0]-1),1.45*p[1]+.7,0])
        title=cn('距离比不变，描出什么轨迹？',29).move_to([0,6.9,0])
        caption=cn('到 A、B 的距离比始终为 2').move_to([0,5.6,0])
        trajectory=always_redraw(lambda:ParametricFunction(lambda u:xy(point(u)),t_range=[0,max(.001,t.get_value())],color=BLUE,stroke_width=3))
        legs=always_redraw(lambda:VGroup(Line(xy((-1,0)),xy(point(t.get_value())),color=ORANGE,stroke_width=2.5),Line(xy((1,0)),xy(point(t.get_value())),color=PURPLE,stroke_width=2.5),Dot(xy(point(t.get_value())),color=GREEN,radius=.08)))
        fixed=VGroup(Dot(xy((-1,0)),color=INK,radius=.06),Dot(xy((1,0)),color=INK,radius=.06),eq('A',26,MUTED).move_to(xy((-1,0))+DOWN*.3),eq('B',26,MUTED).move_to(xy((1,0))+DOWN*.3))
        read=number(r'PA/PB',lambda:ratio(t.get_value()),[0,-3.5,0],GREEN)
        result=eq(r'(x-5/3)^2+y^2=(4/3)^2',33,GREEN).move_to([0,-5,0])
        note=eq(r'\lambda>0,\quad\lambda\ne1',30,MUTED).move_to([0,-6.5,0])
        self.add(title,caption,Line(xy((-1.25,0)),xy((3.25,0)),color=AXIS,stroke_width=1.3),trajectory,legs,fixed,read,result,note)
        self.wait(.8)
        self.play(t.animate.set_value(TAU),run_time=7,rate_func=linear)
        swap(self,(caption,cn('动点的轨迹正是阿波罗尼斯圆',26,GREEN).move_to(caption)))
        self.wait(1.5)
        self.play(t.animate.set_value(0),run_time=2,rate_func=linear)
        swap(self,(caption,cn('到 A、B 的距离比始终为 2').move_to(caption)))
        self.wait(.5)
