from manim import *
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from model import globally_strict_increasing
config.frame_width=9;config.frame_height=16
BG='#F7F8FA';INK='#213044';BLUE='#2778BD';ORANGE='#CD6031';GRAY='#A7B4C2';RED='#B64040';GREEN='#248477'
class F014MovingJoin(Scene):
 def construct(self):
  self.camera.background_color=BG
  def tx(s,size=30,color=INK,pos=(0,0,0),width=8):
   z=Text(s,font='Microsoft YaHei',font_size=size,color=color)
   if z.width>width:z.scale_to_fit_width(width)
   return z.move_to(pos)
  self.add(tx('每段都递增，整体就递增吗？',36,pos=(0,7.1,0)),tx('只改变右段高度，段内斜率始终为 1',27,pos=(0,6.3,0)))
  self.add(MathTex(r'f(x)=\begin{cases}x,&x\le0\\ x+c,&x>0\end{cases}',font_size=43,color=INK).move_to([0,5.0,0]))
  self.add(tx('查结论 · 看图解 · 学证明｜知树 App',28,pos=(0,-6.7,0)),tx('公众号 ok-shuxue｜获取入口',25,pos=(0,-7.28,0)))
  ax=Axes(x_range=[-3,3,1],y_range=[-5,5,1],x_length=5.1,y_length=8.5,axis_config={'color':GRAY,'stroke_width':1.5,'include_ticks':False,'tip_width':.1,'tip_height':.13}).move_to([0,-.1,0])
  self.add(ax,tx('x',25,GRAY,pos=ax.c2p(3,0)+RIGHT*.3),tx('y',25,GRAY,pos=ax.c2p(0,5)+UP*.2))
  c=ValueTracker(2)
  self.add(ax.plot(lambda x:x,x_range=[-3,0],color=BLUE,stroke_width=4),Dot(ax.c2p(0,0),radius=.085,color=BLUE),tx('实心：f(0)=0',24,BLUE,pos=(-2.45,-.5,0),width=3.0))
  right=always_redraw(lambda:ax.plot(lambda x:x+c.get_value(),x_range=[.002,3],color=ORANGE,stroke_width=4))
  ring=always_redraw(lambda:Circle(radius=.085,color=ORANGE,fill_color=BG,fill_opacity=1,stroke_width=2.5).move_to(ax.c2p(0,c.get_value())))
  height=always_redraw(lambda:DashedLine(ax.c2p(0,c.get_value()),ax.c2p(2.3,c.get_value()),color=ORANGE,stroke_width=1.4))
  self.add(right,height,ring,Dot(ax.c2p(0,0),radius=.07,color=BLUE))
  self.add(tx('空心：右段靠近的高度 L=c',24,ORANGE,pos=(0,-4.9,0)))
  read=always_redraw(lambda:tx('c '+chr(0x2248)+f' {c.get_value():+.2f}',31,INK,pos=(0,-4.3,0)))
  def status():
   v=c.get_value()
   if abs(v)<1e-7:return tx('接口取等，仍然严格递增',31,GREEN,pos=(0,-5.65,0))
   return tx('向上跳：整体严格递增' if globally_strict_increasing(v) else '向下跳：整体不递增',31,GREEN if v>=0 else RED,pos=(0,-5.65,0))
  self.add(read,always_redraw(status))
  self.wait(2);self.play(c.animate.set_value(0),run_time=2);self.wait(2);self.play(c.animate.set_value(-2),run_time=2);self.wait(2);self.play(c.animate.set_value(2),run_time=3);self.wait(2)
