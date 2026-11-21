from manim import *
from model import f,state
config.frame_width=9;config.frame_height=16;config.background_color="#F7F8FA"
INK="#213044";BLUE="#2778BD";ORANGE="#CD6031";GRAY="#A7B4C2";GREEN="#158068"
class F019EvenDistance(Scene):
 def construct(self):
  self.add(Text("偶函数比大小：先比较到纵轴的距离",font="Microsoft YaHei",font_size=27,color=INK).move_to([0,7,0]),MathTex(r"f(x)=x^2,\quad b=1.5,\quad a=-t",font_size=35,color=INK).move_to([0,6.05,0]))
  self.add(Text("查结论 · 看图解 · 学证明｜知树 App",font="Microsoft YaHei",font_size=22,color=INK).move_to([0,-6.65,0]),Text("公众号 ok-shuxue｜获取入口",font="Microsoft YaHei",font_size=20,color=INK).move_to([0,-7.2,0]))
  a=Axes(x_range=[-3.2,3.2,1],y_range=[0,9,2],x_length=6.4,y_length=6.4,axis_config={"color":GRAY,"stroke_width":2}).move_to([0,1.1,0]);a.add_coordinates([-2,-1,1,2],[])
  for q in [2,4,6,8]:self.add(Line(a.c2p(-3.2,q),a.c2p(3.2,q),color=GRAY,stroke_opacity=.3,stroke_width=1),MathTex(str(q),font_size=24,color=INK).next_to(a.c2p(-3.2,q),LEFT,.12))
  for m in a.get_family():
   if isinstance(m,SingleStringMathTex):m.set_color(INK)
  self.add(a);self.play(Create(a.plot(f,x_range=[-2.9,2.9],color=BLUE,stroke_width=4)),run_time=1)
  self.add(Dot(a.c2p(1.5,f(1.5)),color=GREEN,radius=.1),Text("绿点：固定输入 b",font="Microsoft YaHei",font_size=24,color=GREEN).move_to([0,-2.8,0]))
  t=ValueTracker(2.6)
  moving=always_redraw(lambda:VGroup(Dot(a.c2p(-t.get_value(),f(t.get_value())),color=ORANGE,radius=.09),Dot(a.c2p(t.get_value(),f(t.get_value())),color=ORANGE,radius=.09),DashedLine(a.c2p(-t.get_value(),f(t.get_value())),a.c2p(t.get_value(),f(t.get_value())),color=ORANGE),DashedLine(a.c2p(-t.get_value(),0),a.c2p(-t.get_value(),f(t.get_value())),color=ORANGE),DashedLine(a.c2p(t.get_value(),0),a.c2p(t.get_value(),f(t.get_value())),color=ORANGE)))
  self.add(moving,MathTex(r"f(a)=f(|a|),\qquad |b|=1.5",font_size=36,color=INK).move_to([0,-3.6,0]))
  lab=MathTex(r"|a|=",font_size=36,color=INK).move_to([-1,-4.45,0]);num=DecimalNumber(2.6,num_decimal_places=2,font_size=34,color=ORANGE).next_to(lab,RIGHT,.2);num.add_updater(lambda m:m.set_value(t.get_value()));self.add(lab,num)
  status=always_redraw(lambda:Text("距离更远，函数值更大" if t.get_value()>1.5001 else ("距离更近，函数值更小" if t.get_value()<1.4999 else "距离相同，函数值相同"),font="Microsoft YaHei",font_size=26,color=INK).move_to([0,-5.35,0]));self.add(status)
  self.wait(1.5);self.play(t.animate.set_value(1.5),run_time=3);self.wait(1.4);self.play(t.animate.set_value(1),run_time=2.4);self.wait(1.2);self.play(t.animate.set_value(2.6),run_time=3);self.wait(1.5)
