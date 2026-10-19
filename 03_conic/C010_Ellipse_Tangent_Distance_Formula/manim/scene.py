"""C010: invariant distance product, complete focal pedal circle, and center foot."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from model import TangentDistanceModel,START,clip_line
from manim import *
import numpy as np

config.background_color='#F7F8FA'
config.frame_width,config.frame_height=9,16
INK,MUTED,BLUE,ORANGE,GREEN,AXIS='#213044','#526275','#2778BD','#CD6031','#158068','#A7B4C2'


class C010TangentDistance(Scene):
    def construct(self):
        model=TangentDistanceModel();angle=ValueTracker(START)
        origin=np.array([0.,.7,0.]);scale=.64
        def xy(p):
            return origin+scale*np.array([p[0],p[1],0.])
        def state():
            return model.state(angle.get_value())
        def text(s,size=28,color=INK):
            return Text(s,font='Microsoft YaHei',font_size=size,color=color)
        def math_footer(s,size=36,color=INK):
            return MathTex(s,font_size=size,color=color).move_to([0,-6.55,0])
        def right_mark(H,n,tau,color):
            step=.15
            return VMobject(color=color,stroke_width=1.8).set_points_as_corners([H-step*n,H-step*n+step*tau,H+step*tau])
        title=text('切线转动，什么保持不变？',36).move_to([0,6.92,0])
        subtitle=text('两焦点的垂距会变，乘积始终不变',26,MUTED).move_to([0,6.02,0])
        equation=MathTex(r'\frac{x^2}{25}+\frac{y^2}{16}=1,\quad c=3',font_size=34,color=INK).move_to([0,5.08,0])
        axes=VGroup(Line(xy((-5.7,0)),xy((5.7,0))),Line(xy((0,-5.5)),xy((0,5.5)))).set_stroke(AXIS,1.2)
        ellipse=ParametricFunction(lambda t:xy((model.a*np.cos(t),model.b*np.sin(t))),t_range=[0,TAU],color=BLUE,stroke_width=3.5)
        foci=VGroup(Dot(xy((-model.c,0)),radius=.065,color=INK),Dot(xy((model.c,0)),radius=.065,color=INK))
        labels=VGroup(MathTex('F_1',font_size=26,color=INK).next_to(xy((-model.c,0)),DOWN,buff=.16),MathTex('F_2',font_size=26,color=INK).next_to(xy((model.c,0)),DOWN,buff=.16),MathTex('O',font_size=23,color=MUTED).next_to(origin,DOWN,buff=.13))
        def diagram():
            s=state();u,v=s['normal'];n=np.array([u,v,0.]);tau=np.array([-v,u,0.]);ends=clip_line(u,v,s['h'])
            P,H1,H2=xy(s['P']),xy(s['H1']),xy(s['H2'])
            group=VGroup(Line(xy(ends[0]),xy(ends[1]),color=MUTED,stroke_width=3),
                         Line(xy(s['F1']),H1,color=ORANGE,stroke_width=3.6),Line(xy(s['F2']),H2,color=GREEN,stroke_width=3.6),
                         right_mark(H1,n,tau,ORANGE),right_mark(H2,n,tau,GREEN),
                         Dot(H1,radius=.075,color=ORANGE),Dot(H2,radius=.075,color=GREEN),Dot(P,radius=.055,color=INK))
            if abs(v)<1e-8:
                group.add(MathTex(r'P=H_1=H_2',font_size=25,color=INK).move_to(P+np.array([-.85*np.sign(u),.36,0.])))
            elif np.linalg.norm(H1-H2)<.35:
                group.add(MathTex('P',font_size=26,color=INK).move_to(P+np.array([-.5*np.sign(u),.42,0.])),
                          MathTex('H_1',font_size=24,color=ORANGE).move_to(H1+.24*n+.28*tau),
                          MathTex('H_2',font_size=24,color=GREEN).move_to(H2+.24*n-.28*tau))
            else:
                group.add(MathTex('P',font_size=28,color=INK).move_to(P+.28*n),
                          MathTex('H_1',font_size=25,color=ORANGE).move_to(H1+.24*n+.16*tau),
                          MathTex('H_2',font_size=25,color=GREEN).move_to(H2+.24*n-.16*tau))
            return group
        moving=always_redraw(diagram)
        num1=DecimalNumber(8.88,num_decimal_places=2,font_size=35,color=ORANGE)
        num2=DecimalNumber(8.88,num_decimal_places=2,font_size=35,color=GREEN)
        read1=VGroup(MathTex(r'd_1\approx',font_size=34,color=ORANGE),num1).arrange(RIGHT,buff=.12).move_to([-1.9,-3.4,0])
        read2=VGroup(MathTex(r'd_2\approx',font_size=34,color=GREEN),num2).arrange(RIGHT,buff=.12).move_to([1.9,-3.4,0])
        a1,a2=num1.get_right().copy(),num2.get_right().copy()
        num1.add_updater(lambda obj:obj.set_value(state()['d1']).align_to(a1,RIGHT));num1.update(0)
        num2.add_updater(lambda obj:obj.set_value(state()['d2']).align_to(a2,RIGHT));num2.update(0)
        product=DecimalNumber(16,num_decimal_places=2,font_size=42,color=INK)
        product_row=VGroup(MathTex(r'd_1d_2=',font_size=41,color=INK),product,MathTex(r'=b^2',font_size=41,color=INK)).arrange(RIGHT,buff=.12).move_to([0,-4.5,0])
        pa=product.get_right().copy();product.add_updater(lambda obj:obj.set_value(state()['d1']*state()['d2']).align_to(pa,RIGHT));product.update(0)
        caption=text('两段距离不相等，积却恒为 16',28).move_to([0,-5.5,0])
        footer=text('P 是切点；H₁、H₂ 是焦点垂足',25,MUTED).move_to([0,-6.65,0])
        self.add(title,subtitle,equation,axes,ellipse,moving,foci,labels,read1,read2,product_row,caption,footer)
        self.wait(1.1)
        def say(s,color=INK):
            self.play(Transform(caption,text(s,27,color).move_to([0,-5.5,0])),run_time=.3)
        say('切线转到水平：两焦点垂距相等')
        self.play(angle.animate.set_value(PI/2),run_time=2.2,rate_func=smooth)
        self.wait(1.4)
        say('转到竖直：8 × 2 仍然等于 16')
        self.play(angle.animate.set_value(0),run_time=2.8,rate_func=smooth)
        self.wait(1.4)
        say('再看垂足：它们都落在长轴主圆上',GREEN)
        circle=Circle(radius=scale*model.a,color=AXIS,stroke_width=2).move_to(origin)
        self.add(circle);self.bring_to_back(circle)
        self.play(Create(circle),Transform(footer,math_footer(r'OH_1=OH_2=a=5',38,GREEN)),run_time=.5)
        self.wait(.9)
        trace=TracedPath(lambda:xy(state()['H2']),stroke_color=GREEN,stroke_width=2.6)
        self.add(trace);self.bring_to_front(moving,foci,labels)
        say('固定右焦点，垂足的完整轨迹是整圆',GREEN)
        self.play(Transform(footer,math_footer(r'x^2+y^2=a^2=25',38,GREEN)),run_time=.3)
        self.play(angle.animate.set_value(TAU),run_time=8,rate_func=linear)
        self.wait(.8)
        trace.clear_updaters()
        say('中心到切线的距离，介于 b 与 a 之间')
        self.play(angle.animate.set_value(TAU+START),run_time=2.2,rate_func=smooth)
        def center_diagram():
            s=state();u,v=s['normal'];n=np.array([u,v,0.]);tau=np.array([-v,u,0.]);Q=xy(s['Q'])
            return VGroup(DashedLine(origin,Q,color=MUTED,stroke_width=2,dash_length=.09),
                          Dot(Q,radius=.06,color=MUTED),MathTex('Q',font_size=25,color=MUTED).move_to(Q+np.array([-.28,.14,0.])),
                          MathTex('d_0',font_size=25,color=MUTED).move_to((origin+Q)/2-.23*tau),right_mark(Q,n,tau,MUTED))
        center=always_redraw(center_diagram)
        self.play(FadeIn(center),Transform(footer,math_footer(r'4\leq d_0\leq5,\quad d_1+d_2=2d_0',32,GREEN)),run_time=.4)
        self.wait(1.7)
        self.play(FadeOut(center),FadeOut(trace),FadeOut(circle),
                  Transform(caption,text('两段距离不相等，积却恒为 16',28).move_to([0,-5.5,0])),
                  Transform(footer,text('P 是切点；H₁、H₂ 是焦点垂足',25,MUTED).move_to([0,-6.65,0])),run_time=.4)
        self.wait(.5)
