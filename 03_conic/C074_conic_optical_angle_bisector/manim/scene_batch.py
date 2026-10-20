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


class C074Animation(Scene):
    def construct(self):
        xy=lambda p:np.array([1.1*p[0]-.15,1.1*p[1]+.3,0])
        self.add(cn('焦半径与角平分线',32).move_to([0,6.9,0]))
        for kind,lo,hi,label in [('ellipse',.6,2.5,'椭圆：法线平分两焦半径夹角'),('hyperbola',.4,1.1,'双曲线：切线平分两焦半径夹角'),('parabola',.5,1.8,'抛物线：向开口的射线与焦半径由法线平分')]:
            t=ValueTracker(lo)
            caption=cn(label,22 if kind=='parabola' else 25).move_to([0,5.6,0])
            if kind=='ellipse':curve=ParametricFunction(lambda u:xy((2.7*np.cos(u),1.8*np.sin(u))),t_range=[0,TAU],color=BLUE)
            elif kind=='hyperbola':curve=VGroup(*[ParametricFunction(lambda u,s=s:xy((s*1.5*np.cosh(u),np.sinh(u))),t_range=[-1.15,1.15],color=BLUE) for s in (-1,1)])
            else:curve=ParametricFunction(lambda u:xy((u*u/2,u)),t_range=[-2.1,2.1],color=BLUE)
            def geometry():
                P,F,G,u,v,w,n=state(kind,t.get_value());P0=xy(P);tangent=np.array([-n[1],n[0],0])
                bis=np.array([w[0],w[1],0])
                return VGroup(Line(xy(F),P0,color=PURPLE),Line(P0,xy(G),color=PURPLE),
                    Line(P0-tangent*1.65,P0+tangent*1.65,color=ORANGE),
                    DashedLine(P0,P0+bis*1.5,color=GREEN,stroke_width=3),
                    Dot(P0,color=GREEN,radius=.07),
                    Dot(xy(F),color=INK,radius=.055),eq('F' if kind=='parabola' else 'F_1',24,MUTED).move_to(xy(F)+DOWN*.3),
                    eq('H' if kind=='parabola' else 'F_2',24,MUTED).move_to(xy(G)+DOWN*.3),
                    Dot(xy(G),color=INK,radius=.055) if kind!='parabola' else Arrow(P0,xy(G),buff=0,color=PURPLE,stroke_width=2))
            moving=always_redraw(geometry)
            reads=VGroup(number(r'\alpha',lambda:angles(kind,t.get_value())[0],[-1.9,-3.7,0],GREEN),
                number(r'\beta',lambda:angles(kind,t.get_value())[1],[1.8,-3.7,0],GREEN))
            formula=eq(r'\alpha=\beta',41,GREEN).move_to([0,-5,0])
            note=cn('绿虚线为内角平分线，橙线为切线',23,MUTED).move_to([0,-6.3,0])
            self.add(curve,moving,reads,caption,formula,note);self.wait(.6)
            self.play(t.animate.set_value(hi),run_time=3);self.wait(.8)
            self.play(t.animate.set_value(lo),run_time=3);self.wait(.3)
            self.play(*[FadeOut(m) for m in (curve,moving,reads,caption,formula,note)],run_time=.2)
