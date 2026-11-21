from manim import *
from model import f,state
config.frame_width=9;config.frame_height=16;config.background_color="#F7F8FA"
INK="#213044";BLUE="#2778BD";ORANGE="#CD6031";GRAY="#A7B4C2";GREEN="#158068";PURPLE="#8054AC"
class F023MovingComparison(Scene):
 def construct(self):
  self.add(Text("中点一直变，两侧仍相隔4且同高",font="Microsoft YaHei",font_size=28,color=INK).move_to([0,7,0]),MathTex(r"f(t)=\sin\frac{\pi t}{2},\qquad a=2",font_size=38,color=INK).move_to([0,6.05,0]))
  self.add(Text("查结论 · 看图解 · 学证明｜知树 App",font="Microsoft YaHei",font_size=22,color=INK).move_to([0,-6.65,0]),Text("公众号 ok-shuxue｜获取入口",font="Microsoft YaHei",font_size=20,color=INK).move_to([0,-7.2,0]))
  a=Axes(x_range=[-2.4,6.4,2],y_range=[-1.6,1.6,1],x_length=6.3,y_length=5.3,axis_config={"color":GRAY,"stroke_width":2}).move_to([0,1.15,0]);a.add_coordinates([-2,2,4,6],[])
  for q in [-1,1]:self.add(Line(a.c2p(-2.4,q),a.c2p(6.4,q),color=GRAY,stroke_opacity=.25,stroke_width=1),MathTex(str(q),font_size=25,color=INK).next_to(a.c2p(-2.4,q),LEFT,.12))
  for m in a.get_family():
   if isinstance(m,SingleStringMathTex):m.set_color(INK)
  self.add(a,Text("绿色点：正在变化的比较中点 x",font="Microsoft YaHei",font_size=25,color=GREEN).move_to([0,4.75,0]));self.play(Create(a.plot(f,x_range=[-2.3,6.3],color=BLUE,stroke_width=4)),run_time=1.1)
  x=ValueTracker(.5)
  def moving():
   s=state(x.get_value());l,r,h=s['left'],s['right'],s['left_height'];out=VGroup(Line(a.c2p(l,h),a.c2p(r,h),color=ORANGE,stroke_width=3),Dot(a.c2p(l,h),color=ORANGE,radius=.09),Dot(a.c2p(r,h),color=ORANGE,radius=.09),Dot(a.c2p(s['center'],0),color=GREEN,radius=.1),DoubleArrow(a.c2p(l,-1.35),a.c2p(r,-1.35),buff=0,color=PURPLE,stroke_width=3));out.add(MathTex(r"4=2a",font_size=28,color=PURPLE).next_to(a.c2p(s['center'],-1.35),DOWN,.13));return out
  self.add(always_redraw(moving),MathTex(r"f(x-2)=f(x+2)",font_size=41,color=INK).move_to([0,-3.15,0]),Text("两个输入相差4，高度始终相同",font="Microsoft YaHei",font_size=26,color=INK).move_to([0,-4.25,0]),Text("关系对所有 x 成立，才能保证周期4",font="Microsoft YaHei",font_size=24,color=INK).move_to([0,-5.3,0]))
  self.wait(1.5);self.play(x.animate.set_value(3.5),run_time=3.3);self.wait(1.3);self.play(x.animate.set_value(1.5),run_time=2.7);self.wait(1.2);self.play(x.animate.set_value(.5),run_time=2.5);self.wait(1.4)
