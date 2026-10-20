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


class C036Animation(Scene):
    def construct(self):
        t=ValueTracker(.3 if KIND=='ellipse' else -1.2)
        branch=[1]; xy=lambda p:np.array([1.1*p[0],1.1*p[1]+.7,0])
        title=cn('距离和不变，轨迹是椭圆',31).move_to([0,6.9,0])
        caption=cn('连接动点与两个固定焦点',26).move_to([0,5.6,0])
        if KIND=='ellipse':
            curve=ParametricFunction(lambda u:xy(point(u)),t_range=[0,TAU],color=BLUE)
        else:
            curve=VGroup(*[ParametricFunction(lambda u,s=s:xy(point(u,s)),t_range=[-1.4,1.4],color=BLUE) for s in (-1,1)])
        legs=always_redraw(lambda:VGroup(Line(xy((-c,0)),xy(point(t.get_value(),branch[0])),color=ORANGE,stroke_width=3),Line(xy((c,0)),xy(point(t.get_value(),branch[0])),color=PURPLE,stroke_width=3),Dot(xy(point(t.get_value(),branch[0])),radius=.08,color=GREEN)))
        fixed=VGroup(*[VGroup(Dot(xy((f,0)),radius=.055,color=INK),eq('F_'+str(i),25,MUTED).move_to(xy((f,0))+DOWN*.3)) for i,f in enumerate((-c,c),1)])
        r1=number('r_1',lambda:distances(t.get_value(),branch[0])[0],[-2,-3.4,0],ORANGE)
        r2=number('r_2',lambda:distances(t.get_value(),branch[0])[1],[2,-3.4,0],PURPLE)
        result=eq(r'r_1+r_2=2a',35,GREEN).move_to([0,-4.9,0])
        read=number(r'r_1+r_2',lambda:invariant(t.get_value(),branch[0]),[0,-6.2,0],GREEN)
        self.add(title,caption,axes(xy,(-3.3,3.3),(-2.7,2.7)),curve,legs,fixed,r1,r2,result,read)
        self.wait(.8)
        if KIND=='ellipse':
            self.play(t.animate.set_value(TAU+.3),run_time=8,rate_func=linear)
        else:
            self.play(t.animate.set_value(1.2),run_time=4)
            self.play(t.animate.set_value(-1.2),run_time=4)
        swap(self,(caption,cn('固定距离和大于两焦点间距',26,GREEN).move_to(caption)))
        self.wait(1.5)
        swap(self,(caption,cn('连接动点与两个固定焦点',26).move_to(caption)))
        self.wait(.5)
