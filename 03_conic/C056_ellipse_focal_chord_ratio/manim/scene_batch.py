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


class C056Animation(Scene):
    def construct(self):
        t=ValueTracker(.35); xy=lambda p:np.array([1.05*p[0],1.05*p[1]+.7,0])
        title=cn('焦点怎样分割这条弦？',31).move_to([0,6.9,0])
        caption=cn('A、B 分别位于焦点两侧').move_to([0,5.6,0])
        curve=ParametricFunction(lambda u:xy((a*np.cos(u),b*np.sin(u))),t_range=[0,TAU],color=BLUE)
        def geometry():
            A,B=endpoints(t.get_value()); f=xy((c,0))
            return VGroup(Line(f,xy(A),color=ORANGE,stroke_width=3),Line(f,xy(B),color=PURPLE,stroke_width=3),Dot(xy(A),color=GREEN,radius=.07),Dot(xy(B),color=GREEN,radius=.07),eq('A',25,ORANGE).move_to(xy(A)+UP*.28),eq('B',25,PURPLE).move_to(xy(B)+DOWN*.28))
        moving=always_redraw(geometry)
        focus=VGroup(Dot(xy((c,0)),color=INK,radius=.055),eq('F',25,MUTED).move_to(xy((c,0))+LEFT*.2+DOWN*.25))
        read=number('AF/BF',lambda:ratio(t.get_value()),[0,-3.5,0],GREEN)
        result=eq(r'\frac{AF}{BF}=\frac{1-e\cos\theta}{1+e\cos\theta}',35,GREEN).move_to([0,-5,0])
        note=cn('通径位置两段等长，比例为 1',25,MUTED).move_to([0,-6.5,0])
        self.add(title,caption,axes(xy,(-3.6,3.6),(-2.7,2.7)),curve,moving,focus,read,result,note)
        self.wait(.8)
        self.play(t.animate.set_value(PI/2),run_time=3)
        swap(self,(caption,cn('此时 AF=BF，焦点平分通径',26,GREEN).move_to(caption)))
        self.wait(1)
        swap(self,(caption,cn('继续旋转，长短关系交换').move_to(caption)))
        self.play(t.animate.set_value(PI-.35),run_time=3)
        self.play(t.animate.set_value(.35),run_time=3)
        swap(self,(caption,cn('A、B 分别位于焦点两侧').move_to(caption)))
        self.wait(.5)
