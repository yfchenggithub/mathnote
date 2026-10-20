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


class C030Animation(Scene):
    def construct(self):
        t=ValueTracker(.4); xy=lambda p:np.array([1.05*p[0],1.05*p[1]+.8,0])
        title=cn('三角形在变，周长不变',31).move_to([0,6.9,0])
        caption=cn('弦 PQ 绕左焦点 F₁ 转动').move_to([0,5.6,0])
        curve=ParametricFunction(lambda u:xy((a*np.cos(u),b*np.sin(u))),t_range=[0,TAU],color=BLUE)
        triangle=always_redraw(lambda:Polygon(xy(endpoints(t.get_value())[0]),xy((c,0)),xy(endpoints(t.get_value())[1]),color=ORANGE,stroke_width=3,fill_color=ORANGE,fill_opacity=.07))
        marks=VGroup(*[VGroup(Dot(xy((f,0)),radius=.055,color=INK),eq('F_'+str(i),25,MUTED).move_to(xy((f,0))+DOWN*.3)) for i,f in enumerate((-c,c),1)])
        points=always_redraw(lambda:VGroup(*[Dot(xy(p),radius=.075,color=GREEN) for p in endpoints(t.get_value())]))
        read=number('C',lambda:perimeter(t.get_value()),[0,-3.4,0],GREEN)
        formula=eq(r'PF_2+QF_2+PQ=4a',34,GREEN).move_to([0,-4.9,0])
        reason=eq(r'PQ=PF_1+QF_1',30,MUTED).move_to([0,-6.2,0])
        self.add(title,caption,axes(xy,(-3.6,3.6),(-2.8,2.8)),curve,triangle,marks,points,read,formula,reason)
        self.wait(.8)
        self.play(t.animate.set_value(PI/2),run_time=3)
        swap(self,(caption,cn('两组焦半径，各自相加为 2a',26,GREEN).move_to(caption)))
        self.wait(1)
        self.play(t.animate.set_value(PI-.4),run_time=3)
        self.play(t.animate.set_value(.4),run_time=3)
        swap(self,(caption,cn('弦 PQ 绕左焦点 F₁ 转动').move_to(caption)))
        self.wait(.5)
