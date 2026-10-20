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


class C026Animation(Scene):
    def construct(self):
        angle,q=ValueTracker(0),ValueTracker(0)
        project=lambda p:np.array([.9*(p[0]+.38*p[2]),.9*(p[1]+.24*p[2])+.7,0])
        title=cn('绕 y 轴旋转，形成椭球',30).move_to([0,6.9,0])
        caption=cn('先看椭圆绕固定轴转动').move_to([0,5.5,0])
        lines=VGroup(*[Line(project(tuple(-3.5 if j==i else 0 for j in range(3))),project(tuple(3.5 if j==i else 0 for j in range(3))),color=GREEN if (i==0 and ROTATION_AXIS=='x') or (i==1 and ROTATION_AXIS=='y') else AXIS,stroke_width=2) for i in range(3)])
        wire=always_redraw(lambda:VGroup(*[ParametricFunction(lambda t,phi=phi:project(profile(t,phi)),t_range=[0,TAU],color=BLUE,stroke_width=1.2,stroke_opacity=.55) for phi in np.linspace(0,TAU,13) if phi<angle.get_value()]))
        moving=always_redraw(lambda:ParametricFunction(lambda t:project(profile(t,angle.get_value())),t_range=[0,TAU],color=ORANGE,stroke_width=3))
        section=always_redraw(lambda:ParametricFunction(lambda t:project(disk(q.get_value(),t)),t_range=[0,TAU],color=PURPLE,stroke_width=2.5,fill_color=PURPLE,fill_opacity=.1))
        formula=eq(r'V_y=\frac43\pi a^2b',40,GREEN).move_to([0,-4,0])
        read=number(r'S_{\rm disk}/\pi',lambda:section_area(q.get_value())/PI,[0,-5.25,0],PURPLE)
        detail=eq(r'V_y=\int_{-b}^{b}\pi a^2(1-y^2/b^2)\,dy',27,MUTED).move_to([0,-6.55,0])
        self.add(title,caption,lines,wire,moving,formula,detail)
        self.wait(.7)
        self.play(angle.animate.set_value(TAU),run_time=3,rate_func=linear)
        self.wait(.8)
        swap(self,(caption,cn('圆盘截面沿旋转轴累加').move_to(caption)))
        self.play(FadeIn(section),FadeIn(read),run_time=.3)
        bound=A if ROTATION_AXIS=='x' else B
        self.play(q.animate.set_value(-bound*.9),run_time=1.4)
        self.play(q.animate.set_value(bound*.9),run_time=3)
        self.play(q.animate.set_value(0),run_time=1.4)
        self.play(FadeOut(section),FadeOut(read),run_time=.3)
        swap(self,(caption,cn('逆向还原，再看旋转过程').move_to(caption)))
        self.play(angle.animate.set_value(0),run_time=2,rate_func=linear)
        swap(self,(caption,cn('先看椭圆绕固定轴转动').move_to(caption)))
        self.wait(.5)
