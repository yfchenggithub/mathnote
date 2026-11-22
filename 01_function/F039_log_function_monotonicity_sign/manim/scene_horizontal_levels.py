from manim import *
from model import log_value,paired_bases
config.background_color='#F7F8FA'
config.frame_width=9
config.frame_height=16
INK='#213044';BLUE='#2778BD';ORANGE='#CD6031';GRAY='#A7B4C2';GOLD='#B77D12'
def txt(s,size=24):return Text(s,font='Microsoft YaHei',font_size=size,color=INK)

class F039HorizontalLevels(Scene):
    def construct(self):
        large=ValueTracker(2);direction=ValueTracker(1)
        self.add(txt('同样向右，底数却反着变化',30).move_to([0,7,0]))
        self.add(MathTex(r'y=\log_a x,\quad a>0,\ a\ne1,\ x>0',font_size=30,color=INK).move_to([0,6.15,0]))
        self.add(txt('沿着水平线 y=1 与 y=-1 观察',24).move_to([0,5.25,0]))
        ax=Axes(x_range=[0,5.5,1],y_range=[-3.2,3.2,1],x_length=6.2,y_length=6.7,axis_config={'color':GRAY,'stroke_width':2,'tip_width':.12,'tip_height':.16}).move_to([0,1.25,0]);self.add(ax)
        for x in [1,2,3,4,5]:self.add(MathTex(str(x),font_size=24,color=INK).move_to(ax.c2p(x,-.27)))
        for y in [-1,1]:self.add(MathTex(str(y),font_size=25,color=INK).next_to(ax.c2p(0,y),LEFT,buff=.15))
        self.add(MathTex('x',font_size=26,color=INK).next_to(ax.c2p(5.5,0),RIGHT,buff=.08),MathTex('y',font_size=26,color=INK).next_to(ax.c2p(0,3.2),UP,buff=.08))
        for y in [-1,1]:self.add(DashedLine(ax.c2p(.06,y),ax.c2p(5.3,y),color=GRAY,stroke_width=1.3))
        self.add(always_redraw(lambda:ax.plot(lambda x:log_value(large.get_value(),x),x_range=[.12,5.2,.025],color=BLUE,stroke_width=3.4)))
        self.add(always_redraw(lambda:ax.plot(lambda x:log_value(1/large.get_value(),x),x_range=[.12,5.2,.025],color=ORANGE,stroke_width=3.4)))
        self.add(always_redraw(lambda:DashedLine(ax.c2p(large.get_value(),-1),ax.c2p(large.get_value(),1),color=GRAY,stroke_width=1.3)))
        for y,c in [(1,BLUE),(-1,ORANGE)]:self.add(always_redraw(lambda y=y,c=c:Dot(ax.c2p(large.get_value(),y),color=c,radius=.085)))
        self.add(Dot(ax.c2p(1,0),color=GOLD,radius=.08))
        self.add(Line(ax.c2p(1,0),ax.c2p(4,.35),color=GRAY,stroke_width=1),MathTex('(1,0)',font_size=26,color=INK).move_to(ax.c2p(4.65,.35)))
        self.add(MathTex(r'y=1:\quad x=a',font_size=30,color=BLUE).move_to([-1.8,-2.8,0]))
        self.add(MathTex(r'y=-1:\quad x=1/a',font_size=30,color=ORANGE).move_to([1.8,-2.8,0]))
        def row(y,formula,col,fn):
            self.add(txt(formula,25).move_to([-1.8,y,0]),MathTex('a\\approx',font_size=32,color=col).move_to([.1,y,0]));n=DecimalNumber(fn(),num_decimal_places=2,font_size=33,color=col).move_to([1.75,y,0]);n.add_updater(lambda m:m.set_value(fn()));self.add(n)
        row(-3.7,'上方底数',BLUE,lambda:large.get_value())
        row(-4.55,'下方底数',ORANGE,lambda:1/large.get_value())
        self.add(always_redraw(lambda:txt('交点向右：大底增大，小底减小' if direction.get_value()>0 else '回放向左：底数变化方向相反',24).move_to([0,-5.4,0])))
        self.add(txt('蓝、橙曲线互为倒数底数；读数保留两位小数',18).move_to([0,-5.95,0]))
        self.add(txt('查结论 · 看图解 · 学证明｜知树 App',23).move_to([0,-6.65,0]),txt('公众号 ok-shuxue｜获取入口',21).move_to([0,-7.2,0]))
        self.wait(1.5)
        for a in [3,4]:self.play(large.animate.set_value(a),run_time=3);self.wait(1.5)
        direction.set_value(-1);self.play(large.animate.set_value(2),run_time=3);self.wait(.7)
        direction.set_value(1);self.wait(.7,frozen_frame=False)
