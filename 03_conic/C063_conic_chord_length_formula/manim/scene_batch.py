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


class C063Animation(Scene):
    def construct(self):
        k=ValueTracker(.3);xy=lambda p:np.array([1.35*p[0],1.35*p[1]+.5,0])
        title=cn('斜着的弦，怎样由投影求长度？',28).move_to([0,6.9,0])
        caption=cn('水平投影不变，倾斜程度改变').move_to([0,5.6,0])
        def moving():
            A,B=endpoints(k.get_value());H=(B[0],A[1])
            return VGroup(Line(xy(A),xy(B),color=ORANGE,stroke_width=3.5),DashedLine(xy(A),xy(H),color=BLUE),DashedLine(xy(H),xy(B),color=PURPLE),Dot(xy(A),color=GREEN,radius=.07),Dot(xy(B),color=GREEN,radius=.07),eq('A',25,MUTED).move_to(xy(A)+LEFT*.3),eq('B',25,MUTED).move_to(xy(B)+RIGHT*.3))
        geometry=always_redraw(moving)
        read=number('AB',lambda:length(k.get_value()),[0,-3.6,0],ORANGE)
        formula=eq(r'AB=\sqrt{1+k^2}\,|x_1-x_2|',36,GREEN).move_to([0,-5,0])
        reason=eq(r'\Delta y=k\Delta x',31,MUTED).move_to([0,-6.4,0])
        self.add(title,caption,geometry,read,formula,reason)
        self.wait(.8);self.play(k.animate.set_value(.9),run_time=3)
        self.play(k.animate.set_value(-.8),run_time=4)
        self.play(k.animate.set_value(.3),run_time=3);self.wait(.5)
