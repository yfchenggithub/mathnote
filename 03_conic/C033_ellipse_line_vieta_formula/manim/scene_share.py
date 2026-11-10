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

def roots(m):
 H=6.25-m*m
 if H<-1e-9:return []
 d=12*math.sqrt(max(0,H));return [(-9*m-d)/12.5,(-9*m+d)/12.5]
class EllipseVietaIntersections(Scene):
 def construct(self):
    brand(self,"先确认实交点，再用韦达","C033 · x²/9+y²/4=1；直线 y=x/2+m")
    coord=lambda x,y:np.array([.82*x,1.25+.82*y,0]);axes(self,-3.7,3.7,-2.6,3.5,coord)
    self.add(Ellipse(width=4.92,height=3.28,color=BLUE).move_to(coord(0,0)))
    m=ValueTracker(0)
    def geometry():
      pts=clipped(.5,m.get_value(),-3.7,3.7,-2.6,3.5);g=VGroup(Line(coord(*pts[0]),coord(*pts[1]),color=ORANGE))
      for i,x in enumerate(roots(m.get_value())):
       y=.5*x+m.get_value();g.add(Dot(coord(x,y),color=GOLD),DashedLine(coord(x,y),coord(x,0),color=GRAY))
      return g
    self.add(always_redraw(geometry));self.add(fm(r'6.25x^2+9mx+9(m^2-4)=0',32).move_to([0,-2.3,0]))
    self.add(fm(r'x_1+x_2=-\frac{36m}{25},\quad x_1x_2=\frac{36(m^2-4)}{25}',28).move_to([0,-3.45,0]))
    self.add(fm(r'H=6.25-m^2',34).move_to([0,-4.4,0]))
    note=txt('m=0：H>0，有两个不同实交点',26).move_to([0,-5.25,0]);self.add(note);self.wait(1)
    for val,label in [(1.5,'m=1.5：两个实根对应两个交点'),(2.5,'m=2.5：H=0，相切并重计切点'),(2.9,'m=2.9：H<0，不解释为实交点')]:
      self.remove(note);self.play(m.animate.set_value(val),run_time=3);note=txt(label,25).move_to([0,-5.25,0]);self.add(note);self.wait(1.5)
    self.remove(note);self.play(m.animate.set_value(0),run_time=2);self.add(txt('本例消去 y 合法：直线的 y 系数非零',24).move_to([0,-5.25,0]));self.wait(1)
