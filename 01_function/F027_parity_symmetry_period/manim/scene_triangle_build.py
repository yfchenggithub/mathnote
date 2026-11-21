from manim import *
from model import f,segment
config.frame_width=9;config.frame_height=16;config.background_color="#F7F8FA"
INK="#213044";BLUE="#2778BD";ORANGE="#CD6031";PURPLE="#8054AC";GRAY="#A7B4C2"
class F027TriangleBuild(Scene):
 def construct(self):
  self.add(Text("从一小段直线，拼出整条周期图",font="Microsoft YaHei",font_size=28,color=INK).move_to([0,7,0]),Text("奇函数，且关于 x=1 对称",font="Microsoft YaHei",font_size=27,color=INK).move_to([0,6.05,0]))
  self.add(Text("查结论 · 看图解 · 学证明｜知树 App",font="Microsoft YaHei",font_size=22,color=INK).move_to([0,-6.65,0]),Text("公众号 ok-shuxue｜获取入口",font="Microsoft YaHei",font_size=20,color=INK).move_to([0,-7.2,0]))
  a=Axes(x_range=[-.5,6.5,1],y_range=[-1.5,1.5,1],x_length=6.4,y_length=4.6,axis_config={"color":GRAY,"stroke_width":2}).move_to([0,1.25,0]);self.add(a)
  for x in range(7):self.add(MathTex(str(x),font_size=25,color=INK).move_to(a.c2p(x,-1.8)))
  for y in [-1,1]:self.add(Line(a.c2p(-.5,y),a.c2p(6.5,y),color=GRAY,stroke_opacity=.25,stroke_width=1),MathTex(str(y),font_size=25,color=INK).next_to(a.c2p(-.5,y),LEFT,.12))
  self.add(DashedLine(a.c2p(1,-1.4),a.c2p(1,1.4),color=PURPLE),MathTex('x=1',font_size=27,color=PURPLE).move_to(a.c2p(1,1.8)))
  status=Text("先画 0到1：y=x",font="Microsoft YaHei",font_size=26,color=INK).move_to([0,4.7,0]);self.add(status)
  for n in range(6):
   if n in [1,2,4]:
    label={1:"关于 x=1 翻折，得到1到2",2:"再向右移2、上下翻转，得到2到4",4:"继续按同样关系，得到4到6"}[n]
    self.remove(status);status=Text(label,font="Microsoft YaHei",font_size=24,color=INK).move_to([0,4.7,0]);self.add(status)
   p,q=segment(n);col=BLUE if n<2 else ORANGE if n<4 else BLUE
   self.play(Create(Line(a.c2p(*p),a.c2p(*q),color=col,stroke_width=5)),run_time=1.2);self.add(Dot(a.c2p(*q),color=col,radius=.07));self.wait(.6)
   if n==3:self.add(MathTex(r"f(x+2)=-f(x)",font_size=39,color=ORANGE).move_to([0,-2.7,0]));self.wait(1)
  self.add(MathTex(r"f(x+4)=f(x)",font_size=40,color=BLUE).move_to([0,-3.8,0]),Text("相隔2：高低相反；相隔4：整段还原",font="Microsoft YaHei",font_size=24,color=INK).move_to([0,-4.9,0]),Text("4是一个正周期，不保证最小",font="Microsoft YaHei",font_size=24,color=INK).move_to([0,-5.6,0]));self.wait(3)
