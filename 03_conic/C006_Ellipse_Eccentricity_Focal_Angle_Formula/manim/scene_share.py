from manim import *
import math
import numpy as np
config.background_color="#F7F8FA"
config.frame_width=8
config.frame_height=128/9
INK="#213044"; BLUE="#2778BD"; ORANGE="#CD6031"; GREEN="#158068"; GRAY="#A7B4C2"; GOLD="#B77D12"
def txt(s,size=28,color=INK): return Text(s,font="Microsoft YaHei",font_size=size,color=color)
def fm(s,size=32): return MathTex(s,font_size=size,color=INK)
def brand(scene,title,subtitle):
    scene.add(txt(title,34).move_to([0,6.25,0]),txt(subtitle,25).move_to([0,5.55,0]))
    scene.add(txt("查结论 · 看图解 · 学证明｜知树 App",22).move_to([0,-6.1,0]),txt("公众号 ok-shuxue｜获取入口",20).move_to([0,-6.58,0]))
def axes(scene,xmin,xmax,ymin,ymax,point):
    scene.add(Line(point(xmin,0),point(xmax,0),color=GRAY),Line(point(0,ymin),point(0,ymax),color=GRAY))
    scene.add(fm("x",24).next_to(point(xmax,0),RIGHT,buff=.1),fm("y",24).next_to(point(0,ymax),UP,buff=.1))
def clipped(k,m,xlo=-4.3,xhi=4.3,ylo=-2.8,yhi=3.2):
    pts=[]
    for x in [xlo,xhi]:
        y=k*x+m
        if ylo-1e-9<=y<=yhi+1e-9:pts.append((x,y))
    if abs(k)>1e-12:
        for y in [ylo,yhi]:
            x=(y-m)/k
            if xlo-1e-9<=x<=xhi+1e-9 and all(abs(x-a)+abs(y-b)>1e-8 for a,b in pts):pts.append((x,y))
    return pts[:2]

A=3.; B=2.; C=math.sqrt(5)
def state(t):
    p=np.array([A*math.cos(t),B*math.sin(t)])
    u=np.array([-C,0])-p;v=np.array([C,0])-p
    theta=math.acos(np.clip(np.dot(u,v)/np.linalg.norm(u)/np.linalg.norm(v),-1,1))
    return p,abs(p[1]),theta
class FocalAngleHeight(Scene):
 def construct(self):
    brand(self,"高度怎样控制焦张角？","C006 · 固定椭圆 a=3，b=2，c=√5")
    coord=lambda x,y: np.array([.95*x,1.4+.95*y,0])
    axes(self,-3.4,3.4,-2.5,2.7,coord)
    self.add(Ellipse(width=5.7,height=3.8,color=BLUE).move_to(coord(0,0)))
    for x,label in [(-C,'F_1'),(C,'F_2')]:self.add(Dot(coord(x,0),color=BLUE),fm(label,27).next_to(coord(x,0),DOWN,buff=.17))
    t=ValueTracker(.16*PI)
    def diagram():
      p,h,theta=state(t.get_value());P=coord(*p);u=np.array([-C,0])-p;v=np.array([C,0])-p
      start=math.atan2(u[1],u[0]);delta=(math.atan2(v[1],v[0])-start+PI)%(2*PI)-PI
      return VGroup(Line(coord(-C,0),P,color=ORANGE),Line(coord(C,0),P,color=ORANGE),DashedLine(P,coord(p[0],0),color=GREEN),Arc(radius=.42,start_angle=start,angle=delta,color=ORANGE,arc_center=P),Dot(P,color=GOLD),fm('P',26).move_to(P+np.array([.25,.34*np.sign(p[1]),0])))
    self.add(always_redraw(diagram))
    initial=state(t.get_value())
    h=DecimalNumber(initial[1],num_decimal_places=2,font_size=32,color=GREEN).move_to([-1,-2.2,0]);ang=DecimalNumber(initial[2]*180/PI,num_decimal_places=1,font_size=32,color=ORANGE).move_to([1.7,-2.2,0])
    h.add_updater(lambda m:m.set_value(state(t.get_value())[1]));ang.add_updater(lambda m:m.set_value(state(t.get_value())[2]*180/PI))
    self.add(txt('h =',27).move_to([-2,-2.2,0]),h,fm(r'\theta=',30).move_to([.6,-2.2,0]),ang,fm(r'{}^\circ',25).move_to([2.5,-2.1,0]))
    self.add(fm(r'\tan\frac{\theta}{2}=\frac{c|y_P|}{b^2}=\frac{\sqrt5}{4}h',34).move_to([0,-3.4,0]))
    self.add(txt('高度相同，上下两点的焦张角也相同',25).move_to([0,-4.5,0]))
    self.wait(1);self.play(t.animate.set_value(PI/2),run_time=3,rate_func=smooth)
    result=fm(r'\sin\frac{\theta_{\max}}2=\frac ca,\quad P=(0,\pm b)',32).move_to([0,-5.25,0]);self.add(result);self.wait(2)
    self.play(t.animate.set_value(.84*PI),run_time=3);self.play(t.animate.set_value(1.5*PI),run_time=4);self.wait(2)
