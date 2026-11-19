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

class F004Motion(Scene):
 def construct(self):
    header(self,"相消以后，二次项不能丢",r"e^x\approx1+x+\frac{x^2}{2},\quad |x|\le\frac12")
    a=axes([-.55,.55,.25],[.4,1.9,.5],h=3.6,at=(0,3.05,0));b=axes([-.55,.55,.25],[.38,.62,.05],h=2.5,at=(0,-1,0),labels=False)
    graph=a.plot(model.exact,x_range=[-.5,.5],color=BLUE,stroke_width=4);approx=a.plot(model.quadratic,x_range=[-.5,.5],color=ORANGE,stroke_width=2)
    res=VGroup(*[b.plot(model.residual,x_range=pair,color=PURPLE,stroke_width=3) for pair in [[-.5,-.002],[.002,.5]]]);hole=Circle(radius=.065,color=PURPLE,fill_color=BG,fill_opacity=1).move_to(b.c2p(0,.5))
    self.add(a,b,graph,approx,res,dash(b,(-.5,.5),(.5,.5)),hole,MathTex(r"\frac12",font_size=29,color=PURPLE).next_to(b.c2p(-.5,.5),LEFT,.12),cn("蓝：指数函数   橙：二次近似",.75,24),eq(r"R(x)=\frac{e^x-1-x}{x^2}\quad(x\ne0)",-2.75,35))
    h=ValueTracker(.5)
    self.add(always_redraw(lambda:VGroup(dot(a,h.get_value(),model.exact(h.get_value()),ORANGE),dot(a,-h.get_value(),model.exact(-h.get_value()),GREEN),dot(b,h.get_value(),model.residual(h.get_value()),ORANGE),dot(b,-h.get_value(),model.residual(-h.get_value()),GREEN))))
    self.add(reading(r"R(h)\approx",h,model.residual,-3.65,5),eq(r"\lim_{x\to0}\frac{e^x-1-x}{x^2}=\frac12",-4.75,42,PURPLE),cn("从左右靠近；空心点不代表 x=0 有定义",-5.8,24,MUTED))
    self.wait(1);self.play(h.animate.set_value(.025),run_time=5);self.wait(2);self.play(h.animate.set_value(.5),run_time=4);self.wait(1);self.play(h.animate.set_value(.025),run_time=3);self.wait(2)
