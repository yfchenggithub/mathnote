from manim import *
from model import f,pair
config.frame_width=9;config.frame_height=16;config.background_color="#F7F8FA"
INK="#213044";BLUE="#2778BD";ORANGE="#CD6031";GRAY="#A7B4C2";PURPLE="#8054AC"
class F028CandidateAxis(Scene):
 def construct(self):
  self.add(Text("半个周期后，又出现一条对称轴",font="Microsoft YaHei",font_size=28,color=INK).move_to([0,7,0]),MathTex(r"f(x)=\cos(\pi x),\qquad T_0=2",font_size=38,color=INK).move_to([0,6.05,0]))
  self.add(Text("查结论 · 看图解 · 学证明｜知树 App",font="Microsoft YaHei",font_size=22,color=INK).move_to([0,-6.65,0]),Text("公众号 ok-shuxue｜获取入口",font="Microsoft YaHei",font_size=20,color=INK).move_to([0,-7.2,0]))
  ax=Axes(x_range=[-1.4,3.6,1],y_range=[-1.6,1.6,1],x_length=6.4,y_length=4.7,axis_config={"color":GRAY,"stroke_width":2}).move_to([0,1.2,0]);self.add(ax,ax.plot(f,x_range=[-1.3,3.5],color=BLUE,stroke_width=3))
  for n in [0,1,2,3]:self.add(MathTex(str(n),font_size=26,color=INK).move_to(ax.c2p(n,1.9)))
  self.add(Text("橙线：正在检验的候选位置 x=a",font="Microsoft YaHei",font_size=25,color=INK).move_to([0,4.75,0]))
  a=ValueTracker(0);t=ValueTracker(.4)
  def moving():
   p,q=pair(a.get_value(),t.get_value());v=VGroup(DashedLine(ax.c2p(a.get_value(),-1.5),ax.c2p(a.get_value(),1.5),color=ORANGE,stroke_width=3),Line(ax.c2p(*p),ax.c2p(*q),color=PURPLE,stroke_width=2))
   for point,label,col in [(p,'L',BLUE),(q,'R',ORANGE)]:v.add(Dot(ax.c2p(*point),color=col,radius=.09),MathTex(label,font_size=27,color=col).move_to(ax.c2p(point[0],-1.95)))
   return v
  self.add(always_redraw(moving),MathTex(r"f(a-t)\ \overset{?}{=}\ f(a+t)",font_size=38,color=INK).move_to([0,-2.8,0]),Text("轴在0、1、2：左右任意等距点都同高",font="Microsoft YaHei",font_size=24,color=INK).move_to([0,-3.9,0]),MathTex(r"\Delta a=1=\frac{T_0}{2}",font_size=38,color=PURPLE).move_to([0,-4.85,0]),Text("对称位置间隔1，函数周期却是2",font="Microsoft YaHei",font_size=24,color=INK).move_to([0,-5.65,0]))
  self.wait(1);self.play(t.animate.set_value(.75),run_time=1.5);self.play(t.animate.set_value(.4),run_time=1);self.play(a.animate.set_value(1),run_time=2.5);self.wait(1);self.play(t.animate.set_value(.2),run_time=1);self.play(t.animate.set_value(.75),run_time=1);self.play(t.animate.set_value(.4),run_time=.7);self.play(a.animate.set_value(2),run_time=2.5);self.wait(2.3)
