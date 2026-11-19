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

class F007Motion(Scene):
 def construct(self):
    header(self,"为什么恰好缺少一个函数值？",r"y=\frac{2x+1}{x-1}=2+\frac3{x-1},\quad x\ne1")
    a=axes([-3.5,5,1],[-1.6,5.6,1],h=6.2,at=(0,1.4,0));graph=VGroup(a.plot(model.f,x_range=[-3.5,.16],color=BLUE,stroke_width=3),a.plot(model.f,x_range=[1.85,5],color=BLUE,stroke_width=3))
    # The finite branches end only at the display boundary; no fake pole segment.
    self.add(a,graph,dash(a,(1,-1.6),(1,5.6)),dash(a,(-3.5,2),(5,2)),eq(r"y=2",1.9,28,MUTED).shift(LEFT*2.7))
    t=ValueTracker(5);line=always_redraw(lambda:Line(a.c2p(-3.5,t.get_value()),a.c2p(5,t.get_value()),color=ORANGE,stroke_width=2))
    point=always_redraw(lambda:dot(a,model.inverse(t.get_value()),t.get_value(),ORANGE))
    self.add(line,point,reading(r"y=t=",t,lambda v:v,-2.3,2),eq(r"t\ne2:\quad x=1+\frac3{t-2}",-3.55,42),cn("每个 t≠2 都能反求到合法的 x",-4.65,29,GREEN),cn("完整定义域；有限窗口只显示部分曲线",-5.7,23,MUTED))
    self.wait(1);self.play(t.animate.set_value(3),run_time=3);self.wait(1);self.remove(point)
    self.play(t.animate.set_value(2),run_time=1);notice=cn("t=2：方程 3/(x−1)=0 无解",-.8,29,ORANGE);self.add(notice);self.wait(2);self.remove(notice,line);t.set_value(1);self.add(line,point)
    self.play(t.animate.set_value(-1),run_time=3);self.wait(1);self.remove(point,line);t.set_value(5);self.add(line,point);self.update_mobjects(0);self.wait(2)
