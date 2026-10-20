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


class C029Animation(Scene):
    def construct(self):
        t=ValueTracker(.6); xy=lambda p:np.array([1.05*p[0],1.05*p[1]+.8,0])
        title=cn('横坐标改变，两条焦半径怎样变？',28).move_to([0,6.9,0])
        caption=cn('左焦半径增大，右焦半径相应减小',25).move_to([0,5.6,0])
        curve=ParametricFunction(lambda u:xy(point(u)),t_range=[0,TAU],color=BLUE)
        legs=always_redraw(lambda:VGroup(Line(xy((-c,0)),xy(point(t.get_value())),color=ORANGE,stroke_width=3),Line(xy((c,0)),xy(point(t.get_value())),color=PURPLE,stroke_width=3)))
        dots=always_redraw(lambda:Dot(xy(point(t.get_value())),color=GREEN,radius=.08))
        focuses=VGroup(*[VGroup(Dot(xy((f,0)),color=INK,radius=.055),eq('F_'+str(i),25,MUTED).move_to(xy((f,0))+DOWN*.3)) for i,f in enumerate((-c,c),1)])
        r1=number('r_1',lambda:radius(t.get_value(),1),[-2,-3.4,0],ORANGE)
        r2=number('r_2',lambda:radius(t.get_value(),2),[2,-3.4,0],PURPLE)
        formula=eq(r'r_1=a+ex\qquad r_2=a-ex',32,GREEN).move_to([0,-4.9,0])
        total=number(r'r_1+r_2',lambda:radius(t.get_value(),1)+radius(t.get_value(),2),[0,-6,0],GREEN)
        note=cn('F₁ 是左焦点，F₂ 是右焦点',24,MUTED).move_to([0,-7.1,0])
        self.add(title,caption,axes(xy,(-3.6,3.6),(-2.8,2.8)),curve,legs,dots,focuses,r1,r2,formula,total,note)
        self.wait(.8)
        swap(self,(caption,cn('绕椭圆一周，观察此消彼长').move_to(caption)))
        self.play(t.animate.set_value(TAU+.6),run_time=9,rate_func=linear)
        swap(self,(caption,cn('两条焦半径之和始终为 2a',27,GREEN).move_to(caption)))
        self.wait(1.5)
        swap(self,(caption,cn('左焦半径增大，右焦半径相应减小',25).move_to(caption)))
        self.wait(.5)
