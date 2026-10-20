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


class C078Animation(Scene):
    def construct(self):
        t=ValueTracker(.35);xy=lambda p:np.array([1.05*p[0],1.05*p[1]+.3,0])
        title=cn('参数角，来自辅助圆',32).move_to([0,6.9,0])
        caption=cn('横坐标不变，纵坐标按 b/a 压缩',25).move_to([0,5.6,0])
        circle=Circle(radius=1.05*a,color=PURPLE,stroke_opacity=.45).move_to(xy((0,0)))
        ellipse=ParametricFunction(lambda u:xy(state(u)[1]),t_range=[0,TAU],color=BLUE)
        def geometry():
            Q,P=state(t.get_value())
            return VGroup(Line(xy((0,0)),xy(Q),color=PURPLE,stroke_opacity=.6),DashedLine(xy(Q),xy(P),color=ORANGE),
                Dot(xy(Q),color=PURPLE,radius=.07),Dot(xy(P),color=GREEN,radius=.07),
                eq('Q',25,PURPLE).move_to(xy(Q)+UP*.3),eq('P',25,GREEN).move_to(xy(P)+DOWN*.3))
        self.add(title,caption,axes(xy,(-3.5,3.5),(-3.4,3.4)),circle,ellipse,always_redraw(geometry),
            eq(r'x=a\cos\theta,\quad y=b\sin\theta',37,GREEN).move_to([0,-4.5,0]),
            cn('θ 是辅助圆的圆心角',25,MUTED).move_to([0,-6.1,0]))
        self.wait(.8);self.play(t.animate.set_value(TAU+.35),run_time=9);self.wait(1)
