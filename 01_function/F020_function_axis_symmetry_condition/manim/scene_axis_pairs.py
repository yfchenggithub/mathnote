from manim import *
from model import f,state
config.frame_width=9;config.frame_height=16;config.background_color="#F7F8FA"
INK="#213044";BLUE="#2778BD";ORANGE="#CD6031";GRAY="#A7B4C2";PURPLE="#8054AC"
class F020AxisPairs(Scene):
 def construct(self):
  self.add(Text("对称轴两侧：一样远，就一样高",font="Microsoft YaHei",font_size=28,color=INK).move_to([0,7,0]),MathTex(r"f(x)=(x-2)^2+1",font_size=38,color=INK).move_to([0,6.1,0]))
  self.add(Text("查结论 · 看图解 · 学证明｜知树 App",font="Microsoft YaHei",font_size=22,color=INK).move_to([0,-6.65,0]),Text("公众号 ok-shuxue｜获取入口",font="Microsoft YaHei",font_size=20,color=INK).move_to([0,-7.2,0]))
  a=Axes(x_range=[-.5,4.5,1],y_range=[0,5.5,1],x_length=6.2,y_length=6.2,axis_config={"color":GRAY,"stroke_width":2}).move_to([0,1.1,0]);a.add_coordinates([1,2,3,4],[])
  for q in [1,2,3,4,5]:self.add(Line(a.c2p(-.5,q),a.c2p(4.5,q),color=GRAY,stroke_opacity=.25,stroke_width=1),MathTex(str(q),font_size=24,color=INK).next_to(a.c2p(-.5,q),LEFT,.12))
  for m in a.get_family():
   if isinstance(m,SingleStringMathTex):m.set_color(INK)
  self.add(a,DashedLine(a.c2p(2,0),a.c2p(2,5.3),color=PURPLE),MathTex(r"x=2",font_size=29,color=PURPLE).next_to(a.c2p(2,5.3),UP,.2));self.play(Create(a.plot(f,x_range=[-.1,4.1],color=BLUE,stroke_width=4)),run_time=1)
  t=ValueTracker(.4)
  def moving():
   s=state(t.get_value());l,r,h=s['left'],s['right'],s['height']
   return VGroup(Dot(a.c2p(l,h),color=ORANGE,radius=.09),Dot(a.c2p(r,h),color=ORANGE,radius=.09),Line(a.c2p(l,h),a.c2p(r,h),color=ORANGE,stroke_width=3),DashedLine(a.c2p(l,0),a.c2p(l,h),color=ORANGE),DashedLine(a.c2p(r,0),a.c2p(r,h),color=ORANGE))
  self.add(always_redraw(moving),MathTex(r"(2-t)+(2+t)=4",font_size=37,color=INK).move_to([0,-3.1,0]),MathTex(r"f(2-t)=f(2+t)=t^2+1",font_size=36,color=INK).move_to([0,-4.1,0]))
  label=MathTex(r"t=",font_size=36,color=INK).move_to([-1,-5.1,0]);num=DecimalNumber(.4,num_decimal_places=2,font_size=35,color=ORANGE).next_to(label,RIGHT,.2);num.add_updater(lambda m:m.set_value(t.get_value()));self.add(label,num)
  self.wait(1.5);self.play(t.animate.set_value(1.9),run_time=3);self.wait(1.3);self.play(t.animate.set_value(1),run_time=2.5);self.wait(1.3);self.play(t.animate.set_value(.4),run_time=2.5);self.wait(1.5)
