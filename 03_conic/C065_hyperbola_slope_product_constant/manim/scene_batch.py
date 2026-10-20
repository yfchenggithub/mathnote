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


class C065Animation(Scene):
    def construct(self):
        lo,hi=(.35,PI-.35) if KIND=='ellipse' else (.3,1.25)
        t=ValueTracker(lo);xy=lambda p:np.array([1.05*p[0],1.05*p[1]+.7,0])
        title=cn('连向两个端点，斜率积不变',30).move_to([0,6.9,0])
        caption=cn('这里连接的是两轴端点，不是焦点',24).move_to([0,5.6,0])
        if KIND=='ellipse':curve=ParametricFunction(lambda u:xy(point(u)),t_range=[0,TAU],color=BLUE)
        else:curve=VGroup(*[ParametricFunction(lambda u,s=s:xy((s*a*np.cosh(u),b*np.sinh(u))),t_range=[-1.3,1.3],color=BLUE) for s in (-1,1)])
        lines=always_redraw(lambda:VGroup(Line(xy((-a,0)),xy(point(t.get_value())),color=ORANGE,stroke_width=3),Line(xy((a,0)),xy(point(t.get_value())),color=PURPLE,stroke_width=3),Dot(xy(point(t.get_value())),color=GREEN,radius=.075)))
        endpoints=VGroup(*[VGroup(Dot(xy((x,0)),radius=.055,color=INK),eq('A_'+str(i),25,MUTED).move_to(xy((x,0))+DOWN*.3)) for i,x in enumerate((-a,a),1)])
        read=number(r'k_1k_2',lambda:product(t.get_value()),[0,-3.5,0],GREEN,4)
        formula=eq(r'k_{PA_1}k_{PA_2}=\frac{b^2}{a^2}',38,GREEN).move_to([0,-5,0])
        note=cn('切点式不是本图的两条连线',24,MUTED).move_to([0,-6.4,0])
        self.add(title,caption,axes(xy,(-3.4,3.4),(-2.6,2.6)),curve,lines,endpoints,read,formula,note)
        self.wait(.8);self.play(t.animate.set_value(hi),run_time=4)
        self.wait(1);self.play(t.animate.set_value(lo),run_time=4);self.wait(.5)
