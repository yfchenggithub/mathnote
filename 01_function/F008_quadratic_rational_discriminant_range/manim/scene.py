from manim import *
import math, numpy as np, sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import model
config.frame_width=9
config.frame_height=16
BG="#F7F8FA"; INK="#213044"; MUTED="#526275"; BLUE="#2778BD"; ORANGE="#CD6031"; PURPLE="#8055B2"; GREEN="#158068"; AXIS="#A7B4C2"
def cn(s,y=0,size=30,color=INK):
    m=Text(s,font="Microsoft YaHei",font_size=size,color=color)
    if m.width>8: m.scale_to_fit_width(8)
    return m.move_to([0,y,0])
def eq(s,y=0,size=39,color=INK):
    m=MathTex(s,font_size=size,color=color)
    if m.width>7.8:m.scale_to_fit_width(7.8)
    return m.move_to([0,y,0])
def header(scene,title,condition):
    scene.camera.background_color=BG
    scene.add(cn(title,7.05,33),eq(condition,5.95,33),cn("查结论 · 看图解 · 学证明｜知树 App",-6.85,22,MUTED),cn("公众号 ok-shuxue｜获取入口",-7.4,20,MUTED))
def axes(xr,yr,w=7.1,h=5.4,at=(0,1.6,0),labels=True):
    a=Axes(x_range=xr,y_range=yr,x_length=w,y_length=h,tips=True,axis_config={"color":AXIS,"stroke_width":1.7,"include_ticks":False,"tip_width":.1,"tip_height":.12}).move_to(at)
    if labels:
        a.add(MathTex("x",font_size=26,color=MUTED).next_to(a.x_axis.get_end(),RIGHT,buff=.08),MathTex("y",font_size=26,color=MUTED).next_to(a.y_axis.get_end(),UP,buff=.08))
    return a
def dot(a,x,y,color=ORANGE):return Dot(a.c2p(x,y),radius=.07,color=color)
def dash(a,p,q,color=AXIS):return DashedLine(a.c2p(*p),a.c2p(*q),color=color,stroke_width=1.5,dash_length=.09)
def trace(a,f,x,color=ORANGE):
    y=f(x)
    return VGroup(dot(a,x,y,color),dash(a,(x,0),(x,y)),dash(a,(0,y),(x,y)))
def number(value,places=3,color=ORANGE):return DecimalNumber(value,num_decimal_places=places,font_size=33,color=color)
def reading(prefix,tracker,fn,y,places=3):
    lab=eq(prefix,0,33);n=number(fn(tracker.get_value()),places);g=VGroup(lab,n).arrange(RIGHT,buff=.18).move_to([0,y,0]);n.add_updater(lambda m:m.set_value(fn(tracker.get_value())));return g

class F008Motion(Scene):
 def construct(self):
    header(self,"判别式给出候选，还要查边界",r"F(x)=\frac{2x^2+3}{x^2+1}=2+\frac1{x^2+1}")
    a=axes([-4.3,4.3,1],[0,4,1],h=5.7,at=(0,1.7,0));graph=a.plot(model.f,x_range=[-4.2,4.2],color=BLUE,stroke_width=3)
    self.add(a,graph,dash(a,(-4.2,2),(4.2,2)),eq(r"y=2",1.1,28,MUTED).shift(LEFT*2.85))
    t=ValueTracker(3.4)
    line=always_redraw(lambda:Line(a.c2p(-4.2,t.get_value()),a.c2p(4.2,t.get_value()),color=ORANGE,stroke_width=2))
    pts=always_redraw(lambda:VGroup(*[dot(a,x,t.get_value(),ORANGE) for x in model.roots(t.get_value()) if abs(x)<=4.2]))
    self.add(line,pts,reading(r"y=",t,lambda v:v,-1.7,2),eq(r"(2-y)x^2+(3-y)=0",-2.8,40),eq(r"\Delta(y)\ge0\iff y\in[2,3]",-3.9,37),eq(r"y=2:\ 1=0\quad\Longrightarrow\quad y\in(2,3]",-5.05,37,GREEN),cn("二次项消失的值必须单独代回",-5.95,24,MUTED))
    self.wait(1);self.play(t.animate.set_value(3),run_time=2);self.wait(1.3);self.play(t.animate.set_value(2.5),run_time=2);self.wait(.8);self.play(t.animate.set_value(2.1),run_time=2);self.wait(1)
    self.remove(pts);self.play(t.animate.set_value(2),run_time=1);self.wait(2.5);self.add(pts);self.play(t.animate.set_value(3.4),run_time=1.5);self.wait(1)
