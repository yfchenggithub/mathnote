"""C005: compare sin(theta/2) with e, then change the ellipse shape."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from model import FocalBoundModel, START, RIGHT_THRESHOLD, ANGLE120_THRESHOLD
from manim import *
import numpy as np

config.background_color='#F7F8FA'
config.frame_width,config.frame_height=9,16
INK,MUTED,BLUE,ORANGE,GREEN,AXIS='#213044','#526275','#2778BD','#CD6031','#158068','#A7B4C2'


class C005EccentricityBound(Scene):
    def construct(self):
        eccentricity,parameter=ValueTracker(.6),ValueTracker(START)
        def model():
            return FocalBoundModel(e=eccentricity.get_value())
        origin=np.array([0.,.5,0.]); scale=.65
        def xy(x,y):
            return origin+scale*np.array([x,y,0.])
        def text(s,size=28,color=INK):
            return Text(s,font='Microsoft YaHei',font_size=size,color=color)
        def note(s,size=35,color=INK):
            return MathTex(s,font_size=size,color=color).move_to([0,-6.9,0])
        title=text('离心率如何限制焦角？',38).move_to([0,6.92,0])
        subtitle=text('半角正弦的上界，就是离心率',27,MUTED).move_to([0,6.05,0])
        bound=MathTex(r'\sin\frac\theta2\leq e',font_size=49,color=INK).move_to([0,5.15,0])
        condition=MathTex(r'a=5,\quad b=5\sqrt{1-e^2},\quad0<e<1',font_size=29,color=MUTED).move_to([0,4.22,0])
        axes=VGroup(Line(xy(-5.6,0),xy(5.6,0)),Line(xy(0,-4.6),xy(0,4.6))).set_stroke(AXIS,1.4)
        ellipse=always_redraw(lambda:ParametricFunction(lambda t:xy(*model().point(t)),t_range=[0,TAU],stroke_width=3.8,color=BLUE))
        def triangle():
            m=model();p=xy(*m.point(parameter.get_value())); f1,f2=xy(-m.c,0),xy(m.c,0)
            u,v=f1-p,f2-p
            sweep=np.arctan2(u[0]*v[1]-u[1]*v[0],np.dot(u,v))
            projection=p.copy();projection[1]=origin[1]
            return VGroup(Polygon(f1,f2,p,fill_color=BLUE,fill_opacity=.065,stroke_width=0),
                          Line(p,f1,color=ORANGE,stroke_width=3.5),Line(p,f2,color=ORANGE,stroke_width=3.5),
                          DashedLine(projection,p,color=GREEN,dash_length=.09,stroke_width=2),
                          Arc(radius=.45,start_angle=np.arctan2(u[1],u[0]),angle=sweep,arc_center=p,color=ORANGE,stroke_width=3),
                          Dot(p,radius=.085,color=ORANGE),MathTex('P',font_size=30,color=ORANGE).next_to(p,UP,buff=.14))
        moving=always_redraw(triangle)
        foci=always_redraw(lambda:VGroup(*[Dot(xy(sign*model().c,0),radius=.065,color=INK) for sign in (-1,1)]))
        focus_labels=always_redraw(lambda:VGroup(MathTex('F_1',font_size=28,color=INK).next_to(xy(-model().c,0),DOWN,buff=.17),MathTex('F_2',font_size=28,color=INK).next_to(xy(model().c,0),DOWN,buff=.17)))
        o=MathTex('O',color=MUTED,font_size=24).next_to(origin,DOWN,buff=.16)
        angle_label=MathTex(r'\theta=\angle F_1PF_2=',color=INK,font_size=32)
        degrees=DecimalNumber(180,num_decimal_places=1,color=ORANGE,font_size=36)
        degree_sign=MathTex(r'{}^\circ',color=ORANGE,font_size=33)
        readout=VGroup(angle_label,degrees,degree_sign).arrange(RIGHT,buff=.1).move_to([0,-2.95,0])
        angle_anchor=degrees.get_right().copy()
        degrees.add_updater(lambda m:m.set_value(model().angle(parameter.get_value())*180/PI).align_to(angle_anchor,RIGHT));degrees.update(0)
        # Two tracks use exactly the same [0,1] scale; no independent rescaling.
        x0,x1=-1.15,2.25
        qy,ey=-3.95,-4.65
        tracks=VGroup(Line([x0,qy,0],[x1,qy,0]),Line([x0,ey,0],[x1,ey,0])).set_stroke('#D7DFE7',9)
        gauge_labels=VGroup(MathTex(r'\sin\frac\theta2',color=ORANGE,font_size=30).move_to([-2.65,qy,0]),MathTex(r'e=\frac ca',color=BLUE,font_size=30).move_to([-2.65,ey,0]))
        bars=always_redraw(lambda:VGroup(Line([x0,qy,0],[x0+(x1-x0)*model().half_sine(parameter.get_value()),qy,0],color=ORANGE,stroke_width=9),Line([x0,ey,0],[x0+(x1-x0)*eccentricity.get_value(),ey,0],color=BLUE,stroke_width=9)))
        qnum=DecimalNumber(.999,num_decimal_places=3,color=ORANGE,font_size=30).move_to([3.14,qy,0])
        enum=DecimalNumber(.999,num_decimal_places=3,color=BLUE,font_size=30).move_to([3.14,ey,0])
        qa,ea=qnum.get_right().copy(),enum.get_right().copy()
        qnum.add_updater(lambda m:m.set_value(model().half_sine(parameter.get_value())).align_to(qa,RIGHT));qnum.update(0)
        enum.add_updater(lambda m:m.set_value(eccentricity.get_value()).align_to(ea,RIGHT));enum.update(0)
        ticks=VGroup(MathTex('0',font_size=22,color=MUTED).move_to([x0,-5.13,0]),MathTex('1',font_size=22,color=MUTED).move_to([x1,-5.13,0]))
        state=text('普通位置：半角正弦严格小于 e',28).move_to([0,-5.88,0])
        footer=note(r'PF_1+PF_2=2a')
        self.add(title,subtitle,bound,condition,axes,ellipse,moving,foci,focus_labels,o,readout,tracks,gauge_labels,bars,qnum,enum,ticks,state,footer)
        self.wait(1.3)
        def caption(s,color=INK):
            self.play(Transform(state,text(s,27,color).move_to([0,-5.88,0])),run_time=.3)
        caption('移向短轴端点，两条焦半径逐渐相等')
        self.play(parameter.animate.set_value(PI/2),run_time=2.5,rate_func=smooth)
        caption('短轴两端点取等：半角正弦达到 e',GREEN)
        markers=always_redraw(lambda:VGroup(*[Circle(radius=.15,color=GREEN,stroke_width=3).move_to(xy(0,sign*model().b)) for sign in (-1,1)]))
        self.add(markers)
        self.play(Transform(footer,note(r'PF_1=PF_2=a,\quad P=(0,\pm b)',33,GREEN)),run_time=.3)
        self.wait(1.4)
        caption('固定 a：椭圆越扁，最大焦角越大')
        self.play(Transform(footer,note(r'\theta_{\max}=2\arcsin e',40,GREEN)),run_time=.3)
        self.play(eccentricity.animate.set_value(RIGHT_THRESHOLD),run_time=2,rate_func=smooth)
        caption('直角的门槛：最大焦角恰为 90°',GREEN)
        self.play(Transform(footer,note(r'e=\frac{\sqrt2}{2}\quad\Rightarrow\quad\theta_{\max}=90^\circ',34,GREEN)),run_time=.3)
        self.wait(1.4)
        caption('继续增大 e，最大焦角继续增大')
        self.play(eccentricity.animate.set_value(ANGLE120_THRESHOLD),run_time=2.2,rate_func=smooth)
        caption('120° 的门槛：恰在短轴端点取到',GREEN)
        self.play(Transform(footer,note(r'e=\frac{\sqrt3}{2}\quad\Rightarrow\quad\theta_{\max}=120^\circ',34,GREEN)),run_time=.3)
        self.wait(1.4)
        caption('超过门槛后，最大焦角超过 120°')
        self.play(Transform(footer,note(r'\theta_{\max}=2\arcsin e',40,GREEN)),run_time=.3)
        self.play(eccentricity.animate.set_value(.9),run_time=1.5,rate_func=smooth)
        self.wait(.6)
        target=FocalBoundModel(e=.9).parameter_for_angle(2*PI/3)
        caption('离开短轴端点，也能取得 120°')
        self.play(parameter.animate.set_value(target),run_time=1.8,rate_func=smooth)
        self.play(Transform(footer,note(r'\exists P:\ \theta=120^\circ\iff e\geq\frac{\sqrt3}{2}',32,GREEN)),run_time=.3)
        self.wait(1.5)
        caption('减小 e，回到原来的椭圆')
        self.remove(markers)
        self.play(eccentricity.animate.set_value(.6),parameter.animate.set_value(START),run_time=2.5,rate_func=smooth)
        caption('e=0.6：所有焦角都小于 120°')
        self.wait(.8)
        self.play(Transform(state,text('普通位置：半角正弦严格小于 e',28).move_to([0,-5.88,0])),Transform(footer,note(r'PF_1+PF_2=2a')),run_time=.4)
        self.wait(.8)
