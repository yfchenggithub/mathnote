from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from model import state
from manim import *
import numpy as np
config.frame_width=9;config.frame_height=16
BG='#F7F8FA';INK='#213044';BLUE='#2778BD';ORANGE='#CD6031';GRAY='#A7B4C2';PURPLE='#8055B2'
class F013DoubleReversal(Scene):
 def construct(self):
  self.camera.background_color=BG
  def tx(s,size=30,color=INK,pos=(0,0,0),width=8):
   z=Text(s,font='Microsoft YaHei',font_size=size,color=color)
   if z.width>width:z.scale_to_fit_width(width)
   return z.move_to(pos)
  self.add(tx('两次递减，为什么反而递增？',36,pos=(0,7.1,0)),tx('同一对数，连续经过两个函数',28,pos=(0,6.2,0)))
  self.add(tx('查结论 · 看图解 · 学证明｜知树 App',28,pos=(0,-6.7,0)),tx('公众号 ok-shuxue｜获取入口',25,pos=(0,-7.28,0)))
  rows=[]
  for y,n in [(4.7,'x'),(1.6,'t'),(-1.5,'y')]:
   line=NumberLine(x_range=[0,10,1],length=7.2,include_ticks=False,include_numbers=False,color=GRAY,stroke_width=1.6,include_tip=True,tip_width=.1,tip_height=.12).move_to([0,y,0]);rows.append(line)
   self.add(line,tx(n,27,pos=(-4.05,y,0)),tx('0',21,GRAY,pos=line.n2p(0)+DOWN*.3),tx('10',21,GRAY,pos=line.n2p(10)+DOWN*.3))
  fixed=[rows[i].n2p(v) for i,v in enumerate([2,8,2])]
  self.add(VGroup(*[Line(fixed[i],fixed[i+1],color=BLUE,stroke_width=2.6) for i in range(2)]),VGroup(*[Dot(p,color=BLUE,radius=.08) for p in fixed]))
  tr=ValueTracker(3)
  def points():return [rows[i].n2p(v) for i,v in enumerate(state(tr.get_value())['orange'])]
  moving=always_redraw(lambda:VGroup(*[Line(points()[i],points()[i+1],color=ORANGE,stroke_width=3) for i in range(2)],*[Dot(p,color=ORANGE,radius=.085) for p in points()]))
  self.add(moving)
  self.add(MathTex(r't=10-x',font_size=40,color=INK).move_to([2.8,3.2,0]),tx('内层递减',24,PURPLE,pos=(2.8,2.55,0)))
  self.add(MathTex(r'y=10-t',font_size=40,color=INK).move_to([2.8,.1,0]),tx('外层递减',24,PURPLE,pos=(2.8,-.55,0)))
  for y,s in [(5.45,r'x_1<x_2'),(2.35,r't_1>t_2'),(-.75,r'y_1<y_2')]:self.add(MathTex(s,font_size=43,color=INK).move_to([-2.6,y,0]))
  self.add(tx('蓝点：2 → 8 → 2',29,BLUE,pos=(0,-3.0,0)))
  read=always_redraw(lambda:tx('橙点 ≈ '+' → '.join(format(v,'.2f') for v in state(tr.get_value())['orange']),28,ORANGE,pos=(0,-3.8,0)))
  self.add(read,tx('第一次反转，再反转一次',29,pos=(0,-4.75,0)),tx('整体仍然随 x 的增大而增大',29,pos=(0,-5.55,0)))
  self.wait(1.5);self.play(tr.animate.set_value(7),run_time=4,rate_func=smooth);self.wait(1)
  self.play(tr.animate.set_value(3),run_time=4,rate_func=smooth);self.wait(1.5)
