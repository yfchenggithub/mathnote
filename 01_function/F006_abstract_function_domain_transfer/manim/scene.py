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

class F006Motion(Scene):
 def construct(self):
    header(self,"能否代入，要看括号里的数",r"D_f=[1,3],\quad t=2x-1")
    a=axes([0,3.1,1],[-1.2,5.3,1],h=5.9,at=(0,1.6,0));a.remove(a[-1]);a.add(MathTex("t",font_size=26,color=MUTED).next_to(a.y_axis.get_end(),UP,.08));graph=a.plot(model.inner,x_range=[0,3],color=BLUE,stroke_width=3)
    band=Polygon(a.c2p(0,1),a.c2p(3,1),a.c2p(3,3),a.c2p(0,3),color=GREEN,fill_opacity=.09,stroke_width=0)
    self.add(band,a,graph,dash(a,(0,1),(1,1),GREEN),dash(a,(0,3),(2,3),GREEN),Line(a.c2p(1,0),a.c2p(2,0),stroke_width=7,color=GREEN))
    for x,y in [(1,1),(2,3)]:self.add(dot(a,x,y,GREEN),dash(a,(x,0),(x,y)),MathTex(str(x),color=INK,font_size=27).next_to(a.c2p(x,0),DOWN,.15))
    x=ValueTracker(.3);self.add(always_redraw(lambda:trace(a,model.inner,x.get_value(),GREEN if model.admissible(x.get_value()) else ORANGE)))
    yes=cn("允许代入：内层值在 [1,3] 内",-3.9,30,GREEN);no=cn("不能代入：内层值超出范围",-3.9,30,ORANGE)
    yes.add_updater(lambda m:m.set_opacity(int(model.admissible(x.get_value()))));no.add_updater(lambda m:m.set_opacity(int(not model.admissible(x.get_value()))))
    yes.set_opacity(int(model.admissible(x.get_value())));no.set_opacity(int(not model.admissible(x.get_value())))
    self.add(reading(r"x=",x,lambda t:t,-1.95,2),reading(r"t=2x-1=",x,model.inner,-2.85,2),yes,no,eq(r"1\le2x-1\le3\iff1\le x\le2",-5.05,39),cn("先算内层，再检查是否属于外层定义域",-5.95,23,MUTED))
    self.wait(1)
    for t,d in [(1,1.8),(2,3),(2.7,1.8),(2,1.8),(1,3),(.3,1.8)]:self.play(x.animate.set_value(t),run_time=d,rate_func=linear);self.wait(.7)
