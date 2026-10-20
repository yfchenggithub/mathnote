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


class C023Animation(Scene):
    def construct(self):
        a,b=ValueTracker(1),ValueTracker(1)
        mode=[False]
        beta=lambda:6/a.get_value() if mode[0] else b.get_value()
        xy=lambda p:np.array([.94*p[0],.94*p[1]+.7,0])
        title=cn('圆怎样变成椭圆？',32).move_to([0,6.9,0])
        caption=cn('从单位圆盘开始').move_to([0,5.6,0])
        shape=always_redraw(lambda:ParametricFunction(lambda t:xy(point(t,a.get_value(),beta())),t_range=[0,TAU],color=BLUE,stroke_width=3,fill_color=BLUE,fill_opacity=.12))
        radii=always_redraw(lambda:VGroup(Line(xy((0,0)),xy((a.get_value(),0)),color=ORANGE,stroke_width=3),Line(xy((0,0)),xy((0,beta())),color=PURPLE,stroke_width=3),eq('a',27,ORANGE).move_to(xy((a.get_value()/2,0))+DOWN*.3),eq('b',27,PURPLE).move_to(xy((0,beta()/2))+LEFT*.3)))
        result=eq(r'S=\pi ab',42,GREEN).move_to([0,-4.1,0])
        read=number(r'S/\pi',lambda:area(a.get_value(),beta())/PI,[0,-5.3,0],GREEN)
        note=cn('面积乘上两个方向的伸缩倍数',25,MUTED).move_to([0,-6.5,0])
        self.add(title,caption,axes(xy,(-3.7,3.7),(-3.4,3.4)),shape,radii,result,read,note)
        self.wait(.8)
        swap(self,(caption,cn('横向伸长 3 倍').move_to(caption)))
        self.play(a.animate.set_value(3),run_time=2)
        swap(self,(caption,cn('再纵向伸长 2 倍，面积成为 6π').move_to(caption)))
        self.play(b.animate.set_value(2),run_time=2)
        self.wait(1)
        swap(self,(caption,cn('保持 ab=6，形状变化而面积不变',25,GREEN).move_to(caption)))
        mode[0]=True
        self.play(a.animate.set_value(2.4),run_time=2)
        self.play(a.animate.set_value(3),run_time=1.5)
        mode[0]=False
        b.set_value(2)
        swap(self,(caption,cn('逆向还原，回到单位圆').move_to(caption)))
        self.play(b.animate.set_value(1),run_time=1.5)
        self.play(a.animate.set_value(1),run_time=1.5)
        swap(self,(caption,cn('从单位圆盘开始').move_to(caption)))
        self.wait(.5)
