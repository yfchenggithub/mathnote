from manim import *
import numpy as np
from model import factor, product
config.frame_width=9
config.frame_height=16
config.background_color="#F7F8FA"
INK="#213044";BLUE="#2778BD";ORANGE="#CD6031";GRAY="#A7B4C2";GREEN="#158068"
class F017OddProduct(Scene):
    def construct(self):
        title=Text("两个负号，乘积左右同高",font="Microsoft YaHei",font_size=30,color=INK).move_to([0,7,0])
        sub=MathTex(r"f(x)=g(x)=x,\qquad f(x)g(x)=x^2",font_size=32,color=INK).move_to([0,6.1,0])
        foot1=Text("查结论 · 看图解 · 学证明｜知树 App",font="Microsoft YaHei",font_size=22,color=INK).move_to([0,-6.65,0])
        foot2=Text("公众号 ok-shuxue｜获取入口",font="Microsoft YaHei",font_size=20,color=INK).move_to([0,-7.2,0])
        self.add(title,sub,foot1,foot2)
        upper=Axes(x_range=[-2,2,1],y_range=[-2,2,1],x_length=6.1,y_length=4.0,axis_config={"color":GRAY,"include_tip":True,"stroke_width":2},tips=True).move_to([0,2.8,0])
        lower=Axes(x_range=[-2,2,1],y_range=[0,4,1],x_length=6.1,y_length=4.0,axis_config={"color":GRAY,"include_tip":True,"stroke_width":2},tips=True).move_to([0,-2.1,0])
        upper.add_coordinates([-1,0,1],[-1,0,1]);lower.add_coordinates([-1,0,1],[])
        for mob in [upper,lower]:
            for label in mob.get_family():
                if isinstance(label,SingleStringMathTex):label.set_color(INK)
        for value in [1,2,3]:
            self.add(Line(lower.c2p(-2,value),lower.c2p(2,value),color=GRAY,stroke_opacity=.35,stroke_width=1),MathTex(str(value),font_size=26,color=INK).next_to(lower.c2p(-2,value),LEFT,.12))
        topcurve=upper.plot(factor,x_range=[-1.75,1.75],color=BLUE,stroke_width=4)
        bottomcurve=lower.plot(product,x_range=[-1.75,1.75],color=GREEN,stroke_width=4)
        topcap=Text("因子：左右函数值互为相反数",font="Microsoft YaHei",font_size=24,color=INK).move_to([0,5.05,0])
        bottomcap=Text("乘积：左右高度始终相同",font="Microsoft YaHei",font_size=24,color=INK).move_to([0,.2,0])
        self.add(upper,lower,topcap,bottomcap)
        self.play(Create(topcurve),Create(bottomcurve),run_time=1.3)
        t=ValueTracker(.4)
        points=always_redraw(lambda:VGroup(Dot(upper.c2p(t.get_value(),factor(t.get_value())),color=ORANGE,radius=.08),Dot(upper.c2p(-t.get_value(),factor(-t.get_value())),color=ORANGE,radius=.08),Dot(lower.c2p(t.get_value(),product(t.get_value())),color=ORANGE,radius=.09),Dot(lower.c2p(-t.get_value(),product(-t.get_value())),color=ORANGE,radius=.09)))
        chord=always_redraw(lambda:DashedLine(lower.c2p(-t.get_value(),product(-t.get_value())),lower.c2p(t.get_value(),product(t.get_value())),color=ORANGE,stroke_width=3))
        formula=MathTex(r"(-t)(-t)=t^2=t\cdot t",font_size=40,color=INK).move_to([0,-5.15,0])
        tlabel=Text("t =",font_size=26,color=INK).move_to([-0.6,-5.9,0]);number=DecimalNumber(.4,num_decimal_places=2,font_size=30,color=ORANGE).next_to(tlabel,RIGHT,.15);number.add_updater(lambda m:m.set_value(t.get_value()))
        self.add(points,chord,formula,tlabel,number)
        self.wait(1)
        self.play(t.animate.set_value(1),run_time=2.5,rate_func=smooth);self.wait(1)
        self.play(t.animate.set_value(1.6),run_time=3,rate_func=smooth);self.wait(1)
        self.play(t.animate.set_value(.4),run_time=3.2,rate_func=smooth);self.wait(1.4)
