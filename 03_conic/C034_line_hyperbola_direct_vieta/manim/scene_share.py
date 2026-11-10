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

def roots(k,m):
 a=1-4*k*k;b=-8*k*m;c=-4*(m*m+1)
 if abs(a)<1e-9:return [] if abs(b)<1e-9 else [-c/b]
 d=b*b-4*a*c
 if d<-1e-8:return []
 return sorted([(-b-math.sqrt(max(0,d)))/(2*a),(-b+math.sqrt(max(0,d)))/(2*a)])
class HyperbolaVietaCases(Scene):
 def construct(self):
    brand(self,"一个交点，也可能不是相切","C034 · x²/4−y²=1；先检查二次项")
    coord=lambda x,y:np.array([.75*x,1.3+.75*y,0]);axes(self,-4.4,4.4,-2.6,3.3,coord)
    for s in [-1,1]:self.add(ParametricFunction(lambda u,s=s:coord(s*2*math.cosh(u),math.sinh(u)),t_range=[-1.4,1.4],color=BLUE))
    for k0 in [-.5,.5]:self.add(DashedLine(coord(-4.3,-4.3*k0),coord(4.3,4.3*k0),color=GRAY))
    k=ValueTracker(1);m=ValueTracker(2)
    def geometry():
      pts=clipped(k.get_value(),m.get_value(),-4.4,4.4,-2.6,3.3);g=VGroup(Line(coord(*pts[0]),coord(*pts[1]),color=ORANGE))
      for x in roots(k.get_value(),m.get_value()):
       y=k.get_value()*x+m.get_value()
       if -4.4<=x<=4.4 and -2.6<=y<=3.3:g.add(Dot(coord(x,y),color=GOLD))
      return g
    drawing=always_redraw(geometry);self.add(drawing)
    formula=fm(r'-3x^2-8mx-4(m^2+1)=0',31).move_to([0,-2.3,0]);self.add(formula)
    detail=fm(r'M=-3\ne0,\quad H=m^2-3',33).move_to([0,-3.45,0]);self.add(detail)
    note=txt('y=x+2：两交点在同一支上',26).move_to([0,-4.55,0]);self.add(note);self.wait(2)
    for val,label in [(math.sqrt(3),'m=√3：H=0，相切'),(1.4,'m=1.4：H<0，无实交点')]:
      self.remove(note);self.play(m.animate.set_value(val),run_time=3);note=txt(label,26).move_to([0,-4.55,0]);self.add(note);self.wait(1.5)
    self.remove(formula,detail,note);k.set_value(.5);m.set_value(1);drawing.update(0)
    self.add(fm(r'y=\frac{x}{2}+1\ \Longrightarrow\ -4x-8=0',31).move_to([0,-2.3,0]),fm(r'M=0,\quad P=(-2,0)',33).move_to([0,-3.45,0]),txt('平行于渐近线：一次交点，并非切点',25).move_to([0,-4.55,0]),txt('二次项为零时，不能除以 M 使用二根韦达',24).move_to([0,-5.3,0]));self.wait(3)
