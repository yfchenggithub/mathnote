from manim import *
from model import f,state
config.frame_width=9;config.frame_height=16;config.background_color="#F7F8FA"
INK="#213044";BLUE="#2778BD";ORANGE="#CD6031";GRAY="#A7B4C2";GREEN="#158068";PURPLE="#8054AC"
class F022FractionCycle(Scene):
 def construct(self):
  self.add(Text("同一个分式用两次，原值就回来了",font="Microsoft YaHei",font_size=28,color=INK).move_to([0,7,0]),MathTex(r"f(x+1)=\frac{f(x)+1}{f(x)-1}",font_size=39,color=INK).move_to([0,5.9,0]))
  self.add(Text("查结论 · 看图解 · 学证明｜知树 App",font="Microsoft YaHei",font_size=22,color=INK).move_to([0,-6.65,0]),Text("公众号 ok-shuxue｜获取入口",font="Microsoft YaHei",font_size=20,color=INK).move_to([0,-7.2,0]))
  a=Axes(x_range=[-.3,4.3,1],y_range=[0,4,1],x_length=6.3,y_length=4.8,axis_config={"color":GRAY,"stroke_width":2}).move_to([0,1.5,0]);a.add_coordinates([0,1,2,3,4],[])
  for q in [2,3]:self.add(Line(a.c2p(-.3,q),a.c2p(4.3,q),color=GRAY,stroke_opacity=.25,stroke_width=1),MathTex(str(q),font_size=26,color=INK).next_to(a.c2p(-.3,q),LEFT,.15))
  for m in a.get_family():
   if isinstance(m,SingleStringMathTex):m.set_color(INK)
  self.add(a)
  graph=VGroup()
  for k in range(4):
   y=f(k);c=BLUE if y==2 else ORANGE
   graph.add(Line(a.c2p(k,y),a.c2p(k+1,y),color=c,stroke_width=4),Dot(a.c2p(k,y),color=c,radius=.065),Circle(radius=.065,color=c,fill_color=config.background_color,fill_opacity=1,stroke_width=2).move_to(a.c2p(k+1,y)))
  graph.add(Dot(a.c2p(4,2),color=BLUE,radius=.065));self.play(Create(graph),run_time=1.2)
  self.add(Text("每段左端取到，右端不取到；按周期2延伸",font="Microsoft YaHei",font_size=23,color=INK).move_to([0,4.6,0]))
  t=ValueTracker(.25)
  def moving():
   s=state(t.get_value());out=VGroup()
   for (x,y),c in zip(s,[PURPLE,GREEN,PURPLE]):out.add(Dot(a.c2p(x,y),color=c,radius=.11),DashedLine(a.c2p(x,.8),a.c2p(x,y),color=c,stroke_opacity=.7))
   for j in range(2):out.add(Arrow(a.c2p(s[j][0],.5),a.c2p(s[j+1][0],.5),buff=.1,color=INK,stroke_width=2))
   return out
  self.add(always_redraw(moving),Text("对应位置向右加1；断点处的高度直接跳变",font="Microsoft YaHei",font_size=24,color=INK).move_to([0,-2.05,0]))
  l1=MathTex(r"2\ \longrightarrow\ 3\ \longrightarrow\ 2",font_size=45,color=INK).move_to([0,-3.15,0]);l2=MathTex(r"3\ \longrightarrow\ 2\ \longrightarrow\ 3",font_size=45,color=INK).move_to([0,-3.15,0]);l1.add_updater(lambda m:m.set_opacity(1 if f(t.get_value())==2 else 0));l2.add_updater(lambda m:m.set_opacity(1 if f(t.get_value())==3 else 0));l2.set_opacity(0);self.add(l1,l2,MathTex(r"f(x+2)=f(x)",font_size=43,color=PURPLE).move_to([0,-4.45,0]),Text("示例取值仅为2或3，分母始终非零",font="Microsoft YaHei",font_size=23,color=INK).move_to([0,-5.35,0]))
  self.wait(1.8);self.play(t.animate.set_value(.75),run_time=2.5);self.wait(1);self.play(t.animate.set_value(1.25),run_time=2.8);self.wait(1.8);self.play(t.animate.set_value(.25),run_time=2.8);self.wait(1.5)
