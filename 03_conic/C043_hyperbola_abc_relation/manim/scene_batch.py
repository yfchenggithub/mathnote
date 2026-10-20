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


class C043Animation(Scene):
    def construct(self):
        b=ValueTracker(1.6)
        xy=lambda p:np.array([2.1*p[0]-2.6,2.1*p[1]-1.4,0])
        title=cn('双曲线中，c 是斜边',31).move_to([0,6.9,0])
        caption=cn('把三个参数放进直角三角形').move_to([0,5.5,0])
        def geometry():
            a,bb,c=parameters(b.get_value()); pts=triangle(bb)
            sides=VGroup(Line(xy(pts[0]),xy(pts[1]),color=ORANGE,stroke_width=3),Line(xy(pts[1]),xy(pts[2]),color=BLUE,stroke_width=3),Line(xy(pts[2]),xy(pts[0]),color=PURPLE,stroke_width=3))
            if KIND=='ellipse':
                # O, right focus, upper vertex: vertical b is O to upper vertex.
                labels=VGroup(eq('c',29,ORANGE).move_to(xy(((pts[0][0]+pts[1][0])/2,0))+DOWN*.3),eq('a',29,BLUE).move_to(xy(((pts[1][0]+pts[2][0])/2,bb/2))+RIGHT*.3),eq('b',29,PURPLE).move_to(xy((0,bb/2))+LEFT*.3))
            else: labels=VGroup(eq('a',29,ORANGE).move_to(xy((a/2,0))+DOWN*.3),eq('b',29,BLUE).move_to(xy((a,bb/2))+RIGHT*.3),eq('c',29,PURPLE).move_to(xy((a/2,bb/2))+LEFT*.3))
            return VGroup(sides,labels)
        figure=always_redraw(geometry)
        formula=eq(r'c^2=a^2+b^2',43,GREEN).move_to([0,-3.4,0])
        read=number('b',lambda:b.get_value(),[-1.7,-4.9,0],BLUE)
        readc=number('c',lambda:parameters(b.get_value())[2],[1.7,-4.9,0],PURPLE)
        note=cn('实半轴 a、虚半轴 b、半焦距 c',25,MUTED).move_to([0,-6.3,0])
        self.add(title,caption,figure,formula,read,readc,note)
        self.wait(.8)
        self.play(b.animate.set_value(.9),run_time=2.5)
        self.play(b.animate.set_value(2.3),run_time=3)
        self.play(b.animate.set_value(1.6),run_time=2.5)
        self.wait(1)
