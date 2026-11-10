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

def approx(a,b):
 h=((a-b)/(a+b))**2
 return PI*(a+b)*(1+3*h/(10+math.sqrt(4-3*h)))
def reference(a,b,n=8192):
 ts=np.linspace(0,TAU,n+1);v=np.sqrt(a*a*np.sin(ts)**2+b*b*np.cos(ts)**2)
 return TAU/n*(v[0]/2+v[-1]/2+sum(v[1:-1]))
class RamanujanPerimeter(Scene):
 def construct(self):
    brand(self,"周长近似，不能写成等号","C024 · 固定 a=3，观察短半轴 b 的变化")
    b=ValueTracker(3);self.add(always_redraw(lambda:Ellipse(width=5.7,height=1.9*b.get_value(),color=BLUE).move_to([0,1.25,0])))
    self.add(Line([-2.85,1.25,0],[2.85,1.25,0],color=GRAY),fm('a=3',29).move_to([1.4,.95,0]))
    self.add(always_redraw(lambda:Line([0,1.25,0],[0,1.25+.95*b.get_value(),0],color=ORANGE)))
    self.add(txt('b =',27).move_to([-1,-2.3,0]));num=DecimalNumber(3,num_decimal_places=2,font_size=32,color=ORANGE).move_to([.2,-2.3,0]);num.add_updater(lambda m:m.set_value(b.get_value()));self.add(num)
    self.add(fm(r'h=\left(\frac{a-b}{a+b}\right)^2',32).move_to([0,-3.25,0]),fm(r'L_R=\pi(a+b)\left(1+\frac{3h}{10+\sqrt{4-3h}}\right)',30).move_to([0,-4.3,0]))
    note=txt('a=b：圆周长恰好等于 2πa',25).move_to([0,-5.25,0]);self.add(note);self.wait(2)
    for value in [2.,1.]:
      self.remove(note);self.play(b.animate.set_value(value),run_time=3)
      lr=approx(3,value);ref=reference(3,value)
      note=VGroup(txt(f'近似值 {lr:.6f}；数值参考 {ref:.6f}',23),txt('数值接近，仍须使用近似号 ≈',24)).arrange(DOWN,buff=.18).move_to([0,-5.15,0]);self.add(note);self.wait(2)
    self.remove(note);self.play(b.animate.set_value(3),run_time=3);self.add(txt('仅圆特例取精确等号；其余按题意取近似',24).move_to([0,-5.2,0]));self.wait(1)
