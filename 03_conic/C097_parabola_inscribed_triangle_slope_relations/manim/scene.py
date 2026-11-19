
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

class C097SlopeRelations(Scene):
 def construct(self):
    header(self,"横向倒斜率相加，纵向斜率相加",r"p=1,\quad A,B\ne O,\quad A\ne B")
    for vertical in [False,True]:
        b=ValueTracker(-.8)
        if vertical:
            ax=axes([-3,3,1],[-.6,4,1],w=7.2,h=5.52,at=(0,1.35,0))
            curve=ParametricFunction(lambda t:ax.c2p(t,t*t/2),t_range=[-2.75,2.75],color=BLUE,stroke_width=3)
            equation=eq(r"x^2=2y",5.05,37)
        else:
            ax=axes([-.6,4,1],[-3,3,1],w=5.52,h=7.2,at=(0,1.2,0))
            curve=ParametricFunction(lambda t:ax.c2p(t*t/2,t),t_range=[-2.75,2.75],color=BLUE,stroke_width=3)
            equation=eq(r"y^2=2x",5.05,37)
        def geometry():
            A,B=model.state(b.get_value(),vertical);O=(0,0);PA,PB=ax.c2p(*A),ax.c2p(*B)
            return VGroup(Line(ax.c2p(*O),PA,color=ORANGE,stroke_width=3),Line(ax.c2p(*O),PB,color=PURPLE,stroke_width=3),Line(PA,PB,color=GREEN,stroke_width=4),dot(ax,*O,INK),dot(ax,*A,ORANGE),dot(ax,*B,PURPLE),MathTex('O',font_size=27,color=INK).next_to(ax.c2p(*O),DOWN+LEFT,.13),MathTex('A',font_size=29,color=ORANGE).next_to(PA,UP,.22),MathTex('B',font_size=29,color=PURPLE).next_to(PB,DOWN,.2))
        moving=always_redraw(geometry)
        formula=eq(r"k_{OA}+k_{OB}=k_{AB}" if vertical else r"\frac1{k_{OA}}+\frac1{k_{OB}}=\frac{x_B-x_A}{y_B-y_A}",-3.35,39)
        numeric=VGroup(eq(r"1+(",0,33),number(-.4,3,PURPLE),eq(r")=",0,33),number(.6,3,GREEN)).arrange(RIGHT,buff=.08).move_to([0,-4.5,0])
        leftnum=numeric[1];rightnum=numeric[3]
        leftnum.add_updater(lambda m:m.set_value(b.get_value()/2));rightnum.add_updater(lambda m:m.set_value(1+b.get_value()/2))
        ordinary=cn("AB 非竖直时，右端才是弦斜率的倒数",-5.6,24,MUTED)
        critical=cn("AB 竖直：弦斜率不存在；位移比为 0",-5.6,24,ORANGE)
        if vertical:
            caption=cn("交换 x、y 后：AB 水平时斜率 0 仍成立",-5.6,24,GREEN)
            extras=[caption]
        else:
            ordinary.set_opacity(1);critical.set_opacity(0)
            ordinary.add_updater(lambda m:m.set_opacity(int(abs(b.get_value()+2)>1e-8)))
            critical.add_updater(lambda m:m.set_opacity(int(abs(b.get_value()+2)<=1e-8)))
            extras=[ordinary,critical]
        read=reading(r"b=x_B=" if vertical else r"b=y_B=",b,lambda v:v,-2.55,3)
        objects=[ax,curve,equation,moving,formula,numeric,read]+extras
        self.add(*objects);self.wait(1)
        self.play(b.animate.set_value(-2),run_time=3,rate_func=linear);self.update_mobjects(0);self.wait(1.3)
        self.play(b.animate.set_value(-2.6),run_time=2,rate_func=linear);self.wait(.7)
        self.play(b.animate.set_value(-.8 if vertical else -2),run_time=2 if vertical else 1.5,rate_func=linear);self.wait(1.3)
        if not vertical:self.remove(*objects)
