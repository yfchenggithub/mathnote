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


class C080Animation(Scene):
    def construct(self):
        xy=lambda p:np.array([1.05*p[0],1.05*p[1]+.3,0])
        title=cn('曲线在变，焦点不动',32).move_to([0,6.9,0]);self.add(title)
        foci=VGroup(*[VGroup(Dot(xy((s*c,0)),color=ORANGE,radius=.075),eq('F_'+str(j),25,ORANGE).move_to(xy((s*c,0))+DOWN*.32)) for j,s in enumerate((-1,1),1)])
        self.add(foci)
        for kind,lo,hi in [('ellipse',.7,2.),('hyperbola',.7,1.7)]:
            t=ValueTracker(lo)
            caption=cn('共焦椭圆族' if kind=='ellipse' else '共焦双曲线族',29).move_to([0,5.6,0])
            def plotting(q,color=BLUE,opacity=1):
                if kind=='ellipse':return ParametricFunction(lambda u:xy(curve(kind,q,u)),t_range=[0,TAU],color=color,stroke_opacity=opacity)
                return VGroup(*[ParametricFunction(lambda u,s=s:xy(curve(kind,q,u,s)),t_range=[-1.1,1.1],color=color,stroke_opacity=opacity) for s in (-1,1)])
            ghosts=VGroup(*[plotting(q,AXIS,.35) for q in np.linspace(lo,hi,4)])
            moving=always_redraw(lambda:plotting(t.get_value()))
            formula=eq(r'A^2-B^2=c^2' if kind=='ellipse' else r'A^2+B^2=c^2',39,GREEN).move_to([0,-4.6,0])
            note=cn('两个焦点固定在 (±c, 0)',25,MUTED).move_to([0,-6.1,0])
            read=number('c',lambda:c,[0,-3.3,0],ORANGE)
            self.add(ghosts,moving,caption,formula,note,read)
            self.wait(.6);self.play(t.animate.set_value(hi),run_time=3)
            self.wait(.8);self.play(t.animate.set_value(lo),run_time=3);self.wait(.4)
            self.play(*[FadeOut(m) for m in (ghosts,moving,caption,formula,note,read)],run_time=.2)
