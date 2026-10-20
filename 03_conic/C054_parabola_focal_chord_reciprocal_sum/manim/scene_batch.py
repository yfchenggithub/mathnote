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


class C054Animation(Scene):
    def construct(self):
        t=ValueTracker(PI/3); xy=lambda q:np.array([1.05*q[0]-1.3,1.05*q[1]+.7,0])
        s=lambda:state(t.get_value())
        title=cn('两段焦半径，倒数和不变',30).move_to([0,6.9,0])
        caption=cn('焦点固定，弦 AB 绕它旋转').move_to([0,5.6,0])
        curve=ParametricFunction(lambda y:xy((y*y/(2*p),y)),t_range=[-2.8,2.8],color=BLUE)
        focus=VGroup(Dot(xy((p/2,0)),radius=.055,color=INK),eq('F',25,MUTED).move_to(xy((p/2,0))+LEFT*.25+DOWN*.2))
        def moving():
            A,B=endpoints(t.get_value()); f=xy((p/2,0))
            return VGroup(Line(f,xy(A),color=ORANGE,stroke_width=3),Line(f,xy(B),color=PURPLE,stroke_width=3),Dot(xy(A),color=GREEN,radius=.07),Dot(xy(B),color=GREEN,radius=.07),eq('A',25,ORANGE).move_to(xy(A)+RIGHT*.25+UP*.15),eq('B',25,PURPLE).move_to(xy(B)+RIGHT*.25+DOWN*.15))
        geometry=always_redraw(moving)
        readings=number(r'1/AF+1/BF',lambda:s()['reciprocal'],[0,-3.6,0],GREEN)
        result=eq(r'\frac1{AF}+\frac1{BF}=\frac2p',36,GREEN).move_to([0,-5.1,0])
        detail=eq(r'y^2=2px\quad(p>0,\ \sin\theta\ne0)',28,MUTED).move_to([0,-6.6,0])
        self.add(title,caption,axes(xy,(-.8,3.6),(-2.8,2.8)),curve,focus,geometry,readings,result,detail)
        self.wait(.8)
        self.play(t.animate.set_value(PI/2),run_time=2.5)
        swap(self,(caption,cn('两段长度相等，倒数和仍不变',26,GREEN).move_to(caption)))
        self.wait(1.1)
        self.play(t.animate.set_value(2*PI/3),run_time=2.5)
        self.play(t.animate.set_value(PI/3),run_time=3)
        swap(self,(caption,cn('焦点固定，弦 AB 绕它旋转').move_to(caption)))
        self.wait(.5)
