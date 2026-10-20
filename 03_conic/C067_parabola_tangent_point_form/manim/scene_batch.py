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


class C067Animation(Scene):
    def construct(self):
        lo,hi=(-1,1) if KIND=='hyperbola' else (-1.8,1.8)
        t=ValueTracker(lo);xy=lambda p:np.array([1.05*p[0]-1.1,1.05*p[1]+.7,0])
        title=cn('切点移动，切线始终贴合',30).move_to([0,6.9,0])
        caption=cn('统一点式也包含顶点处的竖直切线',24).move_to([0,5.6,0])
        curve=ParametricFunction(lambda u:xy(point(u)),t_range=[-1.3,1.3] if KIND=='hyperbola' else [-2.1,2.1],color=BLUE)
        moving=always_redraw(lambda:VGroup(Line(*[xy(p) for p in segment(t.get_value())],color=ORANGE,stroke_width=3),Dot(xy(point(t.get_value())),color=GREEN,radius=.075)))
        formula=eq(r'y_0y=p(x+x_0)',39,GREEN).move_to([0,-4.4,0])
        note=cn('P 必须在曲线上，才能用作切点',25,MUTED).move_to([0,-6,0])
        self.add(title,caption,curve,moving,formula,note)
        self.wait(.8);self.play(t.animate.set_value(0),run_time=2.5);self.wait(1)
        self.play(t.animate.set_value(hi),run_time=2.5)
        self.play(t.animate.set_value(lo),run_time=3.5);self.wait(.5)
