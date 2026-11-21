from manim import *
from model import value,vertex
config.frame_width=9;config.frame_height=16;config.background_color='#F7F8FA'
INK='#213044';BLUE='#2778BD';ORANGE='#CD6031';GRAY='#A7B4C2';PURPLE='#8054AC'
class F029FixedRoots(Scene):
 def construct(self):
  def txt(s,size=26):return Text(s,font='Microsoft YaHei',font_size=size,color=INK)
  self.add(txt('同样两个零点，仍有不同的抛物线',28).move_to([0,7,0]),MathTex(r'f(x)=a(x-1)(x-3),\quad a\ne0',font_size=38,color=INK).move_to([0,6.05,0]))
  self.add(txt('查结论 · 看图解 · 学证明｜知树 App',22).move_to([0,-6.65,0]),txt('公众号 ok-shuxue｜获取入口',20).move_to([0,-7.2,0]))
  ax=Axes(x_range=[-.4,4.4,1],y_range=[-4,4,1],x_length=6.6,y_length=5.4,axis_config={'color':GRAY,'stroke_width':2}).move_to([0,1.4,0]);self.add(ax)
  a=ValueTracker(1)
  graph=always_redraw(lambda:ax.plot(lambda x:value(x,a.get_value()),x_range=[.5,3.5],color=BLUE,stroke_width=3))
  dot=always_redraw(lambda:Dot(ax.c2p(*vertex(a.get_value())),color=ORANGE,radius=.09))
  self.add(DashedLine(ax.c2p(2,-3.8),ax.c2p(2,3.8),color=PURPLE,stroke_width=2),graph,dot)
  for x in [1,3]:self.add(Dot(ax.c2p(x,0),color=ORANGE,radius=.08),MathTex(str(x),font_size=30,color=INK).move_to(ax.c2p(x,-4.6)),DashedLine(ax.c2p(x,0),ax.c2p(x,-4.1),color=GRAY,stroke_width=1))
  self.add(txt('对称轴 x=2',24).move_to([0,4.55,0]))
  label=VGroup(MathTex('a=',font_size=36,color=INK),DecimalNumber(1,num_decimal_places=2,font_size=36,color=INK)).arrange(RIGHT,buff=.15).move_to([0,-2.4,0]);label[1].add_updater(lambda m:m.set_value(a.get_value()));self.add(label)
  self.add(MathTex(r'f(x)=a(x-2)^2-a',font_size=39,color=INK).move_to([0,-3.35,0]),MathTex(r'V=(2,-a)',font_size=38,color=ORANGE).move_to([0,-4.25,0]),txt('零点不变，顶点高度随 a 改变',25).move_to([0,-5.2,0]))
  sign=txt('a>0：开口向上',24).move_to([0,-5.8,0]);self.add(sign)
  self.wait(1);self.play(a.animate.set_value(2),run_time=2.5);self.wait(1);self.play(a.animate.set_value(.5),run_time=2);self.wait(.7)
  # Separate nonzero families. No interpolation through excluded a=0.
  self.play(FadeOut(graph),FadeOut(dot),FadeOut(sign),run_time=.4);a.set_value(-.5);graph=always_redraw(lambda:ax.plot(lambda x:value(x,a.get_value()),x_range=[.5,3.5],color=BLUE,stroke_width=3));dot=always_redraw(lambda:Dot(ax.c2p(*vertex(a.get_value())),color=ORANGE,radius=.09));sign=txt('a<0：开口向下',24).move_to([0,-5.8,0]);self.add(sign);self.play(FadeIn(graph),FadeIn(dot),run_time=.4)
  self.play(a.animate.set_value(-2),run_time=2.5);self.wait(1);self.play(a.animate.set_value(-1),run_time=1.5);self.wait(1.5)
