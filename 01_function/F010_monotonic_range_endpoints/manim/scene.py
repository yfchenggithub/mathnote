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

class F010Motion(Scene):
 def construct(self):
    header(self,"最值看端点，完整值域还要连续",r"x\in[a,b],\quad a\le b")
    a=axes([0,3.4,1],[0,8,1],h=5.6,at=(0,1.8,0));graph=a.plot(model.continuous,x_range=[0,3],color=BLUE,stroke_width=3);x=ValueTracker(0)
    moving=always_redraw(lambda:trace(a,model.continuous,x.get_value(),ORANGE));rangebar=always_redraw(lambda:Line(a.c2p(0,1),a.c2p(0,max(1.001,model.continuous(x.get_value()))),color=GREEN,stroke_width=7))
    form=eq(r"f(x)=2x+1,\quad x\in[0,3]",-1.9,39);answer=eq(r"f(0)=1,\quad f(3)=7\quad\Rightarrow\quad y\in[1,7]",-3.15,36,GREEN);caption=cn("连续地走过每个中间高度",-4.45,30);self.add(a,graph,moving,rangebar,form,answer,caption)
    self.wait(1);self.play(x.animate.set_value(3),run_time=4,rate_func=linear);self.wait(1.5)
    self.remove(moving,rangebar);self.play(*[FadeOut(o) for o in [a,graph,form,answer,caption]],run_time=.5)
    b=axes([0,1.2,.5],[0,2.5,.5],h=5.6,at=(0,1.8,0));g=b.plot(lambda v:v,x_range=[0,.999],color=BLUE,stroke_width=3);hole=Circle(radius=.07,color=BLUE,fill_color=BG,fill_opacity=1).move_to(b.c2p(1,1));endpoint=dot(b,1,2,ORANGE)
    band=Polygon(b.c2p(0,1),b.c2p(1,1),b.c2p(1,2),b.c2p(0,2),stroke_width=0,fill_color=ORANGE,fill_opacity=.1)
    self.add(band,b,g,hole,endpoint,eq(r"f(x)=x\ (0\le x<1),\quad f(1)=2",-1.9,37),eq(r"\min f=0,\quad\max f=2",-3,40),eq(r"\text{Range}=[0,1)\cup\{2\}\ne[0,2]",-4.15,40,ORANGE),cn("端点仍是最值，但中间跳过了一段高度",-5.35,26,MUTED))
    t=ValueTracker(0);p=always_redraw(lambda:dot(b,t.get_value(),t.get_value(),ORANGE));self.add(p);self.play(t.animate.set_value(.99),run_time=3,rate_func=linear);self.wait(1);self.remove(p);self.play(Indicate(endpoint,color=ORANGE),run_time=1);self.wait(3)
