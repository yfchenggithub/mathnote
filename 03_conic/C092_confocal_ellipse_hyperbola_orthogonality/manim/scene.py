"""C092: moving confocal hyperbola, actual tangents at actual intersections."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from model import ConfocalPair
from manim import *
import numpy as np

config.background_color='#F7F8FA'
config.frame_width=9
config.frame_height=16
INK='#213044'; MUTED='#526275'; BLUE='#2778BD'; ORANGE='#CD6031'; GREEN='#158068'; AXIS='#A7B4C2'


class C092Orthogonality(Scene):
    def construct(self):
        def text(s,size=27,color=INK):
            return Text(s,font='Microsoft YaHei',font_size=size,color=color)
        def formula(s,size=33,color=INK):
            return MathTex(s,font_size=size,color=color)
        def pos(x,y): return np.array([.8*x,1.1+.8*y,0])
        def direction(d): return np.array([d[0],d[1],0])
        tracker=ValueTracker(1)
        def model(): return ConfocalPair(A=tracker.get_value())
        title=text('交点在变，直角不变',37).move_to([0,7.15,0])
        subtitle=text('椭圆固定，双曲线改变形状',27,MUTED).move_to([0,6.43,0])
        legend=VGroup(text('椭圆 E',26,BLUE),text('双曲线 H',26,ORANGE)).arrange(RIGHT,buff=.7).move_to([0,5.72,0])
        footer=VGroup(text('查结论 · 看图解 · 学证明｜知树 App',23,MUTED).move_to([0,-6.85,0]),
                      text('公众号 ok-shuxue｜获取入口',21,MUTED).move_to([0,-7.37,0]))
        self.add(title,subtitle,legend,footer)
        axes=VGroup(Line(pos(-4.5,0),pos(4.5,0),color=AXIS,stroke_width=1.4),
                    Line(pos(0,-4.25),pos(0,4.25),color=AXIS,stroke_width=1.4))
        ellipse=Ellipse(width=6.4,height=1.6*np.sqrt(12),color=BLUE,stroke_width=3.4).move_to(pos(0,0))
        def hyperbola():
            m=model(); ymax=min(4.1,np.sqrt(m.B2)*np.sqrt((4.35/m.A)**2-1))
            return VGroup(*[ParametricFunction(lambda t,sgn=sgn:pos(m.hyperbola_x(t,sgn),t),
                       t_range=[-ymax,ymax,.045],color=ORANGE,stroke_width=3) for sgn in (-1,1)])
        hyper=always_redraw(hyperbola)
        foci=VGroup(*[Dot(pos(x,0),radius=.055,color=INK) for x in (-2,2)])
        focal_labels=VGroup(formula('F_1',27).move_to(pos(-2,-.42)),formula('F_2',27).move_to(pos(2,-.42)))
        origin=formula('O',22,color=MUTED).move_to(pos(-.24,-.3))
        dots=always_redraw(lambda:VGroup(*[Dot(pos(*model().point(sx,sy)),radius=.065,color=INK)
                       for sx in (-1,1) for sy in (-1,1)]))
        def point_name():
            m=model(); e,h=[direction(d) for d in m.directions()]
            offset=-.48*(e+h)/np.linalg.norm(e+h)
            return formula('P',29).move_to(pos(*m.point())+offset)
        point_label=always_redraw(point_name)
        self.add(axes,ellipse,hyper,foci,focal_labels,origin,dots,point_label)
        condition=text('两条曲线始终共用焦点 F₁、F₂',26,MUTED).move_to([0,-2.63,0])
        eqe=formula(r'E:\ \frac{x^2}{16}+\frac{y^2}{12}=1',32,BLUE).move_to([0,-3.38,0])
        eqh=formula(r'H:\ \frac{x^2}{A^2}-\frac{y^2}{4-A^2}=1',32,ORANGE).move_to([0,-4.22,0])
        av=VGroup(formula('A=',30),DecimalNumber(1,num_decimal_places=2,font_size=30,color=INK))
        av.arrange(RIGHT,buff=.12).move_to([-1.7,-5.12,0])
        av[1].add_updater(lambda d:d.set_value(tracker.get_value()))
        bounds=formula(r'0<A<2',30,color=MUTED).move_to([1.5,-5.12,0])
        note=text('观察同一公共点 P 处的两条切线',25,MUTED).move_to([0,-5.88,0])
        self.add(condition,eqe,eqh,av,bounds,note)
        self.wait(1.5)
        def tangents(sx=1,sy=1,half=1.22,mark=.23):
            m=model(); p=pos(*m.point(sx,sy)); e,h=[direction(d) for d in m.directions(sx,sy)]
            # True tangent directions, uniform Cartesian scaling, true square corner.
            return VGroup(Line(p-.8*half*e,p+.8*half*e,color=BLUE,stroke_width=3.5),
                          Line(p-.8*half*h,p+.8*half*h,color=ORANGE,stroke_width=3.5),
                          VMobject(color=GREEN,stroke_width=2.6).set_points_as_corners(
                              [p+mark*e,p+mark*(e+h),p+mark*h]))
        main_tangent=always_redraw(tangents)
        angle=always_redraw(lambda:formula(r'90^\circ',30,GREEN).move_to(
                      pos(*model().point())+np.array([.72,.06,0])))
        self.play(FadeIn(main_tangent),FadeIn(angle),run_time=.6)
        self.wait(1.5)
        self.play(tracker.animate.set_value(1.55),run_time=3,rate_func=smooth)
        self.wait(.8)
        self.play(tracker.animate.set_value(.65),run_time=4,rate_func=smooth)
        self.wait(.8)
        self.play(tracker.animate.set_value(1),run_time=2,rate_func=smooth)
        self.wait(.8)
        others=VGroup(*[tangents(sx,sy,half=.62,mark=.19) for sx,sy in [(-1,1),(-1,-1),(1,-1)]])
        result=text('四个公共点处，两条切线都垂直',28,GREEN).move_to(note)
        self.play(FadeIn(others),Transform(note,result),run_time=.5)
        self.wait(2.5)
        self.play(FadeOut(others),FadeOut(main_tangent),FadeOut(angle),
                  Transform(note,text('观察同一公共点 P 处的两条切线',25,MUTED).move_to(note)),run_time=.4)
        self.wait(.6)
