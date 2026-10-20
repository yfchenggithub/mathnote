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


class C039Animation(Scene):
    def construct(self):
        t=ValueTracker(-1.8 if KIND=='parabola' else .3 if KIND=='ellipse' else -1.2)
        if KIND=='ellipse': scale,shift=.95,-.4
        elif KIND=='hyperbola': scale,shift=1.1,-.7
        else: scale,shift=1.45,-1
        xy=lambda p:np.array([scale*p[0]+shift,scale*p[1]+.7,0])
        title=cn('椭圆：焦准距离比小于 1',30).move_to([0,6.9,0])
        caption=cn('一条焦半径，一条准线垂距',26).move_to([0,5.55,0])
        if KIND=='ellipse': curve=ParametricFunction(lambda u:xy(point(u)),t_range=[0,TAU],color=BLUE)
        elif KIND=='hyperbola': curve=ParametricFunction(lambda u:xy(point(u)),t_range=[-1.4,1.4],color=BLUE)
        else: curve=ParametricFunction(lambda u:xy(point(u)),t_range=[-2,2],color=BLUE)
        direct=Line(xy((directrix,-2.6)),xy((directrix,2.6)),color=MUTED,stroke_width=2)
        fixed=VGroup(Dot(xy(focus),color=INK,radius=.055),eq('F',25,MUTED).move_to(xy(focus)+DOWN*.3),eq('l',25,MUTED).move_to(xy((directrix,2.6))+RIGHT*.2))
        def geometry():
            P,H=xy(point(t.get_value())),xy(foot(t.get_value()))
            return VGroup(Line(P,xy(focus),color=ORANGE,stroke_width=3),Line(P,H,color=PURPLE,stroke_width=3),Dot(P,color=GREEN,radius=.075),Dot(H,color=PURPLE,radius=.055),eq('P',25,GREEN).move_to(P+UP*.3),eq('H',24,PURPLE).move_to(H+LEFT*.25+DOWN*.25))
        moving=always_redraw(geometry)
        read=number(r'PF/PH',lambda:ratio(t.get_value()),[0,-3.65,0],GREEN)
        formula=eq(r'\frac{PF}{PH}=e\in(0,1)',36,GREEN).move_to([0,-5,0])
        standard=eq(r'\frac{x^2}{a^2}+\frac{y^2}{b^2}=1',29,MUTED).move_to([0,-6.5,0])
        self.add(title,caption,curve,direct,fixed,moving,read,formula,standard)
        self.wait(.8)
        if KIND=='ellipse': self.play(t.animate.set_value(TAU+.3),run_time=8,rate_func=linear)
        else:
            target=1.8 if KIND=='parabola' else 1.2
            self.play(t.animate.set_value(target),run_time=4)
            self.play(t.animate.set_value(-target),run_time=4)
        swap(self,(caption,cn('比值固定，动点沿圆锥曲线运动',25,GREEN).move_to(caption)))
        self.wait(1.2)
        swap(self,(caption,cn('一条焦半径，一条准线垂距',26).move_to(caption)))
        self.wait(.5)
