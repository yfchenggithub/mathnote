from manim import *
import math
from model import value,visible_domain,category,slope_at_common_point

config.background_color='#F7F8FA'
config.frame_width=9
config.frame_height=16
INK='#213044';BLUE='#2778BD';ORANGE='#CD6031';VIOLET='#8055B2';TEAL='#158068';GRAY='#A7B4C2';GOLD='#B77D12'

def txt(s,size=25):return Text(s,font='Microsoft YaHei',font_size=size,color=INK)

class F038BaseClockwise(Scene):
    def construct(self):
        beta=ValueTracker(math.log(4));direction=ValueTracker(-1)
        base=lambda:math.exp(beta.get_value())
        def col():
            t=beta.get_value()/math.log(2)
            if t>=1:return interpolate_color(ManimColor(BLUE),ManimColor(VIOLET),min(1,t-1))
            if t>=-1:return interpolate_color(ManimColor(ORANGE),ManimColor(BLUE),(t+1)/2)
            return interpolate_color(ManimColor(TEAL),ManimColor(ORANGE),max(0,t+2))
        self.add(txt('底数减小，曲线怎样改变？',30).move_to([0,7,0]))
        self.add(MathTex(r'y=a^x,\quad a>0',font_size=35,color=INK).move_to([-1.3,6.1,0]))
        self.add(MathTex(r'a\approx',font_size=34,color=INK).move_to([1.5,6.1,0]))
        decimal=DecimalNumber(4,num_decimal_places=2,font_size=34,color=INK).move_to([2.7,6.1,0])
        decimal.add_updater(lambda m:m.set_value(base()));self.add(decimal)
        self.add(always_redraw(lambda:txt(category(base()),25).move_to([0,5.2,0])))
        ax=Axes(x_range=[-2.4,2.4,1],y_range=[0,5,1],x_length=5.76,y_length=6,axis_config={'color':GRAY,'stroke_width':2,'tip_width':.12,'tip_height':.16}).move_to([0,1.4,0])
        self.add(ax)
        for x in [-2,-1,0,1,2]:self.add(MathTex(str(x),font_size=25,color=INK).move_to(ax.c2p(x,-.25)))
        for y in [1,4]:self.add(MathTex(str(y),font_size=25,color=INK).next_to(ax.c2p(0,y),LEFT,buff=.16))
        self.add(MathTex('x',font_size=27,color=INK).next_to(ax.c2p(2.4,0),RIGHT,buff=.08),MathTex('y',font_size=27,color=INK).next_to(ax.c2p(0,5),UP,buff=.08))
        self.add(DashedLine(ax.c2p(-2.3,1),ax.c2p(2.3,1),color=GRAY,stroke_width=1))
        self.add(always_redraw(lambda:ax.plot(lambda x:value(base(),x),x_range=[*visible_domain(base()),.025],color=col(),stroke_width=3.5)))
        self.add(always_redraw(lambda:DashedLine(ax.c2p(-.65,1-.65*slope_at_common_point(base())),ax.c2p(.65,1+.65*slope_at_common_point(base())),color=INK,stroke_width=2,dash_length=.09)))
        for x,c in [(-1,ORANGE),(1,BLUE)]:
            self.add(always_redraw(lambda x=x,c=c:VGroup(DashedLine(ax.c2p(x,0),ax.c2p(x,value(base(),x)),color=c,stroke_width=1.3),Dot(ax.c2p(x,value(base(),x)),color=c,radius=.075))))
        self.add(Dot(ax.c2p(0,1),color=GOLD,radius=.085))
        for x,c,formula,pos in [(-1,ORANGE,r'x=-1:\;1/a\approx',-1.95),(1,BLUE,r'x=1:\;a\approx',1.95)]:
            self.add(MathTex(formula,font_size=31,color=c).move_to([pos,-2.7,0]))
            num=DecimalNumber(value(4,x),num_decimal_places=2,font_size=33,color=c).move_to([pos,-3.4,0]);num.add_updater(lambda m,x=x:m.set_value(value(base(),x)));self.add(num)
        self.add(always_redraw(lambda:txt('底数减小：左侧升高，右侧降低' if direction.get_value()<0 else '回放：底数增大，变化方向相反',25).move_to([0,-4.25,0])))
        self.add(always_redraw(lambda:txt('短虚线是切线：方向顺时针改变' if direction.get_value()<0 else '短切线方向随之逆时针恢复',23).move_to([0,-5.05,0])))
        self.add(txt('公共点始终为(0,1)；数值保留两位小数',20).move_to([0,-5.8,0]))
        self.add(txt('查结论 · 看图解 · 学证明｜知树 App',23).move_to([0,-6.65,0]),txt('公众号 ok-shuxue｜获取入口',21).move_to([0,-7.2,0]))
        self.wait(1.3)
        for a in [2,1,.5,.25]:
            self.play(beta.animate.set_value(math.log(a)),run_time=2)
            self.wait(1.1 if a!=1 else 1.4)
        direction.set_value(1)
        self.play(beta.animate.set_value(math.log(4)),run_time=3.5)
        self.wait(.6)
        direction.set_value(-1)
        self.wait(.7,frozen_frame=False)
