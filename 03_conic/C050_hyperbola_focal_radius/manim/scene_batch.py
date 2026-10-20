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


class C050Animation(Scene):
    def construct(self):
        t=ValueTracker(.5 if KIND=='ellipse' else .35)
        xy=lambda p:np.array([1.05*p[0],1.05*p[1]+.7,0])
        s=lambda:state(t.get_value())
        title=cn('双曲线焦半径，注意绝对值',31).move_to([0,6.9,0])
        caption=cn('移动曲线上的点 P').move_to([0,5.6,0])
        if KIND=='ellipse': curve=ParametricFunction(lambda u:xy(point(u)),t_range=[0,TAU],color=BLUE)
        else: curve=VGroup(*[ParametricFunction(lambda u,sign=sign:xy((sign*a*np.cosh(u),b*np.sinh(u))),t_range=[-1.35,1.35],color=BLUE) for sign in (-1,1)])
        triangle=always_redraw(lambda:Polygon(xy((-c,0)),xy(point(t.get_value())),xy((c,0)),color=ORANGE,stroke_width=2.5,fill_color=ORANGE,fill_opacity=.07))
        P=always_redraw(lambda:VGroup(Dot(xy(point(t.get_value())),color=GREEN,radius=.075),eq('P',26,GREEN).move_to(xy(point(t.get_value()))+UP*.3)))
        fixed=VGroup(*[VGroup(Dot(xy((f,0)),radius=.055,color=INK),eq('F_'+str(i),24,MUTED).move_to(xy((f,0))+DOWN*.3)) for i,f in enumerate((-c,c),1)])
        if KIND=='radius':
            readings=VGroup(number('r_1',lambda:s()['r1'],[-2,-3.5,0],ORANGE),number('r_2',lambda:s()['r2'],[2,-3.5,0],PURPLE))
            formula=eq(r'r_1=|a+ex|\quad r_2=|a-ex|',32,GREEN).move_to([0,-5,0])
            note=cn('本图取右支，实际距离均为正数',25,MUTED).move_to([0,-6.5,0])
        else:
            readings=VGroup(number('S',lambda:s()['area'],[-1.8,-3.5,0],ORANGE),number(r'\theta',lambda:s()['angle']*180/PI,[1.8,-3.5,0],PURPLE))
            formula=eq(r'S=b^2\cot\frac{\theta}{2}',38,GREEN).move_to([0,-5,0])
            note=eq(r'\theta=\angle F_1PF_2,\quad S=c|y_P|',28,MUTED).move_to([0,-6.5,0])
        self.add(title,caption,axes(xy,(-3.4,3.4),(-2.6,2.6)),curve,triangle,P,fixed,readings,formula,note)
        self.wait(.8)
        target=PI-.5 if KIND=='ellipse' else 1.25
        self.play(t.animate.set_value(target),run_time=4)
        swap(self,(caption,cn('焦点位置固定，长度与角度同步变化',25,GREEN).move_to(caption)))
        self.wait(1)
        self.play(t.animate.set_value(.5 if KIND=='ellipse' else .35),run_time=4)
        swap(self,(caption,cn('移动曲线上的点 P').move_to(caption)))
        self.wait(.5)
