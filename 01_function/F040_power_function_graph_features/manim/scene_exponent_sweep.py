from manim import *
from model import power,category
config.frame_width=9;config.frame_height=16;config.background_color='#F7F8FA'
INK='#213044';BLUE='#2778BD';ORANGE='#CD6031';PURPLE='#8054AC';GRAY='#A7B4C2';GOLD='#B77D12'
class F040ExponentSweep(Scene):
 def construct(self):
  def text(s,size=26,color=INK):return Text(s,font='Microsoft YaHei',font_size=size,color=color)
  self.add(text('改变指数，曲线都经过同一个点',28).move_to([0,7.0,0]),text('查结论 · 看图解 · 学证明｜知树 App',22).move_to([0,-6.65,0]),text('公众号 ok-shuxue｜获取入口',20).move_to([0,-7.2,0]))
  alpha=ValueTracker(-1)
  self.add(MathTex(r'y=x^\alpha,\quad x>0',font_size=39,color=INK).move_to([-1.3,6.05,0]))
  self.add(MathTex(r'\alpha\approx',font_size=34,color=INK).move_to([1.1,6.05,0]))
  number=DecimalNumber(-1,num_decimal_places=2,font_size=34,color=INK).move_to([2.5,6.05,0]);number.add_updater(lambda m:m.set_value(alpha.get_value()));self.add(number)
  self.add(always_redraw(lambda:text(category(alpha.get_value()),25).move_to([0,5.15,0])))
  ax=Axes(x_range=[0,2.4,.5],y_range=[0,5,1],x_length=6.6,y_length=5.6,axis_config={'color':GRAY,'stroke_width':2}).move_to([0,1.9,0]);self.add(ax)
  for x,lab in [(.5,r'\frac12'),(1,'1'),(2,'2')]:self.add(MathTex(lab,font_size=26,color=INK).move_to(ax.c2p(x,-.35)))
  self.add(MathTex('1',font_size=26,color=INK).next_to(ax.c2p(0,1),LEFT,buff=.18),MathTex('4',font_size=26,color=INK).next_to(ax.c2p(0,4),LEFT,buff=.18),DashedLine(ax.c2p(0,1),ax.c2p(2.3,1),color=GRAY,stroke_width=1),DashedLine(ax.c2p(1,0),ax.c2p(1,4.8),color=GRAY,stroke_width=1))
  self.add(always_redraw(lambda:ax.plot(lambda x:power(x,alpha.get_value()),x_range=[.23,2.2],color=BLUE,stroke_width=3)))
  for x,col in [(.5,ORANGE),(2,PURPLE)]:
   self.add(always_redraw(lambda x=x,col=col:VGroup(DashedLine(ax.c2p(x,0),ax.c2p(x,power(x,alpha.get_value())),color=col,stroke_width=1.4),Dot(ax.c2p(x,power(x,alpha.get_value())),color=col,radius=.08))))
  self.add(Dot(ax.c2p(1,1),color=GOLD,radius=.085))
  def value_row(formula,x,y,col):
   self.add(MathTex(formula,font_size=36,color=col).move_to([-1.1,y,0]))
   val=DecimalNumber(power(x,-1),num_decimal_places=2,font_size=36,color=col).move_to([1.65,y,0]);val.add_updater(lambda q:q.set_value(power(x,alpha.get_value())));self.add(val)
  value_row(r'(\frac12)^\alpha\approx',.5,-2.2,ORANGE);value_row(r'2^\alpha\approx',2,-3.15,PURPLE)
  self.add(text('系数固定为1，公共点始终是(1,1)',24).move_to([0,-4.25,0]),text('提高指数：1左降低，1右升高',25).move_to([0,-5.15,0]),text('显示数值保留两位小数',20).move_to([0,-5.85,0]))
  self.wait(1.5)
  for a,rt,hold in [(0,2,1),(.5,2,1),(1,2,1),(2,2,1.5),(-1,3,1)]:self.play(alpha.animate.set_value(a),run_time=rt);self.wait(hold)
