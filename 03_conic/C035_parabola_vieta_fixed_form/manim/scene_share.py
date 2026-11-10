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

def intersections(x):return [] if x<0 else [(x,2*math.sqrt(x)),(x,-2*math.sqrt(x))]
class ParabolaVietaProjection(Scene):
 def construct(self):
    brand(self,"横坐标重根，未必有实交点","C035 · y²=4x；竖直线 x=x₀")
    coord=lambda x,y:np.array([.9*(x-1),1.25+.9*y,0]);axes(self,-1.5,3.5,-3.4,3.4,coord)
    self.add(ParametricFunction(lambda y:coord(y*y/4,y),t_range=[-3.35,3.35],color=BLUE))
    x0=ValueTracker(-1)
    def geometry():
      x=x0.get_value();g=VGroup(Line(coord(x,-3.4),coord(x,3.4),color=ORANGE))
      for a,b in intersections(x):g.add(Dot(coord(a,b),color=GOLD),DashedLine(coord(a,b),coord(0,b),color=GRAY))
      return g
    self.add(always_redraw(geometry))
    self.add(fm(r'(x-x_0)^2=0',34).move_to([0,-2.5,0]),fm(r'y^2=4x_0:\quad y_1+y_2=0,\ y_1y_2=-4x_0',29).move_to([0,-3.65,0]))
    note=txt('x₀=−1：y²=−4，没有实交点',26).move_to([0,-4.7,0]);self.add(note);self.add(txt('和、积解释为实坐标时，必须有 x₀≥0',24).move_to([0,-5.4,0]));self.wait(2)
    for value,label in [(0,'x₀=0：顶点切线，纵坐标也为重根'),(1,'x₀=1：P(1,2)、Q(1,−2)，两个交点'),(2.25,'x₀=2.25：上下两点，横坐标仍相同')]:
      self.remove(note);self.play(x0.animate.set_value(value),run_time=2.5);note=txt(label,25).move_to([0,-4.7,0]);self.add(note);self.wait(1.5)
