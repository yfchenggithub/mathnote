from manim import *
from model import f,state
config.frame_width=9;config.frame_height=16;config.background_color="#F7F8FA"
INK="#213044";BLUE="#2778BD";ORANGE="#CD6031";GRAY="#A7B4C2";PURPLE="#8054AC"
class F021FixedMidpoint(Scene):
 def construct(self):
  self.add(Text("端点在动，中点始终固定",font="Microsoft YaHei",font_size=29,color=INK).move_to([0,7,0]),MathTex(r"f(x)=(x-2)^3+3",font_size=39,color=INK).move_to([0,6.1,0]))
  self.add(Text("查结论 · 看图解 · 学证明｜知树 App",font="Microsoft YaHei",font_size=22,color=INK).move_to([0,-6.65,0]),Text("公众号 ok-shuxue｜获取入口",font="Microsoft YaHei",font_size=20,color=INK).move_to([0,-7.2,0]))
  a=Axes(x_range=[-.2,4.2,1],y_range=[-2,8,2],x_length=6.1,y_length=6.3,axis_config={"color":GRAY,"stroke_width":2}).move_to([0,1.2,0]);a.add_coordinates([1,2,3,4],[])
  for q in [0,2,4,6,8]:self.add(Line(a.c2p(-.2,q),a.c2p(4.2,q),color=GRAY,stroke_opacity=.25,stroke_width=1),MathTex(str(q),font_size=24,color=INK).next_to(a.c2p(-.2,q),LEFT,.12))
  for m in a.get_family():
   if isinstance(m,SingleStringMathTex):m.set_color(INK)
  self.add(a);self.play(Create(a.plot(f,x_range=[.35,3.65],color=BLUE,stroke_width=4)),run_time=1)
  self.add(DashedLine(a.c2p(-.2,3),a.c2p(4.2,3),color=PURPLE,stroke_opacity=.4))
  t=ValueTracker(.4)
  def moving():
   l,r=state(t.get_value());return VGroup(Line(a.c2p(*l),a.c2p(*r),color=ORANGE,stroke_width=3),Dot(a.c2p(*l),color=ORANGE,radius=.09),Dot(a.c2p(*r),color=ORANGE,radius=.09))
  self.add(always_redraw(moving),Dot(a.c2p(2,3),color=PURPLE,radius=.11),MathTex(r"C(2,3)",font_size=30,color=PURPLE).next_to(a.c2p(2,3),DOWN+RIGHT,.18))
  self.add(MathTex(r"\frac{(2-t)+(2+t)}2=2",font_size=37,color=INK).move_to([0,-3.1,0]),MathTex(r"\frac{f(2-t)+f(2+t)}2=3",font_size=37,color=INK).move_to([0,-4.25,0]))
  label=MathTex(r"t=",font_size=35,color=INK).move_to([-1,-5.3,0]);num=DecimalNumber(.4,num_decimal_places=2,font_size=35,color=ORANGE).next_to(label,RIGHT,.2);num.add_updater(lambda m:m.set_value(t.get_value()));self.add(label,num)
  self.wait(1.4);self.play(t.animate.set_value(1.5),run_time=3);self.wait(1.4);self.play(t.animate.set_value(1),run_time=2.4);self.wait(1.2);self.play(t.animate.set_value(.4),run_time=2.6);self.wait(1.5)
