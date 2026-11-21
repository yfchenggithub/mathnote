from manim import *
from model import inner,outer
config.frame_width=9
config.frame_height=16
config.background_color="#F7F8FA"
INK="#213044";BLUE="#2778BD";ORANGE="#CD6031";GRAY="#A7B4C2";GREEN="#158068"
class F018InnerEven(Scene):
    def construct(self):
        self.add(Text("内层先合并，外层收到同一个数",font="Microsoft YaHei",font_size=28,color=INK).move_to([0,7,0]),MathTex(r"g(x)=x^2,\qquad f(u)=2^u",font_size=34,color=INK).move_to([0,6.15,0]))
        self.add(Text("查结论 · 看图解 · 学证明｜知树 App",font="Microsoft YaHei",font_size=22,color=INK).move_to([0,-6.65,0]),Text("公众号 ok-shuxue｜获取入口",font="Microsoft YaHei",font_size=20,color=INK).move_to([0,-7.2,0]))
        a=Axes(x_range=[-1.6,1.6,1],y_range=[0,2.4,1],x_length=6,y_length=3.4,axis_config={"color":GRAY,"stroke_width":2}).move_to([0,2.7,0])
        z=Axes(x_range=[0,2.4,1],y_range=[0,5.5,1],x_length=6,y_length=3.4,axis_config={"color":GRAY,"stroke_width":2}).move_to([0,-2.3,0])
        a.add_coordinates([-1,1],[]);z.add_coordinates([1,2],[])
        for ax,values in [(a,[1,2]),(z,[1,2,4])]:
            for v in values:self.add(Line(ax.c2p(ax.x_range[0],v),ax.c2p(ax.x_range[1],v),color=GRAY,stroke_opacity=.3,stroke_width=1),MathTex(str(v),font_size=24,color=INK).next_to(ax.c2p(ax.x_range[0],v),LEFT,.12))
            for mob in ax.get_family():
                if isinstance(mob,SingleStringMathTex):mob.set_color(INK)
        self.add(a,z,Text("第一步：正负输入平方后同高",font="Microsoft YaHei",font_size=24,color=INK).move_to([0,5.05,0]),Text("第二步：外层只有一个输入 u",font="Microsoft YaHei",font_size=24,color=INK).move_to([0,.1,0]))
        self.play(Create(a.plot(inner,x_range=[-1.4,1.4],color=BLUE,stroke_width=4)),run_time=1)
        t=ValueTracker(.4)
        upper=always_redraw(lambda:VGroup(Dot(a.c2p(t.get_value(),inner(t.get_value())),color=ORANGE,radius=.08),Dot(a.c2p(-t.get_value(),inner(-t.get_value())),color=ORANGE,radius=.08),DashedLine(a.c2p(-t.get_value(),inner(t.get_value())),a.c2p(t.get_value(),inner(t.get_value())),color=ORANGE)))
        self.add(upper);self.wait(.8)
        self.play(Create(z.plot(outer,x_range=[0,2.2],color=GREEN,stroke_width=4)),run_time=1)
        target=always_redraw(lambda:Dot(z.c2p(inner(t.get_value()),outer(inner(t.get_value()))),color=ORANGE,radius=.1))
        formula=MathTex(r"f(g(-t))=f(g(t))",font_size=39,color=INK).move_to([0,-5.1,0])
        label=Text("u = t² =",font="Microsoft YaHei",font_size=24,color=INK).move_to([-.65,-5.9,0]);number=DecimalNumber(.16,num_decimal_places=2,font_size=30,color=ORANGE).next_to(label,RIGHT,.15);number.add_updater(lambda m:m.set_value(inner(t.get_value())))
        self.add(target,formula,label,number)
        self.play(t.animate.set_value(1),run_time=2.8);self.wait(1)
        self.play(t.animate.set_value(1.4),run_time=2.4);self.wait(1.2)
        self.play(t.animate.set_value(.4),run_time=3);self.wait(1.6)
