from manim import *
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from model import pairs,even,odd
config.frame_width=9;config.frame_height=16
BG='#F7F8FA';INK='#213044';BLUE='#2778BD';ORANGE='#CD6031';GRAY='#A7B4C2';TEAL='#248477'
class F015SymmetryPartners(Scene):
 def construct(self):
  self.camera.background_color=BG
  def tx(s,size=30,color=INK,pos=(0,0,0),width=8):
   z=Text(s,font='Microsoft YaHei',font_size=size,color=color)
   if z.width>width:z.scale_to_fit_width(width)
   return z.move_to(pos)
  self.add(tx('奇偶性：每个点都要有伙伴',36,pos=(0,7.1,0)),tx('定义域均为 R：先配输入，再比输出',28,pos=(0,6.35,0)))
  self.add(tx('查结论 · 看图解 · 学证明｜知树 App',28,pos=(0,-6.7,0)),tx('公众号 ok-shuxue｜获取入口',25,pos=(0,-7.28,0)))
  t=ValueTracker(.5)
  ae=Axes(x_range=[-2,2,1],y_range=[-.25,2.75,1],x_length=4,y_length=3,axis_config={'color':GRAY,'include_ticks':False,'stroke_width':1.3,'tip_width':.09,'tip_height':.12}).move_to([0,3.5,0])
  ao=Axes(x_range=[-2,2,1],y_range=[-3.5,3.5,1],x_length=3.4,y_length=5.95,axis_config={'color':GRAY,'include_ticks':False,'stroke_width':1.3,'tip_width':.09,'tip_height':.12}).move_to([0,-2.65,0])
  # Both coordinate systems use equal horizontal and vertical unit lengths.
  self.add(ae,ae.plot(even,x_range=[-1.65,1.65],color=BLUE,stroke_width=3),ao,ao.plot(odd,x_range=[-1.5,1.5],color=TEAL,stroke_width=3))
  self.add(MathTex(r'y=x^2:\quad f(-x)=f(x)',font_size=40,color=BLUE).move_to([0,5.7,0]),MathTex(r'y=x^3:\quad g(-x)=-g(x)',font_size=40,color=TEAL).move_to([0,1.0,0]))
  for ax in (ae,ao):
   self.add(tx('x',24,GRAY,pos=ax.c2p(2,0)+RIGHT*.3),tx('y',24,GRAY,pos=ax.c2p(0,ax.y_range[1])+UP*.15))
  def geometry():
   ps=pairs(t.get_value());ep=[ae.c2p(*p) for p in ps['even']];op=[ao.c2p(*p) for p in ps['odd']]
   return VGroup(DashedLine(*ep,color=ORANGE,stroke_width=1.5),Line(*op,color=ORANGE,stroke_width=1.5),*[Dot(p,radius=.075,color=ORANGE) for p in ep+op])
  self.add(always_redraw(geometry))
  self.add(tx('左右换位，高度相同',25,BLUE,pos=(0,1.7,0)),tx('左右换位，高度互为相反数',25,TEAL,pos=(0,-6.05,0)))
  def labels():
   v=t.get_value();return VGroup(tx('x '+chr(0x2248)+f' {v:.2f}',25,pos=(3.25,4.65,0),width=2.2),tx(chr(0x2212)+'x '+chr(0x2248)+f' {-v:.2f}',25,pos=(-3.2,4.65,0),width=2.5))
  self.add(always_redraw(labels))
  self.wait(2);self.play(t.animate.set_value(1.5),run_time=4,rate_func=smooth);self.wait(2);self.play(t.animate.set_value(.5),run_time=4,rate_func=smooth);self.wait(2)
