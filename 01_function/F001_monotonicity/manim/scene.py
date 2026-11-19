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

class F001Motion(Scene):
 def construct(self):
    header(self,"切线斜率怎样决定升降？",r"f(x)=x^3-3x+1,\quad f'(x)=3(x^2-1)")
    a=axes([-2.1,2.1,1],[-2.3,4.3,1],w=7,h=6,at=(0,1.5,0))
    graph=a.plot(model.f,x_range=[-2,2],color=BLUE,stroke_width=3)
    x=ValueTracker(-1.9)
    def tangent():
        t=x.get_value();s=model.df(t);c=GREEN if s>1e-7 else ORANGE if s< -1e-7 else PURPLE
        return VGroup(Line(a.c2p(t-.18,model.f(t)-.18*s),a.c2p(t+.18,model.f(t)+.18*s),color=c,stroke_width=4),dot(a,t,model.f(t),c))
    self.add(a,graph,always_redraw(tangent),dot(a,-1,3,PURPLE),dot(a,1,-1,PURPLE))
    self.add(eq(r"(-1,3)",3.8,29,PURPLE).shift(LEFT*1.8),eq(r"(1,-1)",-.65,29,PURPLE).shift(RIGHT*1.8))
    self.add(reading(r"x=",x,lambda t:t,-2.2,2),reading(r"f'(x)=",x,model.df,-3.15,2),cn("正：上升     负：下降",-4.3,31),cn("先限定同一连续区间，再按导数符号分段",-5.4,24,MUTED))
    self.wait(1)
    for t,d in [(-1,2.3),(1,3.6),(1.9,2.3),(1,1.8),(-1,2.6),(-1.9,1.8)]:
        self.play(x.animate.set_value(t),run_time=d,rate_func=linear);self.wait(.7)
