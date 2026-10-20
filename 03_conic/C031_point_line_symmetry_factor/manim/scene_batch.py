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


class C031Animation(Scene):
    def construct(self):
        t=ValueTracker(1.3); xy=lambda p:np.array([1.15*p[0],1.15*p[1]+.7,0])
        title=cn('关于直线对称，先找垂足',30).move_to([0,6.9,0])
        caption=cn('中点 H 始终落在对称轴上').move_to([0,5.6,0])
        line=Line(xy((-3,-1.5)),xy((3,1.5)),color=BLUE,stroke_width=3)
        segment=always_redraw(lambda:Line(xy(point(t.get_value())),xy(reflected(t.get_value())),color=ORANGE,stroke_width=3))
        def marks():
            p,q,h=point(t.get_value()),reflected(t.get_value()),foot(t.get_value())
            return VGroup(Dot(xy(p),radius=.075,color=GREEN),Dot(xy(q),radius=.075,color=PURPLE),Dot(xy(h),radius=.055,color=INK),eq('P',26,GREEN).move_to(xy(p)+UP*.3),eq("P'",26,PURPLE).move_to(xy(q)+DOWN*.3),eq('H',24,MUTED).move_to(xy(h)+RIGHT*.3))
        labels=always_redraw(marks)
        formula=eq(r'P^{\prime}=P-2\frac{Ax_0+By_0+C}{A^2+B^2}(A,B)',29,GREEN).move_to([0,-4.4,0])
        reason=eq(r'PH=HP^{\prime}\qquad PP^{\prime}\perp l',31,MUTED).move_to([0,-5.8,0])
        note=eq(r'l:x-2y=0',29,BLUE).move_to([0,-7,0])
        self.add(title,caption,axes(xy,(-3.1,3.1),(-2.7,2.7)),line,segment,labels,formula,reason,note)
        self.wait(.8)
        self.play(t.animate.set_value(.9),run_time=2)
        self.play(t.animate.set_value(2.1),run_time=4)
        swap(self,(caption,cn('两侧距离相等，连线始终垂直',26,GREEN).move_to(caption)))
        self.wait(1)
        self.play(t.animate.set_value(1.3),run_time=3)
        swap(self,(caption,cn('中点 H 始终落在对称轴上').move_to(caption)))
        self.wait(.5)
