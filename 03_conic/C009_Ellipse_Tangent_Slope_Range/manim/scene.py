"""C009: free directions versus point-constrained slopes and vertical exceptions."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from model import SlopeRangeModel,clip_line
from manim import *
import numpy as np

config.background_color='#F7F8FA'
config.frame_width,config.frame_height=9,16
INK,MUTED,BLUE,ORANGE,GREEN,AXIS='#213044','#526275','#2778BD','#CD6031','#158068','#A7B4C2'


class C009TangentSlopeRange(Scene):
    def construct(self):
        model=SlopeRangeModel(); kval=ValueTracker(-1); mx=ValueTracker(0); my=ValueTracker(2)
        visible=ValueTracker(1); phase=0
        origin=np.array([0.,.65,0.]);scale=1.4
        def xy(x,y):
            return origin+scale*np.array([x,y,0.])
        def text(s,size=28,color=INK):
            return Text(s,font='Microsoft YaHei',font_size=size,color=color)
        def formula(s,size=38,color=INK):
            return MathTex(s,font_size=size,color=color).move_to([0,-5.65,0])
        def point():
            return mx.get_value(),my.get_value()
        title=text('切线斜率能取哪些值？',38).move_to([0,6.92,0])
        subtitle=text('方向任取，每个有限斜率配两条切线',26,MUTED).move_to([0,6.02,0])
        ellipse_eq=MathTex(r'\frac{x^2}{4}+y^2=1',font_size=38,color=INK).move_to([0,5.1,0])
        rule=MathTex(r'y=kx\pm\sqrt{4k^2+1}',font_size=37,color=INK).move_to([0,4.17,0])
        axes=VGroup(Line(xy(-2.75,0),xy(2.75,0)),Line(xy(0,-2.25),xy(0,2.25))).set_stroke(AXIS,1.4)
        labels=VGroup(MathTex('O',font_size=24,color=MUTED).next_to(origin,DOWN,buff=.15),MathTex('x',font_size=24,color=MUTED).next_to(xy(2.75,0),DOWN,buff=.1))
        ellipse=ParametricFunction(lambda t:xy(model.a*np.cos(t),model.b*np.sin(t)),t_range=[0,TAU],color=BLUE,stroke_width=3.8)
        def geometry():
            pairs=model.parallel_pair(kval.get_value()) if phase==0 else model.point_tangents(point())
            objects=VGroup()
            for i,(line,touch) in enumerate(pairs):
                color=(ORANGE,GREEN)[i]
                ends=clip_line(*line)
                objects.add(Line(xy(*ends[0]),xy(*ends[1]),color=color,stroke_width=3.5),Dot(xy(*touch),radius=.075,color=color))
            if phase==1:
                p=xy(*point())
                objects.add(Dot(p,radius=.08,color=INK),MathTex('M',font_size=29,color=INK).next_to(p,RIGHT,buff=.15))
            return objects.fade(1-visible.get_value())
        drawing=always_redraw(geometry)
        kdigits=DecimalNumber(-2,num_decimal_places=2,include_sign=True,font_size=37,color=ORANGE)
        kinfo=VGroup(MathTex('k=',font_size=36,color=INK),kdigits).arrange(RIGHT,buff=.12).move_to([0,-3.3,0])
        ka=kdigits.get_right().copy();kdigits.add_updater(lambda o:o.set_value(kval.get_value()).align_to(ka,RIGHT));kdigits.update(0)
        xdigits=DecimalNumber(-2,num_decimal_places=2,font_size=33,color=INK)
        ydigits=DecimalNumber(-2,num_decimal_places=2,font_size=33,color=INK)
        minfo=VGroup(MathTex('M=(',font_size=33,color=INK),xdigits,MathTex(',',font_size=33,color=INK),ydigits,MathTex(')',font_size=33,color=INK)).arrange(RIGHT,buff=.1).move_to([0,-3.3,0])
        xa,ya=xdigits.get_right().copy(),ydigits.get_right().copy()
        xdigits.add_updater(lambda o:o.set_value(mx.get_value()).align_to(xa,RIGHT));xdigits.update(0)
        ydigits.add_updater(lambda o:o.set_value(my.get_value()).align_to(ya,RIGHT));ydigits.update(0)
        state=text('指定方向，总能找到两条平行切线',28).move_to([0,-4.4,0])
        result=formula(r'k\in\mathbb R',44,GREEN)
        note=text('竖直切线 x=±2 没有斜率',25,MUTED).move_to([0,-6.9,0])
        self.add(title,subtitle,ellipse_eq,rule,axes,labels,ellipse,drawing,kinfo,state,result,note)
        self.wait(1)
        def caption(s,color=INK):
            self.play(Transform(state,text(s,28,color).move_to([0,-4.4,0])),run_time=.3)
        caption('从负斜率转到零斜率，再转到正斜率')
        self.play(kval.animate.set_value(0),run_time=1.8,rate_func=smooth);self.wait(.6)
        self.play(kval.animate.set_value(2),run_time=2.6,rate_func=smooth);self.wait(.8)
        self.play(visible.animate.set_value(0),FadeOut(kinfo),run_time=.3)
        phase=1;drawing.update(0)
        self.play(Transform(title,text('固定外点后，斜率不再任意',35).move_to([0,6.92,0])),
                  Transform(subtitle,text('两条切线，对应两个有限斜率',27,MUTED).move_to([0,6.02,0])),
                  Transform(rule,MathTex(r'4k^2-3=0',font_size=38,color=INK).move_to([0,4.17,0])),
                  Transform(state,text('过 M(0,2)：斜率只能取这两个值',28).move_to([0,-4.4,0])),
                  Transform(result,formula(r'k_1=\frac{\sqrt3}{2},\quad k_2=-\frac{\sqrt3}{2}',37,GREEN)),
                  Transform(note,text('这里两条切线的斜率都存在',25,MUTED).move_to([0,-6.9,0])),FadeIn(minfo),run_time=.4)
        self.play(visible.animate.set_value(1),run_time=.3);self.wait(1.5)
        caption('M 横向移动，一条切线逐渐竖直')
        self.play(Transform(rule,MathTex(r'(4-x_0^2)k^2+2x_0y_0k+1-y_0^2=0',font_size=29,color=INK).move_to([0,4.17,0])),
                  Transform(result,formula(r'(y_0-kx_0)^2=4k^2+1',36)),run_time=.3)
        self.play(mx.animate.set_value(2),run_time=2.7,rate_func=smooth)
        caption('仍有两条切线，但只有一个有限斜率',GREEN)
        self.play(Transform(subtitle,text('两条切线，未必有两个有限斜率',26,MUTED).move_to([0,6.02,0])),
                  Transform(rule,MathTex(r'0k^2+8k-3=0',font_size=39,color=INK).move_to([0,4.17,0])),
                  Transform(result,formula(r'k=\frac38,\qquad x=2',40,GREEN)),
                  Transform(note,text('方程只求有限斜率；竖直切线须补上',25,GREEN).move_to([0,-6.9,0])),run_time=.3)
        self.wait(2)
        caption('沿 x=2 下移，走向长轴端点')
        self.play(Transform(title,text('点的位置，决定切线条数',37).move_to([0,6.92,0])),
                  Transform(subtitle,text('先数切线，再数有限斜率',27,MUTED).move_to([0,6.02,0])),
                  Transform(rule,MathTex(r'4y_0k+1-y_0^2=0',font_size=35,color=INK).move_to([0,4.17,0])),
                  Transform(result,formula(r'S=1+y_0^2',39)),
                  Transform(note,text('外点始终有两条实切线',25,MUTED).move_to([0,-6.9,0])),run_time=.3)
        self.play(my.animate.set_value(0),run_time=2.5,rate_func=smooth)
        caption('椭圆上的长轴端点：只有竖直切线',GREEN)
        no_slope=VGroup(MathTex(r'1=0',font_size=38,color=INK),text('斜率方程无解',25,MUTED)).arrange(RIGHT,buff=.22).move_to([0,4.17,0])
        self.play(Transform(rule,no_slope),
                  Transform(result,formula(r'x=2\quad(S=1)',42,GREEN)),
                  Transform(note,text('一条切线；没有有限斜率',25,GREEN).move_to([0,-6.9,0])),run_time=.3)
        self.wait(1.1)
        caption('进入椭圆内部，不存在实切线')
        self.play(Transform(rule,MathTex(r'S=\frac{x_0^2}{4}+y_0^2',font_size=36,color=INK).move_to([0,4.17,0])),Transform(result,formula(r'S<1',43)),Transform(note,text('按直线条数计数：外 2、上 1、内 0',25,MUTED).move_to([0,-6.9,0])),run_time=.3)
        self.play(mx.animate.set_value(1),run_time=1.2,rate_func=smooth);self.wait(1)
        self.play(visible.animate.set_value(0),FadeOut(minfo),run_time=.3)
        phase=0;kval.set_value(-1);mx.set_value(0);my.set_value(2);kdigits.update(0);drawing.update(0)
        self.play(Transform(title,text('切线斜率能取哪些值？',38).move_to([0,6.92,0])),
                  Transform(subtitle,text('方向任取，每个有限斜率配两条切线',26,MUTED).move_to([0,6.02,0])),
                  Transform(rule,MathTex(r'y=kx\pm\sqrt{4k^2+1}',font_size=37,color=INK).move_to([0,4.17,0])),
                  Transform(state,text('指定方向，总能找到两条平行切线',28).move_to([0,-4.4,0])),
                  Transform(result,formula(r'k\in\mathbb R',44,GREEN)),
                  Transform(note,text('竖直切线 x=±2 没有斜率',25,MUTED).move_to([0,-6.9,0])),FadeIn(kinfo),run_time=.4)
        self.play(visible.animate.set_value(1),run_time=.3);self.wait(.6)
