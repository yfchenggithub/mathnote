from manim import *
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import model_infinity as m
config.frame_width=9
config.frame_height=16
BG='#F7F8FA'; INK='#213044'; MUTED='#526275'; BLUE='#2778BD'; ORANGE='#CD6031'; PURPLE='#8055B2'; GREEN='#158068'; AXIS='#A7B4C2'
def text(s,y,size=29,color=INK):
 obj=Text(s,font='Microsoft YaHei',font_size=size,color=color)
 if obj.width>7.9:obj.scale_to_fit_width(7.9)
 return obj.move_to([0,y,0])
def formula(s,y,size=36,color=INK):
 obj=MathTex(s,font_size=size,color=color)
 if obj.width>7.9:obj.scale_to_fit_width(7.9)
 return obj.move_to([0,y,0])
def numeric_row(label,tracker,fn,y,color=INK,places=3):
 lab=MathTex(label,font_size=34,color=color).move_to([-1.55,y,0])
 num=DecimalNumber(fn(tracker.get_value()),num_decimal_places=places,group_with_commas=False,font_size=34,color=color)
 num.move_to([1.5,y,0])
 num.add_updater(lambda obj:obj.set_value(fn(tracker.get_value())).move_to([1.5,y,0]))
 return VGroup(lab,num)
def make_axes(xr,yr,h,center,xnums,ynums):
 ax=Axes(x_range=xr,y_range=yr,x_length=7.0,y_length=h,tips=False,axis_config={'color':AXIS,'stroke_width':1.8,'include_ticks':True,'tick_size':.045}).move_to(center)
 labels=VGroup()
 for x in xnums:labels.add(MathTex(str(x),font_size=23,color=MUTED).next_to(ax.c2p(x,yr[0]),DOWN,buff=.12))
 for y in ynums:labels.add(MathTex(str(y),font_size=23,color=MUTED).next_to(ax.c2p(xr[0],y),LEFT,buff=.12))
 labels.add(MathTex('x',font_size=25,color=MUTED).next_to(ax.c2p(xr[1],yr[0]),RIGHT,buff=.1))
 return ax,labels
class F005InfinityRatio(Scene):
 def construct(self):
  self.camera.background_color=BG
  title=text('都趋向无穷，比值呢？',7.05,34)
  f_label=formula(r'f(x)=2x^2+3x+1',6.15,36,BLUE)
  g_label=formula(r'g(x)=x^2+1',5.4,36,ORANGE)
  brand=VGroup(text('查结论 · 看图解 · 学证明｜知树 App',-6.85,22,MUTED),text('公众号 ok-shuxue｜获取入口',-7.4,20,MUTED))
  self.add(title,f_label,g_label,brand)
  x=ValueTracker(2)
  ax,labels=make_axes([0,10,2],[0,250,50],4.8,[.2,1.6,0],[0,5,10],[0,100,200])
  curves=VGroup(ax.plot(m.numerator,x_range=[0,10],color=BLUE,stroke_width=3.5),ax.plot(m.denominator,x_range=[0,10],color=ORANGE,stroke_width=3.5))
  dots=always_redraw(lambda:VGroup(Dot(ax.c2p(x.get_value(),m.numerator(x.get_value())),color=BLUE,radius=.075),Dot(ax.c2p(x.get_value(),m.denominator(x.get_value())),color=ORANGE,radius=.075),DashedLine(ax.c2p(x.get_value(),0),ax.c2p(x.get_value(),m.numerator(x.get_value())),color=AXIS,stroke_width=1.5)))
  operation=text('先看函数值：分子、分母都在增大',4.55,27)
  rows=VGroup(numeric_row('x=',x,lambda v:v,-1.9,places=1),numeric_row('f(x)=',x,m.numerator,-2.75,BLUE,1),numeric_row('g(x)=',x,m.denominator,-3.6,ORANGE,1))
  infinity=formula(r'x\to+\infty:\quad f(x),\ g(x)\to+\infty',-4.65,34)
  note=text('“无穷比无穷”描述类型，还不是答案',-5.65,26,MUTED)
  first=VGroup(ax,labels,curves,dots,operation,rows,infinity,note)
  self.add(first);self.wait(1.5);self.play(x.animate.set_value(10),run_time=4,rate_func=linear);self.wait(1.5)
  dots.clear_updaters()
  for obj in rows:obj[1].clear_updaters()
  self.play(FadeOut(first),run_time=.45)
  x.set_value(10)
  ax2,labels2=make_axes([0,80,20],[1.95,2.75,.2],4.1,[.2,1.25,0],[0,20,40,60,80],[2,2.4,2.7])
  line=DashedLine(ax2.c2p(0,2),ax2.c2p(80,2),color=GREEN,stroke_width=2)
  ref=MathTex('2',font_size=26,color=GREEN).next_to(ax2.c2p(80,2),RIGHT,buff=.12)
  curves2=VGroup(ax2.plot(m.ratio,x_range=[4,80,.25],color=BLUE,stroke_width=3.4),DashedVMobject(ax2.plot(m.derivative_ratio,x_range=[4,80,.25],color=PURPLE,stroke_width=3.0),num_dashes=45))
  moving=always_redraw(lambda:VGroup(Dot(ax2.c2p(x.get_value(),m.ratio(x.get_value())),color=BLUE,radius=.075),Dot(ax2.c2p(x.get_value(),m.derivative_ratio(x.get_value())),color=PURPLE,radius=.075),DashedLine(ax2.c2p(x.get_value(),1.95),ax2.c2p(x.get_value(),m.ratio(x.get_value())),color=AXIS,stroke_width=1.3)))
  operation2=text('改看比值：两条曲线都靠近 2',4.55,29)
  legend=VGroup(MathTex(r'f/g',font_size=29,color=BLUE),MathTex(r"f'/g'",font_size=29,color=PURPLE)).arrange(RIGHT,buff=1.3).move_to([0,3.8,0])
  ratio_rows=VGroup(numeric_row('x=',x,lambda v:v,-1.7,places=1),numeric_row(r'\frac{f(x)}{g(x)}\approx',x,m.ratio,-2.6,BLUE,4),numeric_row(r"\frac{f'(x)}{g'(x)}\approx",x,m.derivative_ratio,-3.6,PURPLE,4))
  derivative=formula(r"\frac{f'(x)}{g'(x)}=\frac{4x+3}{2x}=2+\frac{3}{2x}\to2",-4.8,33,PURPLE)
  caveat=text('有限位置不必相等；比较的是极限',-5.75,26,MUTED)
  self.add(ax2,labels2,line,ref,curves2,moving,operation2,legend,ratio_rows,derivative,caveat)
  self.wait(1);self.play(x.animate.set_value(80),run_time=6,rate_func=linear);self.wait(1)
  conditions=text('本例：可导，分母导数非零，导数比有极限',-5.9,23,MUTED)
  result=formula(r'\lim_{x\to+\infty}\frac{2x^2+3x+1}{x^2+1}=2',-4.85,38,GREEN)
  self.play(FadeOut(derivative),FadeOut(caveat),run_time=.3)
  self.add(result,conditions)
  self.wait(3)
