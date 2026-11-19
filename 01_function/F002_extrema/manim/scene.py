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

class F002Motion(Scene):
 def construct(self):
    header(self,"导数为零，就一定有极值吗？",r"x_0=0,\quad x\to0^-,\quad x\to0^+")
    a=axes([-1.8,1.8,1],[-3.8,3.8,1],w=6.8,h=6,at=(0,1.4,0));self.add(a)
    specs=[(model.peak,r"f(x)=1-x^2",r"f'(0)=0", "先增后减：极大值",GREEN),(model.stationary,r"f(x)=x^3",r"f'(0)=0","一直递增：不是极值",ORANGE),(model.corner,r"f(x)=|x|",r"f'_-(0)=-1,\quad f'_+(0)=1","不可导，也能有极小值",PURPLE)]
    x=ValueTracker(-1.45)
    for idx,(f,form,deriv,caption,color) in enumerate(specs):
        x.set_value(-1.45);graph=a.plot(f,x_range=[-1.5,1.5],color=BLUE,stroke_width=3);moving=always_redraw(lambda f=f:trace(a,f,x.get_value(),ORANGE))
        content=VGroup(eq(form,-2.35,46),eq(deriv,-3.4,38),cn(caption,-4.55,31,color),cn("极值要比较左右足够近的函数值",-5.55,25,MUTED),dot(a,0,f(0),color))
        if idx==0:self.add(graph,content)
        else:self.play(FadeIn(graph),FadeIn(content),run_time=.5)
        self.add(moving)
        self.play(x.animate.set_value(0),run_time=2,rate_func=linear);self.wait(1.1);self.play(x.animate.set_value(1.45),run_time=2,rate_func=linear);self.wait(1)
        self.remove(moving)
        if idx<2:self.play(FadeOut(graph),FadeOut(content),run_time=.4)
        else:self.wait(1.5)
