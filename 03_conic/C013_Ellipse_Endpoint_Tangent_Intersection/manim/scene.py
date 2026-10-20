import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from manim import *
from model import state

config.background_color='#F7F8FA'
config.frame_width,config.frame_height=9,16
INK='#213044'
MUTED='#526275'
BLUE='#2778BD'
PURPLE='#7959A6'
ORANGE='#CD6031'
GREEN='#158068'
AXIS='#A7B4C2'


class C013EndpointIntersection(Scene):
    def construct(self):
        def cn(s,size=26,color=INK): return Text(s,font='Microsoft YaHei',font_size=size,color=color)
        def eq(s,size=34,color=INK): return MathTex(s,font_size=size,color=color)
        def xy(p): return np.array([1.45*p[0],1.45*p[1]+.3,0])
        ratio=ValueTracker(.65)
        def now(): return state(ratio.get_value())
        title=cn('两段一长一短，乘积不变',31).move_to([0,6.9,0])
        subtitle=eq(r'\frac{x^2}{4}+y^2=1\quad(a=2,\ b=1)',31).move_to([0,5.9,0])
        caption=cn('两条固定端点切线：x=±a',26).move_to([0,4.85,0])
        axes=VGroup(Line(xy((-2.6,0)),xy((2.6,0)),color=AXIS,stroke_width=1.5),Line(xy((0,-1.45)),xy((0,2.7)),color=AXIS,stroke_width=1.5))
        axislabels=VGroup(eq('O',24).move_to(xy((-.16,-.23))),eq('x',24).move_to(xy((2.6,-.2))))
        fixed=VGroup(*[Line(xy((x,-1.45)),xy((x,2.7)),color=AXIS,stroke_width=2) for x in (-2,2)])
        endpoints=VGroup(*[Dot(xy((x,0)),color=INK,radius=.045) for x in (-2,2)])
        names=VGroup(eq('A_1',25).move_to(xy((-2.2,-.24))),eq('A_2',25).move_to(xy((2.2,-.24))))
        fill=always_redraw(lambda:Polygon(*[xy(now()[name]) for name in ('a1','p1','p2','a2')],stroke_width=0,fill_color=GREEN,fill_opacity=.11))
        ellipse=ParametricFunction(lambda t:xy((2*np.cos(t),np.sin(t))),t_range=[0,TAU],color=INK,stroke_width=3.5)
        heights=always_redraw(lambda:VGroup(Line(xy(now()['a1']),xy(now()['p1']),color=BLUE,stroke_width=6),Line(xy(now()['a2']),xy(now()['p2']),color=PURPLE,stroke_width=6)))
        tangent=always_redraw(lambda:Line(xy(now()['p1']),xy(now()['p2']),color=ORANGE,stroke_width=3.5))
        dots=always_redraw(lambda:VGroup(Dot(xy(now()['p1']),color=BLUE,radius=.06),Dot(xy(now()['p2']),color=PURPLE,radius=.06),Dot(xy(now()['p']),color=ORANGE,radius=.07)))
        movenames=always_redraw(lambda:VGroup(eq('P_1',25,BLUE).move_to(xy(now()['p1'])+np.array([-.25,.22,0])),eq('P_2',25,PURPLE).move_to(xy(now()['p2'])+np.array([.25,.22,0])),eq('P',26).move_to(xy(now()['p'])+np.array([0,-.3,0]))))
        lengths=always_redraw(lambda:VGroup(eq('d_1',28,BLUE).move_to((xy(now()['a1'])+xy(now()['p1']))/2+LEFT*.35),eq('d_2',28,PURPLE).move_to((xy(now()['a2'])+xy(now()['p2']))/2+RIGHT*.35)))
        width=DoubleArrow(xy((-2,-1.27)),xy((2,-1.27)),buff=0,color=MUTED,stroke_width=2,tip_length=.12)
        widthlabel=eq('2a',25,MUTED).move_to(xy((0,-1.5)))
        def numberline(symbol,key,color,x,y):
            label=eq(symbol+r'\approx',32,color)
            number=DecimalNumber(8.88,num_decimal_places=2,font_size=34,color=color)
            group=VGroup(label,number).arrange(RIGHT,buff=.12).move_to([x,y,0])
            anchor=number.get_right().copy()
            number.add_updater(lambda m:m.set_value(now()[key]).align_to(anchor,RIGHT))
            number.update(0)
            return group
        numbers=VGroup(numberline('d_1','d1',BLUE,-1.9,-3.2),numberline('d_2','d2',PURPLE,1.9,-3.2))
        product=eq(r'd_1d_2=1=b^2',41,GREEN).move_to([0,-4.4,0])
        area=numberline('S','area',INK,0,-5.65)
        foot=eq(r'P\ne(\pm a,0)',29,MUTED).move_to([0,-6.8,0])
        self.add(title,subtitle,caption,axes,axislabels,fixed,fill,ellipse,heights,tangent,endpoints,names,dots,movenames,lengths,width,widthlabel,numbers,product,area,foot)
        self.wait(1.5)
        self.play(Transform(caption,cn('一段变长，另一段就变短',26).move_to(caption)),run_time=.3)
        self.play(ratio.animate.set_value(-.8),run_time=3)
        self.wait(.7)
        self.play(ratio.animate.set_value(.8),run_time=3)
        self.wait(.7)
        self.play(ratio.animate.set_value(.4),run_time=1)
        self.play(FadeOut(numbers),FadeOut(area),Transform(caption,cn('平方差锁住两个截高的乘积',25).move_to(caption)),run_time=.35)
        proof=VGroup(eq(r'\ell:\ y=kx+m',29,ORANGE),eq(r'(m-ak)(m+ak)=m^2-a^2k^2=b^2',30)).arrange(DOWN,buff=.27).move_to([0,-3.15,0])
        self.play(FadeIn(proof),run_time=.3)
        self.wait(2.5)
        self.play(FadeOut(proof),FadeIn(numbers),FadeIn(area),Transform(caption,cn('积固定，两段等长时面积最小',25).move_to(caption)),run_time=.35)
        bound=eq(r'S=a(d_1+d_2)\ge2ab=4',33,GREEN).move_to([0,-6.8,0])
        self.play(Transform(foot,bound),ratio.animate.set_value(0),run_time=1.8)
        self.play(Transform(caption,cn('短轴顶点：梯形变成矩形',26).move_to(caption)),run_time=.3)
        self.wait(2)
        self.play(Transform(caption,cn('偏离等长状态，面积随之增大',25).move_to(caption)),run_time=.3)
        self.play(ratio.animate.set_value(-.8),run_time=2)
        self.wait(.6)
        self.play(Transform(caption,cn('两条固定端点切线：x=±a',26).move_to(caption)),Transform(foot,eq(r'P\ne(\pm a,0)',29,MUTED).move_to(foot)),run_time=.3)
        self.play(ratio.animate.set_value(.65),run_time=2.5)
        self.wait(.8)
