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

class F005Motion(Scene):
 def construct(self):
    header(self,"同趋于零，比值却趋于 2",r"f(x)=x^2-1,\quad g(x)=x-1,\quad x\to1")
    a=axes([-.25,2.2,1],[-1.5,4.1,1],h=6.1,at=(0,1.5,0));f=a.plot(model.f,x_range=[0,2.15],color=BLUE,stroke_width=3);g=a.plot(model.g,x_range=[0,2.15],color=ORANGE,stroke_width=3)
    origin=a.c2p(1,0);h=ValueTracker(.8)
    def secants():
        x=1+h.get_value()
        return VGroup(Line(origin,a.c2p(x,model.f(x)),color=BLUE,stroke_width=5),Line(origin,a.c2p(x,model.g(x)),color=ORANGE,stroke_width=5),dot(a,x,model.f(x),BLUE),dot(a,x,model.g(x),ORANGE),dash(a,(x,0),(x,model.f(x))))
    self.add(a,f,g,dot(a,1,0,INK),always_redraw(secants),cn("蓝：分子 f     橙：分母 g",-1.9,25))
    self.add(reading(r"x=1+h,\quad h=",h,lambda t:t,-2.8,3),reading(r"\frac{f(1+h)}{g(1+h)}=2+h=",h,lambda t:2+t,-3.9,4),eq(r"\lim_{x\to1}\frac{x^2-1}{x-1}=\frac{f'(1)}{g'(1)}=2",-5,38,GREEN),cn("本例条件满足；0/0 本身不是一个数",-5.95,24,MUTED))
    self.wait(1);self.play(h.animate.set_value(.03),run_time=4);self.wait(1.5);h.set_value(-.8);self.update_mobjects(0);self.wait(.2)
    self.play(h.animate.set_value(-.03),run_time=4);self.wait(1.5);h.set_value(.8);self.update_mobjects(0);self.wait(.2);self.wait(2)
