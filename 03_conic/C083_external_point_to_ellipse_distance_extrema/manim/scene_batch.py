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


class C083Animation(Scene):
    def construct(self):
        t=ValueTracker(tmin);xy=lambda p:np.array([.85*p[0]-.4,.85*p[1]+.5,0])
        title=cn('外点到椭圆，最近与最远在哪里？',27).move_to([0,6.9,0])
        caption=cn('固定 M，比较椭圆上所有点的距离',25).move_to([0,5.6,0])
        ellipse=ParametricFunction(lambda u:xy(point(u)),t_range=[0,TAU],color=BLUE)
        moving=always_redraw(lambda:VGroup(Line(xy(M),xy(point(t.get_value())),color=ORANGE,stroke_width=3),
            Dot(xy(point(t.get_value())),color=ORANGE,radius=.075)))
        marks=VGroup(Dot(xy(M),color=INK,radius=.07),eq('M',27,INK).move_to(xy(M)+UP*.3))
        for z,label,col in [(tmin,'P_{min}',GREEN),(tmax,'P_{max}',PURPLE)]:
            P=point(z);dx,dy=-a*np.sin(z),b*np.cos(z);u=np.array([dx,dy,0]);u/=np.linalg.norm(u)
            marks.add(DashedLine(xy(M),xy(P),color=col,stroke_opacity=.45),
                Line(xy(P)-u*.6,xy(P)+u*.6,color=col,stroke_width=2),Dot(xy(P),color=col,radius=.07),
                eq(label,25,col).move_to(xy(P)+DOWN*.32))
        self.add(title,caption,ellipse,marks,moving,number('MP',lambda:distance(t.get_value()),[0,-3.3,0],ORANGE),
            eq(r'F(\theta)=(a\cos\theta-x_0)^2+(b\sin\theta-y_0)^2',27,GREEN).move_to([0,-4.7,0]),
            eq(r'F^\prime(\theta)=0:\ \ MP\perp\text{tangent}',29,MUTED).move_to([0,-6.2,0]))
        self.wait(1.2);self.play(t.animate.set_value(tmax),run_time=4)
        swap(self,(caption,cn('比较全部驻点，才能确定全局最值',25,GREEN).move_to(caption)))
        self.wait(1.4);self.play(t.animate.set_value(tmin+TAU),run_time=4)
        swap(self,(caption,cn('固定 M，比较椭圆上所有点的距离',25).move_to(caption)));self.wait(.8)
