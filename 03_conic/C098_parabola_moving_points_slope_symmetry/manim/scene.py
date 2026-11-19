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

class C098Motion(Scene):
 def construct(self):
    header(self,"两条弦转动，第三条弦方向不变",r"y^2=4x,\quad A=(1,2),\quad F=(1,0)")
    a=axes([-.7,8,1],[-6,3.3,1],w=6.35,h=6.79,at=(0,1.35,0))
    curve=ParametricFunction(lambda t:a.c2p(t*t/4,t),t_range=[-5.65,3.1],color=BLUE,stroke_width=3)
    A=dot(a,1,2,INK);F=dot(a,1,0,MUTED)
    self.add(a,curve,A,F,MathTex("A",font_size=30,color=INK).next_to(A,UP+LEFT,.12),MathTex("F",font_size=26,color=MUTED).next_to(F,RIGHT,.13))
    u=ValueTracker(0)
    def moving():
        av,m,n=model.state(u.get_value());p,q=a.c2p(*m),a.c2p(*n)
        return VGroup(Line(A.get_center(),p,color=ORANGE,stroke_width=3),Line(A.get_center(),q,color=PURPLE,stroke_width=3),Line(p,q,color=GREEN,stroke_width=4),Dot(p,color=ORANGE,radius=.075),Dot(q,color=PURPLE,radius=.075),MathTex("M",font_size=29,color=ORANGE).next_to(p,LEFT,.15),MathTex("N",font_size=29,color=PURPLE).next_to(q,RIGHT,.15))
    chords=always_redraw(moving)
    self.add(chords,eq(r"k_{AM}=-k_{AN}", -3.1,43),eq(r"u+v=-4\quad\Longrightarrow\quad k_{MN}=\frac4{u+v}=-1",-4.35,38,GREEN),cn("u、v 分别为 M、N 的纵坐标",-5.2,25,MUTED),cn("三点互异，且 AM、AN 斜率存在",-5.95,23,MUTED))
    display=reading(r"k_{AM}=",u,lambda t:4/(t+2),-2.15,2);self.add(display)
    self.wait(1.5);self.play(u.animate.set_value(1.35),run_time=4,rate_func=smooth);self.wait(1)
    self.play(u.animate.set_value(-.7),run_time=4,rate_func=smooth);self.wait(1)
    self.play(u.animate.set_value(0),run_time=3,rate_func=smooth);self.wait(2)
