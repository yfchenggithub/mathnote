
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

class C096Closure(Scene):
 def construct(self):
    header(self,"两条弦切圆，第三条也切圆",r"y^2=x,\quad\Gamma:(x-2)^2+y^2=1")
    self.add(eq(r"k=r=1,\quad h=r+\frac{r^2}{k}=2",5.05,30))
    ax=axes([-.5,4.7,1],[-2.5,2.5,1],w=6.448,h=6.2,at=(0,1.05,0))
    parabola=ParametricFunction(lambda t:ax.c2p(t*t,t),t_range=[-2.13,2.13],color=BLUE,stroke_width=3)
    unit=np.linalg.norm(ax.c2p(1,0)-ax.c2p(0,0))
    assert abs(unit-np.linalg.norm(ax.c2p(0,1)-ax.c2p(0,0)))<1e-10
    circle=Circle(radius=unit,color=PURPLE,stroke_width=3,fill_color=PURPLE,fill_opacity=.045).move_to(ax.c2p(2,0))
    M=dot(ax,2,0,PURPLE);mlabel=MathTex('M',font_size=28,color=PURPLE).next_to(M,DOWN,.16)
    a=ValueTracker(-.22)
    def side(i,j,color,showpoints=False):
        s=model.state(a.get_value());u,v=s['parameters'][i],s['parameters'][j];A,B=s['points'][i],s['points'][j]
        L=model.line(u,v);ends=model.clip_line(L);T=model.foot(s['center'],L)
        g=VGroup(DashedLine(ax.c2p(*ends[0]),ax.c2p(*ends[1]),color=color,stroke_width=1.3,dash_length=.09,stroke_opacity=.45),Line(ax.c2p(*A),ax.c2p(*B),color=color,stroke_width=3.5),dash(ax,s['center'],T,color),dot(ax,*T,color))
        return g
    first=always_redraw(lambda:side(0,1,ORANGE));second=always_redraw(lambda:side(0,2,PURPLE));third=always_redraw(lambda:side(1,2,GREEN))
    def vertices():
        ps=model.state(a.get_value())['points'];g=VGroup()
        for i,P in enumerate(ps):
            D=dot(ax,*P,INK);lab=MathTex('A_'+str(i+1),font_size=29,color=INK).next_to(D,UP if i==1 else DOWN+LEFT,buff=.2)
            if i==0:lab.move_to(ax.c2p(-.3,a.get_value()+.5))
            lab.add_background_rectangle(color=BG,opacity=1,buff=.055)
            g.add(D,lab)
        return g
    points=always_redraw(vertices)
    self.add(ax,parabola,circle,M,mlabel,first,second,points,reading(r"a=y_{A_1}=",a,lambda v:v,-2.95,3))
    start=cn("已知：两条共顶点的弦与圆相切",-4.8,29)
    end=cn("第三条弦也始终与同一个圆相切",-4.8,29,GREEN)
    result=eq(r"d(M,A_2A_3)=r=1",-3.85,40,GREEN)
    self.add(start,cn("三点互异；相切指三边所在的整条直线",-5.75,24,MUTED))
    self.wait(1.6);self.remove(start);self.add(third,end,result);self.bring_to_front(points,M,mlabel)
    vertical=eq(r"a=0:\quad A_2A_3:\ x=3",-2.3,29,GREEN)
    self.play(a.animate.set_value(0),run_time=3);self.update_mobjects(0);self.add(vertical);self.wait(1.5);self.remove(vertical)
    self.play(a.animate.set_value(.22),run_time=3);self.wait(1)
    self.play(a.animate.set_value(0),run_time=2);self.update_mobjects(0);self.add(vertical);self.wait(1.3);self.remove(vertical)
    self.play(a.animate.set_value(-.22),run_time=2.5);self.wait(1.5)
