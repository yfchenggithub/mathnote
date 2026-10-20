import math
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from manim import *
from model import state, clip_line

config.background_color='#F7F8FA'
config.frame_width,config.frame_height=9,16
INK='#213044'
MUTED='#526275'
BLUE='#2778BD'
PURPLE='#7959A6'
ORANGE='#CD6031'
GREEN='#158068'
AXIS='#A7B4C2'


class C012OriginDistance(Scene):
    def construct(self):
        def cn(s,size=27,color=INK):
            return Text(s,font='Microsoft YaHei',font_size=size,color=color)
        def eq(s,size=34,color=INK):
            return MathTex(s,font_size=size,color=color)
        def xy(p): return np.array([1.02*p[0],1.02*p[1]+.8,0])
        theta=ValueTracker(PI/4)
        def now(): return state(theta.get_value())
        title=cn('切线离中心多远？',34).move_to([0,6.9,0])
        sub=eq(r'\frac{x^2}{9}+\frac{y^2}{4}=1\quad(a=3,\ b=2)',31).move_to([0,5.9,0])
        caption=cn('从中心作垂线，找到真实距离',26).move_to([0,4.85,0])
        axes=VGroup(Line(xy((-3.6,0)),xy((3.6,0)),color=AXIS,stroke_width=1.5),Line(xy((0,-3)),xy((0,3)),color=AXIS,stroke_width=1.5))
        labels=VGroup(eq('O',25).move_to(xy((-.18,-.27))),eq('x',25).move_to(xy((3.55,-.25))),eq('y',25).move_to(xy((0,3.3))))
        ellipse=ParametricFunction(lambda t:xy(state(t)['p']),t_range=[0,TAU],color=INK,stroke_width=3.5)
        focal=VGroup(Dot(xy(now()['f1']),color=BLUE,radius=.055),Dot(xy(now()['f2']),color=PURPLE,radius=.055),eq('F_1',24,BLUE).move_to(xy(now()['f1'])+DOWN*.32),eq('F_2',24,PURPLE).move_to(xy(now()['f2'])+DOWN*.32))
        tangent=always_redraw(lambda:Line(*[xy(p) for p in clip_line(*now()['line'])],color=ORANGE,stroke_width=3.4))
        radii=always_redraw(lambda:VGroup(Line(xy(now()['f1']),xy(now()['p']),color=BLUE,stroke_width=3.5),Line(xy(now()['f2']),xy(now()['p']),color=PURPLE,stroke_width=3.5)))
        perp=always_redraw(lambda:Line(xy((0,0)),xy(now()['h']),color=GREEN,stroke_width=5))
        def marker():
            h=xy(now()['h']); n=h-xy((0,0)); n=n/np.linalg.norm(n)
            u=np.array([-n[1],n[0],0]); v=-n; size=.16
            return VMobject(color=GREEN,stroke_width=2).set_points_as_corners([h+size*u,h+size*(u+v),h+size*v])
        square=always_redraw(marker)
        pdot=always_redraw(lambda:Dot(xy(now()['p']),color=ORANGE,radius=.07))
        plabel=always_redraw(lambda:eq('P',27).move_to(xy(now()['p'])+np.array([.23,.29,0])))
        def hmark():
            s=now(); visible=min(1,max(0,(math.dist(s['p'],s['h'])-.15)/.3))
            return VGroup(Dot(xy(s['h']),color=GREEN,radius=.055),eq('H',25,GREEN).move_to(xy(s['h'])+np.array([-.26,.24,0]))).fade(1-visible)
        hlabel=always_redraw(hmark)
        dlabel=always_redraw(lambda:eq('d',29,GREEN).move_to((xy(now()['h'])+xy((0,0)))/2+np.array([-.27,0,0])))
        op=DashedLine(xy((0,0)),xy(now()['p']),color=MUTED,stroke_width=2,dash_length=.12)
        legend=VGroup(eq(r'r_1=PF_1',27,BLUE),eq(r'r_2=PF_2',27,PURPLE),eq('d=OH',27,GREEN)).arrange(RIGHT,buff=.5).move_to([0,-2.95,0])
        def reading(formula,key,color,x):
            label=eq(formula+r'\approx',32,color)
            number=DecimalNumber(8.88,num_decimal_places=2,font_size=34,color=color)
            group=VGroup(label,number).arrange(RIGHT,buff=.14).move_to([x,-4.05,0])
            anchor=number.get_right().copy()
            number.add_updater(lambda m:m.set_value(now()[key]).align_to(anchor,RIGHT))
            number.update(0)
            return group
        readings=VGroup(reading(r'\sqrt{r_1r_2}','g',INK,-1.9),reading('d','d',GREEN,2))
        result=eq(r'\sqrt{r_1r_2}\,d=6=ab',40,GREEN).move_to([0,-5.25,0])
        foot=cn('d 是垂距，一般不等于 OP',24,MUTED).move_to([0,-6.6,0])
        self.add(title,sub,caption,axes,labels,ellipse,focal,tangent,radii,op,perp,square,pdot,plabel,hlabel,dlabel,legend,readings,result,foot)
        self.wait(2)
        self.play(FadeOut(op),Transform(caption,cn('切点移动：两项变化，乘积不变',25).move_to(caption)),run_time=.35)
        self.play(theta.animate.set_value(15*DEGREES),run_time=2)
        self.wait(.6)
        self.play(theta.animate.set_value(75*DEGREES),run_time=3)
        self.wait(.6)
        self.play(theta.animate.set_value(PI/4),run_time=1.5)
        self.play(Transform(caption,cn('同一个量，分别出现在分子与分母',24).move_to(caption)),FadeOut(readings),run_time=.35)
        why=VGroup(eq(r'r_1r_2=a^2-e^2x_0^2',31),eq(r'd=\frac{ab}{\sqrt{a^2-e^2x_0^2}}',33,GREEN)).arrange(DOWN,buff=.28).move_to([0,-4.25,0])
        self.play(FadeIn(why),result.animate.move_to([0,-5.85,0]),run_time=.35)
        self.wait(2.5)
        self.play(FadeOut(why),FadeIn(readings),result.animate.move_to([0,-5.25,0]),Transform(caption,cn('走向长轴顶点，观察垂距增大',25).move_to(caption)),run_time=.35)
        self.play(theta.animate.set_value(0),run_time=1.3)
        self.play(Transform(caption,cn('长轴顶点：距离最大，此时 H=P',25).move_to(caption)),Transform(foot,eq(r'd_{\max}=a=3,\quad\sqrt{r_1r_2}=b=2',29,MUTED).move_to(foot)),run_time=.3)
        self.wait(1.5)
        self.play(Transform(caption,cn('从长轴顶点走向短轴顶点',25).move_to(caption)),Transform(foot,cn('d 逐渐减小，焦半径几何平均数逐渐增大',22,MUTED).move_to(foot)),run_time=.3)
        self.play(theta.animate.set_value(PI/2),run_time=2.5)
        self.play(Transform(caption,cn('短轴顶点：距离最小，此时 H=P',25).move_to(caption)),Transform(foot,eq(r'd_{\min}=b=2,\quad\sqrt{r_1r_2}=a=3',29,MUTED).move_to(foot)),run_time=.3)
        self.wait(1.5)
        self.play(Transform(caption,cn('始终有 b ≤ d ≤ a',27).move_to(caption)),Transform(foot,cn('d 是垂距，一般不等于 OP',24,MUTED).move_to(foot)),run_time=.3)
        self.play(theta.animate.set_value(PI/4),run_time=1.5)
        self.wait(1)
        self.play(FadeIn(op),Transform(caption,cn('从中心作垂线，找到真实距离',26).move_to(caption)),run_time=.35)
        self.wait(.7)
