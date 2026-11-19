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

class F009Motion(Scene):
 def construct(self):
    header(self,"换了字母，允许的范围不能变",r"y=(\sqrt{x-1}-2)^2,\quad2\le x\le5")
    a=axes([1.5,5.5,1],[0,1.4,.5],h=2.7,at=(0,3.3,0));b=axes([0,3.1,1],[0,4.3,1],h=3.1,at=(0,-.45,0),labels=False)
    curve=a.plot(model.original,x_range=[2,5],color=BLUE,stroke_width=3);whole=b.plot(model.transformed,x_range=[0,3],color=AXIS,stroke_width=2);part=b.plot(model.transformed,x_range=[1,2],color=GREEN,stroke_width=5)
    self.add(a,b,curve,whole,part,eq(r"t",-2.15,27).shift(RIGHT*3.7),cn("同一个函数值，对应两种横坐标",1.3,24),dot(a,2,1,BLUE),dot(a,5,0,BLUE),dot(b,1,1,GREEN),dot(b,2,0,GREEN))
    for ax,xs in [(a,[2,5]),(b,[1,2])]:
      for v in xs:self.add(MathTex(str(v),font_size=25,color=INK).next_to(ax.c2p(v,0),DOWN,.12))
    x=ValueTracker(2)
    self.add(always_redraw(lambda:VGroup(dot(a,x.get_value(),model.original(x.get_value()),ORANGE),dot(b,model.substitution(x.get_value()),model.original(x.get_value()),ORANGE))))
    self.add(reading(r"t=\sqrt{x-1}=",x,model.substitution,-2.85,3),eq(r"1\le t\le2,\quad y=(t-2)^2",-3.9,41),eq(r"0\le y\le1",-4.95,47,GREEN),cn("灰色抛物线部分不属于本题允许范围",-5.9,24,MUTED))
    self.wait(1.2);self.play(x.animate.set_value(5),run_time=5,rate_func=linear);self.wait(2);self.play(x.animate.set_value(2),run_time=5,rate_func=linear);self.wait(2)
