"""A changing confocal hyperbola reveals the C090 focal-angle identity."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from model import state, motion_h
from manim import *
import math

config.background_color = '#F7F8FA'
config.frame_width = 9
config.frame_height = 16

INK='#213044'; MUTED='#526275'; BLUE='#2778BD'; ORANGE='#B64E24'
GREEN='#158068'; GOLD='#A56D08'; AXIS='#A7B4C2'


def cn(s, size=28, color=INK):
    return Text(s, font='Microsoft YaHei', font_size=size, color=color)


def tex(s, size=34, color=INK):
    return MathTex(s, font_size=size, color=color)


def number(value, places=2, size=34, color=INK):
    return DecimalNumber(value,num_decimal_places=places,font_size=size,color=color)


def reading(label,value,places=2,size=34,color=INK,suffix=None):
    parts=[tex(label,size,color),number(value,places,size,color)]
    if suffix: parts.append(tex(suffix,size,color))
    return VGroup(*parts).arrange(RIGHT,buff=.08)


class C090ConfocalAngle(Scene):
    def construct(self):
        self.time_tracker=ValueTracker(0)
        self.layout_checks=[]
        h=lambda: motion_h(self.time_tracker.get_value())
        q=lambda: state(h())
        def xy(x,y): return np.array([.78*x,.78*y+2.5,0])
        left,right=xy(-2,0),xy(2,0)
        pp=lambda: xy(q().x,q().y)
        # Stage bounds are in scene units; equal x/y scale is essential.
        title=cn('共焦点，把焦角与离心率连起来',32).move_to([0,7.1,0])
        initial=cn('固定椭圆，改变共焦双曲线',27,MUTED).move_to([0,6.4,0])
        legend=VGroup(cn('椭圆 E  实线',24,BLUE),cn('双曲线 H  虚线',24,ORANGE)).arrange(RIGHT,buff=.55).move_to([0,5.8,0])
        footer1=cn('查结论 · 看图解 · 学证明｜知树 App',24,MUTED).move_to([0,-6.85,0])
        footer2=cn('公众号 ok-shuxue｜获取入口',22,MUTED).move_to([0,-7.4,0])
        fixed=VGroup(title,legend,footer1,footer2)
        axis=VGroup(Line(xy(-4.45,0),xy(4.45,0),color=AXIS,stroke_width=1.3),
                    Line(xy(0,-3.75),xy(0,3.75),color=AXIS,stroke_width=1.3))
        ellipse=ParametricFunction(lambda t:xy(4*math.cos(t),math.sqrt(12)*math.sin(t)),
                                   t_range=[0,TAU,.025],color=BLUE,stroke_width=3.1)
        def hyperbola():
            b=math.sqrt(4-h()**2)
            u=min(math.asinh(3.72/b),math.acosh(4.45/h()))
            curves=VGroup()
            for sign in (-1,1):
                curve=ParametricFunction(lambda t,sign=sign:xy(sign*h()*math.cosh(t),b*math.sinh(t)),
                                         t_range=[-u,u,.025],color=ORANGE,stroke_width=3)
                curves.add(DashedVMobject(curve,num_dashes=34,dashed_ratio=.68))
            return curves
        hyper=always_redraw(hyperbola)
        focal_lines=always_redraw(lambda:VGroup(Line(left,pp(),color=GREEN,stroke_width=3.2),
                                                 Line(right,pp(),color=GREEN,stroke_width=3.2)))
        focals=VGroup(Dot(left,radius=.055,color=INK),Dot(right,radius=.055,color=INK),
                      tex('F_1',28).move_to(left+DOWN*.33),tex('F_2',28).move_to(right+DOWN*.33),
                      tex('O',24,color=MUTED).move_to(xy(0,0)+DOWN*.28+LEFT*.18))
        point=always_redraw(lambda:Dot(pp(),radius=.075,color=GOLD))
        # Right/slightly above P: between H above and E below, including at
        # the widest hyperbola, without entering the legend near the top.
        point_label=always_redraw(lambda:tex('P',29,color=GOLD).move_to(pp()+RIGHT*.55+UP*.15))
        def angle_mark():
            v1,v2=left-pp(),right-pp()
            start=math.atan2(v1[1],v1[0])
            return Arc(radius=.45,start_angle=start,angle=q().theta,
                       arc_center=pp(),color=GREEN,stroke_width=2.2)
        arc=always_redraw(angle_mark)
        def theta_label():
            v=left-pp(); start=math.atan2(v[1],v[0])
            mid=start+q().theta*.28
            return tex(r'\theta',32,color=GREEN).move_to(pp()+1.1*np.array([math.cos(mid),math.sin(mid),0]))
        theta=always_redraw(theta_label)
        parameters=always_redraw(lambda:VGroup(
            tex(r'e_1=0.50',34,color=BLUE),
            reading(r'e_2\approx',q().e2,color=ORANGE),
            reading(r'\theta\approx',math.degrees(q().theta),places=1,color=GREEN,suffix=r'^\circ')
        ).arrange(RIGHT,buff=.42).move_to([0,-.92,0]))
        lengths=always_redraw(lambda:VGroup(
            reading(r'PF_1\approx',q().r1,color=GREEN),
            reading(r'PF_2\approx',q().r2,color=GREEN)
        ).arrange(RIGHT,buff=.65).move_to([0,-1.65,0]))
        sums=tex(r'PF_1+PF_2=2a_E=8',38,color=BLUE).move_to([0,-2.45,0])
        differences=always_redraw(lambda:reading(r'|PF_1-PF_2|=2a_H\approx',2*h(),size=38,color=ORANGE).move_to([0,-3.18,0]))
        scale_note=cn('共同焦点不动，公共点沿椭圆移动',25,MUTED).move_to([0,-4.55,0])
        condition=tex(r'c=2,\quad a_E=4,\quad 0<a_H<c',28,color=MUTED).move_to([0,-5.35,0])
        graph=VGroup(axis,ellipse,hyper,focal_lines,focals,point,point_label,arc,theta)
        self.add(fixed,initial,graph,parameters,lengths,sums,differences,scale_note,condition)
        # Track labels at every real rendered frame without altering geometry.
        tracked=[title,legend,footer1,footer2,initial,point_label,theta,parameters,
                 lengths,sums,differences,scale_note,condition]
        def check_layout(_dt):
            for m in tracked:
                if m in self.mobjects or m is point_label or m is theta:
                    if m.get_left()[0]<-4.15 or m.get_right()[0]>4.15 or m.get_bottom()[1]<-7.75 or m.get_top()[1]>7.65:
                        raise ValueError('C090 label outside safe area')
        self.add_updater(check_layout)
        self.wait(1.5)
        self.time_tracker.set_value(1.5)
        self.play(self.time_tracker.animate.set_value(4.5),run_time=3,rate_func=linear)
        self.time_tracker.set_value(5.5); self.wait(1)
        self.play(self.time_tracker.animate.set_value(8.5),run_time=3,rate_func=linear)
        self.time_tracker.set_value(8.5)
        insight=cn('椭圆给和，双曲线给差',27,MUTED).move_to(initial)
        self.play(FadeOut(initial),run_time=.25)
        self.play(FadeIn(insight),run_time=.25)
        self.wait(.5)
        formula=tex(r'\frac{\sin^2(\theta/2)}{e_1^2}+\frac{\cos^2(\theta/2)}{e_2^2}=1',44,color=INK).move_to([0,-3.4,0])
        invariant=always_redraw(lambda:VGroup(number(q().ellipse_term,3,38,GREEN),tex('+',38,GREEN),
                         number(q().hyperbola_term,3,38,GREEN),tex('=1',38,GREEN)).arrange(RIGHT,buff=.18).move_to([0,-4.6,0]))
        why=cn('余弦定理消去两条焦半径',25,MUTED).move_to([0,-5.4,0])
        self.play(FadeOut(sums),FadeOut(differences),FadeOut(lengths),FadeOut(scale_note),FadeOut(condition),run_time=.25)
        self.play(FadeIn(formula),FadeIn(invariant),FadeIn(why),run_time=.25)
        self.wait(1)
        # Timeline now 11 seconds; return to the same trajectory parametrization.
        self.time_tracker.set_value(11)
        self.play(self.time_tracker.animate.set_value(14),run_time=3,rate_func=linear)
        self.time_tracker.set_value(14.5); self.wait(.5)
        self.play(self.time_tracker.animate.set_value(16),run_time=1.5,rate_func=linear)
        equality_heading=cn('当 e₁e₂ = 1，推论恰好取等号',27,MUTED).move_to(initial)
        bound=tex(r'\frac1{e_1}+\frac1{e_2}\le\frac2{\sin\theta}',44).move_to([0,-3.35,0])
        exact=tex(r'2+\frac12=\frac2{4/5}=\frac52',42,color=GREEN).move_to([0,-4.6,0])
        equality_note=cn('等号只可能在锐角时成立',25,MUTED).move_to([0,-5.4,0])
        self.play(FadeOut(insight),FadeOut(formula),FadeOut(invariant),FadeOut(why),run_time=.25)
        self.play(FadeIn(equality_heading),FadeIn(bound),FadeIn(exact),FadeIn(equality_note),run_time=.25)
        self.wait(3.5)
        self.play(FadeOut(equality_heading),FadeOut(bound),FadeOut(exact),FadeOut(equality_note),run_time=.25)
        self.play(FadeIn(initial),FadeIn(lengths),FadeIn(sums),FadeIn(differences),FadeIn(scale_note),FadeIn(condition),run_time=.25)
        self.wait(.5)
        self.time_tracker.set_value(21)
        self.play(self.time_tracker.animate.set_value(23),run_time=2,rate_func=linear)
        self.wait(1)
