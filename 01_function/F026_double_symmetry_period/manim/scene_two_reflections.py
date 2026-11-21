from manim import *
from model import f,state
config.frame_width=9;config.frame_height=16;config.background_color="#F7F8FA"
INK="#213044";BLUE="#2778BD";ORANGE="#CD6031";PURPLE="#8054AC";GRAY="#A7B4C2"
class F026TwoReflections(Scene):
 def construct(self):
  self.add(Text("两次照镜子，横向移动多少？",font="Microsoft YaHei",font_size=29,color=INK).move_to([0,7,0]),MathTex(r"f(t)=\cos\frac{\pi t}{2}",font_size=41,color=INK).move_to([0,6.05,0]))
  self.add(Text("查结论 · 看图解 · 学证明｜知树 App",font="Microsoft YaHei",font_size=22,color=INK).move_to([0,-6.65,0]),Text("公众号 ok-shuxue｜获取入口",font="Microsoft YaHei",font_size=20,color=INK).move_to([0,-7.2,0]))
  a=Axes(x_range=[-1.6,5.6,1],y_range=[-1.6,1.6,1],x_length=6.4,y_length=4.7,axis_config={"color":GRAY,"stroke_width":2}).move_to([0,1.2,0]);self.add(a)
  for t in [0,2]:self.add(DashedLine(a.c2p(t,-1.5),a.c2p(t,1.5),color=PURPLE,stroke_width=2),MathTex(f"x={t}",font_size=28,color=PURPLE).move_to(a.c2p(t,1.9)))
  for q in [-1,1]:self.add(MathTex(str(q),font_size=25,color=INK).next_to(a.c2p(-1.6,q),LEFT,.12))
  self.play(Create(a.plot(f,x_range=[-1.5,5.5],color=BLUE,stroke_width=3)),run_time=1)
  x=ValueTracker(.6)
  def marks():
   p,q,r=state(x.get_value());v=VGroup(Line(a.c2p(*q),a.c2p(*r),color=GRAY,stroke_width=2,stroke_opacity=.5))
   for point,lab,col,direction in [(p,'P',BLUE,UR),(q,'Q',ORANGE,UL),(r,'R',PURPLE,UR)]:v.add(Line(a.c2p(point[0],-1.6),a.c2p(*point),color=col,stroke_width=1,stroke_opacity=.2),Dot(a.c2p(*point),color=col,radius=.09),MathTex(lab,font_size=28,color=col).move_to(a.c2p(point[0],-1.95)))
   return v
  self.add(always_redraw(marks),Text("两条轴相距2：对应三点始终同高",font="Microsoft YaHei",font_size=25,color=INK).move_to([0,4.75,0]),MathTex(r"x\ \longrightarrow\ -x\ \longrightarrow\ 4+x",font_size=38,color=INK).move_to([0,-2.7,0]),MathTex(r"f(4+x)=f(-x)=f(x)",font_size=39,color=BLUE).move_to([0,-3.8,0]),Text("横向总共移动4，是轴间距的两倍",font="Microsoft YaHei",font_size=25,color=INK).move_to([0,-4.9,0]),Text("任意起点都成立，4是一个正周期",font="Microsoft YaHei",font_size=24,color=INK).move_to([0,-5.65,0]))
  self.wait(1.5);self.play(x.animate.set_value(1.2),run_time=3);self.wait(1.3);self.play(x.animate.set_value(.3),run_time=3.5);self.wait(1.3);self.play(x.animate.set_value(.6),run_time=2);self.wait(1.4)
