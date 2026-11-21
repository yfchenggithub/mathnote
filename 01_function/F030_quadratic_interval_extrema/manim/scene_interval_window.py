from manim import *
from model import f,extrema
config.frame_width=9;config.frame_height=16;config.background_color='#F7F8FA'
INK='#213044';BLUE='#2778BD';ORANGE='#CD6031';TEAL='#008B86';GRAY='#A7B4C2';PURPLE='#8054AC'
class F030IntervalWindow(Scene):
 def construct(self):
  def txt(s,size=26):return Text(s,font='Microsoft YaHei',font_size=size,color=INK)
  self.add(txt('同一条抛物线，允许区间决定最值',28).move_to([0,7,0]),MathTex(r'f(x)=(x-2)^2+1',font_size=40,color=INK).move_to([0,6.05,0]))
  self.add(txt('查结论 · 看图解 · 学证明｜知树 App',22).move_to([0,-6.65,0]),txt('公众号 ok-shuxue｜获取入口',20).move_to([0,-7.2,0]))
  ax=Axes(x_range=[-.5,4.5,1],y_range=[0,6,1],x_length=6.5,y_length=4.5,axis_config={'color':GRAY,'stroke_width':2}).move_to([0,2.25,0]);self.add(ax,ax.plot(f,x_range=[-.15,4.15],color=GRAY,stroke_width=2),DashedLine(ax.c2p(2,0),ax.c2p(2,5.7),color=PURPLE,stroke_width=2))
  for x in [0,1,2,3,4]:self.add(MathTex(str(x),font_size=26,color=INK).move_to(ax.c2p(x,-.4)))
  self.add(txt('蓝色粗线：允许段；灰色：区间外参考',23).move_to([0,4.85,0]))
  m=ValueTracker(0);n=ValueTracker(4)
  def moving():
   l,r=m.get_value(),n.get_value();e=extrema(l,r)
   group=VGroup(ax.plot(f,x_range=[l,r],color=BLUE,stroke_width=5),Line(ax.c2p(l,-.9),ax.c2p(r,-.9),color=BLUE,stroke_width=5),Dot(ax.c2p(e['nearest'],e['minimum']),radius=.10,color=TEAL))
   for x in e['farthest']:group.add(Dot(ax.c2p(x,f(x)),radius=.10,color=ORANGE))
   for x in [l,r]:group.add(DashedLine(ax.c2p(x,-.9),ax.c2p(x,f(x)),color=GRAY,stroke_width=1))
   return group
  self.add(always_redraw(moving))
  def number_row(prefix,func,y,color=INK):
   lab=MathTex(prefix,font_size=34,color=color).move_to([-1.5,y,0]);num=DecimalNumber(func(),num_decimal_places=2,font_size=34,color=color).move_to([1.15,y,0]);num.add_updater(lambda q:q.set_value(func()));self.add(lab,num)
  number_row('m=',lambda:m.get_value(),-1.3);number_row('n=',lambda:n.get_value(),-2.0)
  number_row(r'f_{\min}\approx',lambda:extrema(m.get_value(),n.get_value())['minimum'],-2.9,TEAL)
  number_row(r'f_{\max}\approx',lambda:extrema(m.get_value(),n.get_value())['maximum'],-3.7,ORANGE)
  self.add(txt('青点：最近位置；橙点：最远端点',24).move_to([0,-4.4,0]),txt('顶点在区间外，就不能选顶点',25).move_to([0,-5.2,0]),txt('演示改变区间；数值保留两位小数',21).move_to([0,-5.85,0]))
  self.wait(1.5);self.play(m.animate.set_value(3),run_time=3);self.wait(1.5);self.play(m.animate.set_value(0),n.animate.set_value(1),run_time=3.5);self.wait(1.5);self.play(n.animate.set_value(4),run_time=3);self.wait(1.5)
