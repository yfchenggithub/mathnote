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

A=3.;B=2.;C=math.sqrt(5)
def state(t):
 p=np.array([A*math.cos(t),B*math.sin(t)]);n=p/np.array([A*A,B*B]);foot=n/np.dot(n,n)
 r1=np.linalg.norm(p-np.array([-C,0]));r2=np.linalg.norm(p-np.array([C,0]));d=1/np.linalg.norm(n)
 return p,foot,r1,r2,d
class TangentFocalProduct(Scene):
 def construct(self):
    brand(self,"切线在变，乘积不变","C021 · a=3，b=2；d 是原点到切线的垂距")
    coord=lambda x,y:np.array([.92*x,1.4+.92*y,0])
    axes(self,-3.5,3.5,-2.6,3.1,coord)
    self.add(Ellipse(width=5.52,height=3.68,color=BLUE).move_to(coord(0,0)),fm('O',25).next_to(coord(0,0),DOWN))
    for x,label in [(-C,'F_1'),(C,'F_2')]:self.add(Dot(coord(x,0),color=BLUE),fm(label,25).next_to(coord(x,0),DOWN,buff=.15))
    t=ValueTracker(.1*PI)
    def diagram():
      p,foot,r1,r2,d=state(t.get_value());n=p/np.array([9,4]);aa,bb=n;pts=[]
      for x in [-3.5,3.5]:
       if abs(bb)>1e-9:
        y=(1-aa*x)/bb
        if -2.6<=y<=3.1:pts.append((x,y))
      for y in [-2.6,3.1]:
       if abs(aa)>1e-9:
        x=(1-bb*y)/aa
        if -3.5<=x<=3.5:pts.append((x,y))
      tangent=Line(coord(*pts[0]),coord(*pts[1]),color=ORANGE)
      return VGroup(tangent,Line(coord(-C,0),coord(*p),color=GRAY),Line(coord(C,0),coord(*p),color=GRAY),Line(coord(0,0),coord(*foot),color=GREEN,stroke_width=5),Dot(coord(*p),color=GOLD),Dot(coord(*foot),color=GREEN),fm('P',26).move_to(coord(*p)+[.25,.28,0]),fm('d',29).move_to(coord(*(foot*.5))+[-.25,.12,0]))
    self.add(always_redraw(diagram))
    specs=[('d',lambda:state(t.get_value())[4],-2.4),(r'\sqrt{r_1r_2}',lambda:math.sqrt(state(t.get_value())[2]*state(t.get_value())[3]),0),('product',lambda:math.sqrt(state(t.get_value())[2]*state(t.get_value())[3])*state(t.get_value())[4],2.4)]
    for lab,fn,x in specs:
      title=txt('乘积',26) if lab=='product' else fm(lab,30)
      self.add(title.move_to([x,-2.4,0]));num=DecimalNumber(fn(),num_decimal_places=3,font_size=32,color=GREEN).move_to([x,-3.2,0]);num.add_updater(lambda m,f=fn:m.set_value(f()));self.add(num)
    self.add(fm(r'\sqrt{r_1r_2}\,d=ab=6',38).move_to([0,-4.4,0]),txt('焦半径的几何平均 × 垂距',25).move_to([0,-5.2,0]))
    self.wait(1);self.play(t.animate.set_value(PI/2),run_time=3);self.wait(1.5);self.play(t.animate.set_value(.9*PI),run_time=4);self.wait(1);self.play(t.animate.set_value(.1*PI),run_time=4);self.wait(1.5)
