from manim import *
from model import f,state
config.frame_width=9;config.frame_height=16;config.background_color="#F7F8FA"
INK="#213044";BLUE="#2778BD";ORANGE="#CD6031";GRAY="#A7B4C2"
class F025ReciprocalReturn(Scene):
 def construct(self):
  self.add(Text("倒数两次，高度回到原样",font="Microsoft YaHei",font_size=31,color=INK).move_to([0,7,0]),MathTex(r"f(t)=2^{\sin(\pi t)},\quad a=1",font_size=38,color=INK).move_to([0,6.05,0]))
  self.add(Text("查结论 · 看图解 · 学证明｜知树 App",font="Microsoft YaHei",font_size=22,color=INK).move_to([0,-6.65,0]),Text("公众号 ok-shuxue｜获取入口",font="Microsoft YaHei",font_size=20,color=INK).move_to([0,-7.2,0]))
  ax=Axes(x_range=[-.5,4.4,1],y_range=[-.5,2.6,.5],x_length=6.5,y_length=4.8,axis_config={"color":GRAY,"stroke_width":2}).move_to([0,1.1,0])
  self.add(ax)
  for t in [0,1,2,3,4]:self.add(Line(ax.c2p(t,-.4),ax.c2p(t,2.5),color=GRAY,stroke_opacity=.18,stroke_width=1),MathTex(str(t),font_size=25,color=INK).move_to(ax.c2p(t,2.8)))
  for q,lab in [(.5,r"\frac12"),(1,"1"),(2,"2")]:self.add(Line(ax.c2p(-.5,q),ax.c2p(4.4,q),color=GRAY,stroke_opacity=.25,stroke_width=1),MathTex(lab,font_size=25,color=INK).next_to(ax.c2p(-.5,q),LEFT,.12))
  self.add(Text("每隔1，两点高度的乘积始终为1",font="Microsoft YaHei",font_size=25,color=INK).move_to([0,4.65,0]))
  self.play(Create(ax.plot(f,x_range=[-.4,4.3],color=BLUE,stroke_width=3)),run_time=1)
  x=ValueTracker(.5)
  def moving():
   s=state(x.get_value());p,q,r=s;v=VGroup(Line(ax.c2p(*p),ax.c2p(*r),color=BLUE,stroke_width=2,stroke_opacity=.4))
   for i,((t,y),c) in enumerate(zip(s,[BLUE,ORANGE,BLUE])):
    v.add(Line(ax.c2p(t,0),ax.c2p(t,y),color=c,stroke_width=4),Dot(ax.c2p(t,y),color=c,radius=.09),MathTex(["x","x+1","x+2"][i],font_size=27,color=c).move_to(ax.c2p(t,-.85)))
   return v
  self.add(always_redraw(moving),MathTex(r"f(x+1)=\frac1{f(x)}",font_size=39,color=ORANGE).move_to([0,-2.85,0]),MathTex(r"f(x+2)=\frac1{1/f(x)}=f(x)",font_size=39,color=BLUE).move_to([0,-4,0]),Text("起点任意变化，两步后仍同高",font="Microsoft YaHei",font_size=25,color=INK).move_to([0,-5.2,0]),Text("示例处处为正；2是一个正周期",font="Microsoft YaHei",font_size=23,color=INK).move_to([0,-5.8,0]))
  self.wait(1.5);self.play(x.animate.set_value(1.8),run_time=3);self.wait(1.3);self.play(x.animate.set_value(-.2),run_time=3.5);self.wait(1.3);self.play(x.animate.set_value(.5),run_time=2);self.wait(1.4)
