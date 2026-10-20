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


class C069Animation(Scene):
    def construct(self):
        lo,hi=(.35,TAU+.35) if KIND in ('ellipse','monge') else (1.3,2.6) if KIND=='hyperbola' else (-.8,.8)
        t=ValueTracker(lo)
        scale=1.65 if KIND=='monge' else .95 if KIND=='ellipse' else 1.3
        xy=lambda p:np.array([scale*p[0]-(.85 if KIND=='parabola' else 0),scale*p[1]+.4,0])
        title=cn('双曲线的两条实切线与切点弦',30).move_to([0,6.9,0])
        caption=cn('P 引出两条切线，A、B 是切点',25).move_to([0,5.6,0])
        if KIND in ('ellipse','monge'):curveplot=ParametricFunction(lambda u:xy(curve(u)),t_range=[0,TAU],color=BLUE)
        elif KIND=='hyperbola':curveplot=VGroup(*[ParametricFunction(lambda u,s=s:xy(curve(u,s)),t_range=[-1.15,1.15],color=BLUE) for s in (-1,1)])
        else:curveplot=ParametricFunction(lambda u:xy(curve(u)),t_range=[-2.3,2.3],color=BLUE)
        def geometry():
            P,A,B=state(t.get_value())
            g=VGroup(Line(xy(P),xy(A),color=ORANGE,stroke_width=2.8),Line(xy(P),xy(B),color=ORANGE,stroke_width=2.8),Line(xy(A),xy(B),color=PURPLE,stroke_width=3),
                Dot(xy(P),color=ORANGE,radius=.07),Dot(xy(A),color=GREEN,radius=.065),Dot(xy(B),color=GREEN,radius=.065),
                eq('P',25,ORANGE).move_to(xy(P)+UP*.32),
                eq('A',24,GREEN).move_to(xy(A)+(xy(A)-xy(B))/np.linalg.norm(xy(A)-xy(B))*.25),
                eq('B',24,GREEN).move_to(xy(B)+(xy(B)-xy(A))/np.linalg.norm(xy(B)-xy(A))*.25))
            if KIND=='monge':
                u=(xy(A)-xy(P));u/=np.linalg.norm(u)
                v=(xy(B)-xy(P));v/=np.linalg.norm(v);o=xy(P)
                g.add(VMobject(color=GREEN,stroke_width=2).set_points_as_corners([o+u*.22,o+(u+v)*.22,o+v*.22]))
            return g
        moving=always_redraw(geometry)
        formula=eq(r'x_0x/a^2-y_0y/b^2=1',36,GREEN).move_to([0,-4.8,0])
        note=cn('紫色直线是切点弦，不是从 P 引出的切线',23,MUTED).move_to([0,-6.3,0])
        self.add(title,caption,curveplot)
        if KIND=='monge':
            locus=ParametricFunction(lambda u:xy((np.sqrt(a*a+b*b)*np.cos(u),np.sqrt(a*a+b*b)*np.sin(u))),t_range=[0,TAU],color=PURPLE,stroke_opacity=.4)
            self.add(locus,number(r'\angle APB',lambda:angle(t.get_value()),[0,-3.4,0],GREEN))
        self.add(moving,formula,note)
        self.wait(.8);self.play(t.animate.set_value(hi),run_time=7 if KIND in ('ellipse','monge') else 4)
        self.wait(1)
        if KIND not in ('ellipse','monge'):self.play(t.animate.set_value(lo),run_time=4)
        self.wait(.5)
