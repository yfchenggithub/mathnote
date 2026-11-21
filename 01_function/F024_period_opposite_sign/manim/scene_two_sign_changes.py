from manim import *
from model import f,state
config.frame_width=9;config.frame_height=16;config.background_color="#F7F8FA"
INK="#213044";BLUE="#2778BD";ORANGE="#CD6031";GRAY="#A7B4C2";PURPLE="#8054AC"
class F024TwoSignChanges(Scene):
 def construct(self):
  self.add(Text("走一步变号，走两步还原",font="Microsoft YaHei",font_size=31,color=INK).move_to([0,7,0]),MathTex(r"f(t)=\sin\frac{\pi t}{2},\quad a=2",font_size=38,color=INK).move_to([0,6.05,0]))
  self.add(Text("查结论 · 看图解 · 学证明｜知树 App",font="Microsoft YaHei",font_size=22,color=INK).move_to([0,-6.65,0]),Text("公众号 ok-shuxue｜获取入口",font="Microsoft YaHei",font_size=20,color=INK).move_to([0,-7.2,0]))
  ax=Axes(x_range=[-.8,7.6,2],y_range=[-1.5,1.5,1],x_length=6.5,y_length=4.7,axis_config={"color":GRAY,"stroke_width":2}).move_to([0,1.1,0])
  for m in ax.get_family():
   if isinstance(m,SingleStringMathTex):m.set_color(INK)
  self.add(ax)
  for t in [0,2,4,6]:self.add(Line(ax.c2p(t,-1.5),ax.c2p(t,1.5),color=GRAY,stroke_opacity=.18,stroke_width=1),MathTex(str(t),font_size=25,color=INK).move_to(ax.c2p(t,1.7)))
  for q in [-1,1]:self.add(Line(ax.c2p(-.8,q),ax.c2p(7.6,q),color=GRAY,stroke_opacity=.25,stroke_width=1),MathTex(str(q),font_size=25,color=INK).next_to(ax.c2p(-.8,q),LEFT,.12))
  self.add(Text("蓝点同高，橙点是它们的相反高度",font="Microsoft YaHei",font_size=25,color=INK).move_to([0,4.6,0]))
  self.play(Create(ax.plot(f,x_range=[-.7,7.5],color=BLUE,stroke_width=3)),run_time=1)
  x=ValueTracker(.6)
  def moving():
   s=state(x.get_value());p,q,r=s;v=VGroup(Line(ax.c2p(*p),ax.c2p(*r),color=BLUE,stroke_width=2,stroke_opacity=.4))
   for i,((t,y),c) in enumerate(zip(s,[BLUE,ORANGE,BLUE])):
    v.add(Line(ax.c2p(t,0),ax.c2p(t,y),color=c,stroke_width=4),Dot(ax.c2p(t,y),color=c,radius=.09),MathTex(["x","x+2","x+4"][i],font_size=27,color=c).move_to(ax.c2p(t,-1.9)))
   return v
  self.add(always_redraw(moving),MathTex(r"f(x+2)=-f(x)",font_size=39,color=ORANGE).move_to([0,-2.8,0]),MathTex(r"f(x+4)=-[-f(x)]=f(x)",font_size=39,color=BLUE).move_to([0,-3.8,0]),Text("任意起点都成立：4是一个正周期",font="Microsoft YaHei",font_size=25,color=INK).move_to([0,-5,0]),Text("这一步尚不能保证周期最小",font="Microsoft YaHei",font_size=23,color=INK).move_to([0,-5.7,0]))
  self.wait(1.5);self.play(x.animate.set_value(2.6),run_time=3);self.wait(1.3);self.play(x.animate.set_value(-.4),run_time=3.5);self.wait(1.3);self.play(x.animate.set_value(.6),run_time=2);self.wait(1.4)
