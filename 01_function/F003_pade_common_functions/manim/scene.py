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

class F003Motion(Scene):
 def construct(self):
    header(self,"分式近似，究竟差多少？",r"E(x)=\frac{x^2+6x+12}{x^2-6x+12},\quad0\le x\le1")
    a=axes([0,1.1,.5],[0,3,1],h=3.7,at=(0,3.1,0));b=axes([0,1.1,.5],[0,4.6,1],h=2.6,at=(0,-.95,0),labels=False)
    f=a.plot(model.exact,x_range=[0,1],color=BLUE,stroke_width=4);g=a.plot(model.rational,x_range=[0,1],color=ORANGE,stroke_width=2)
    error=b.plot(lambda t:1000*model.error(t),x_range=[0,1],color=PURPLE,stroke_width=3)
    self.add(a,b,f,g,error,cn("蓝：真实值   橙：分式近似",.75,24),eq(r"10^3\bigl(e^x-E(x)\bigr)",-2.75,32,PURPLE))
    x=ValueTracker(0);self.add(always_redraw(lambda:trace(a,model.exact,x.get_value(),BLUE)),always_redraw(lambda:trace(b,lambda t:1000*model.error(t),x.get_value(),PURPLE)))
    self.add(reading(r"e^x-E(x)\approx",x,model.error,-3.7,6),eq(r"0\le e^x-E(x)\le\frac{3x^5}{665}",-4.8,39,GREEN),cn("误差另图放大；接近不等于相等",-5.8,25,MUTED))
    self.wait(1.2);self.play(x.animate.set_value(1),run_time=5,rate_func=linear);self.wait(2)
    self.play(x.animate.set_value(.1),run_time=4,rate_func=linear);self.wait(1.5);self.play(x.animate.set_value(0),run_time=1.5);self.wait(1.5)
