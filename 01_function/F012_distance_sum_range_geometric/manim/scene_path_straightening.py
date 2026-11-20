from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from model import state,X0,MINIMUM
from manim import *
import numpy as np
config.frame_width=9;config.frame_height=16
BG='#F7F8FA';INK='#213044';BLUE='#2778BD';ORANGE='#CD6031';PURPLE='#8055B2';GOLD='#B77D12';GRAY='#A7B4C2'
class F012PathStraightening(Scene):
 def construct(self):
  self.camera.background_color=BG
  def tx(s,size=30,color=INK,pos=(0,0,0),width=8.0):
   z=Text(s,font='Microsoft YaHei',font_size=size,color=color)
   if z.width>width:z.scale_to_fit_width(width)
   return z.move_to(pos)
  title=tx('两个根号，怎样连成最短的路？',36,pos=(0,7.1,0))
  sub=tx('P 在横轴上移动，两段距离一起改变',28,pos=(0,6.15,0))
  footer=VGroup(tx('查结论 · 看图解 · 学证明｜知树 App',28,pos=(0,-6.7,0)),tx('公众号 ok-shuxue｜获取入口',25,pos=(0,-7.28,0)))
  axes=Axes(x_range=[-2,6,1],y_range=[-3,4,1],x_length=7.2,y_length=6.3,axis_config={'color':GRAY,'stroke_width':1.5,'include_ticks':False,'tip_width':.1,'tip_height':.12}).move_to([0,1.4,0])
  cp=axes.c2p;a=cp(1,-2);b=cp(3,3)
  ad=Dot(a,color=BLUE,radius=.075);bd=Dot(b,color=BLUE,radius=.075)
  labels=VGroup(tx('A(1,−2)',25,pos=a+np.array([-.5,-.45,0]),width=2),tx('B(3,3)',25,pos=b+np.array([.5,.4,0]),width=2),tx('x',25,pos=cp(6,0)+RIGHT*.2),tx('y',25,pos=cp(0,4)+UP*.2))
  direct=DashedLine(a,b,color=BLUE,stroke_width=2.4,dash_length=.1)
  tracker=ValueTracker(5)
  legs=always_redraw(lambda:VGroup(Line(a,cp(tracker.get_value(),0),color=ORANGE,stroke_width=4),Line(cp(tracker.get_value(),0),b,color=PURPLE,stroke_width=4)))
  pd=always_redraw(lambda:Dot(cp(tracker.get_value(),0),color=GOLD,radius=.085))
  pl=always_redraw(lambda:tx('P',25,color=GOLD,pos=cp(tracker.get_value(),0)+np.array([.25,-.35,0])))
  xread=always_redraw(lambda:tx('x ≈ '+format(tracker.get_value(),'.2f'),29,pos=(0,-2.7,0)))
  vals=always_redraw(lambda:VGroup(tx('AP ≈ '+format(state(tracker.get_value())['ap'],'.3f'),29,ORANGE,pos=(-1.8,-3.45,0),width=3.4),tx('PB ≈ '+format(state(tracker.get_value())['pb'],'.3f'),29,PURPLE,pos=(1.8,-3.45,0),width=3.4)))
  total=always_redraw(lambda:tx('总路程  AP + PB ≈ '+format(state(tracker.get_value())['sum'],'.3f'),31,pos=(0,-4.25,0)))
  formula=MathTex(r'AP+PB\ge AB=\sqrt{29}',font_size=38,color=INK).move_to([0,-5.1,0])
  note=tx('只有 P 在线段 AB 上，折线才成为直路',27,pos=(0,-5.85,0))
  self.add(title,sub,footer,axes,direct,ad,bd,labels,legs,pd,pl,xread,vals,total,formula,note)
  self.wait(1.5);self.play(tracker.animate.set_value(X0),run_time=3.0,rate_func=smooth);self.wait(1.5)
  self.play(tracker.animate.set_value(3.8),run_time=2.2,rate_func=smooth);self.wait(.6)
  self.play(tracker.animate.set_value(X0),run_time=2.2,rate_func=smooth);self.wait(1.5)
  self.play(tracker.animate.set_value(5),run_time=2.5,rate_func=smooth);self.wait(.8)
