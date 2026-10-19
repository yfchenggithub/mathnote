"""C007: translate a fixed-slope line, observe root merger, then both tangents."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from model import SlopeTangentModel,clip_line
from manim import *
import numpy as np

config.background_color='#F7F8FA'
config.frame_width,config.frame_height=9,16
INK,MUTED,BLUE,ORANGE,GREEN,AXIS='#213044','#526275','#2778BD','#CD6031','#158068','#A7B4C2'


class C007SlopeTangentCondition(Scene):
    def construct(self):
        model=SlopeTangentModel(); intercept=ValueTracker(2)
        origin=np.array([0.,.65,0.])
        def xy(x,y):
            return origin+np.array([x,y,0.])
        def text(s,size=28,color=INK):
            return Text(s,font='Microsoft YaHei',font_size=size,color=color)
        def formula(s,size=37,color=INK):
            return MathTex(s,font_size=size,color=color).move_to([0,-6.35,0])
        def drawn_line(m,color=ORANGE,width=3.7):
            ends=clip_line(model.k,m)
            return Line(xy(*ends[0]),xy(*ends[1]),color=color,stroke_width=width)
        title=text('直线何时恰好相切？',39).move_to([0,6.92,0])
        subtitle=text('固定斜率，平行移动直线',28,MUTED).move_to([0,6.03,0])
        equation=MathTex(r'\frac{x^2}{9}+\frac{y^2}{4}=1',font_size=37,color=INK).move_to([0,5.08,0])
        line_equation=MathTex(r'l:\ y=\frac12x+m',font_size=34,color=ORANGE).move_to([0,4.23,0])
        axes=VGroup(Line(xy(-3.65,0),xy(3.65,0)),Line(xy(0,-3.05),xy(0,3.05))).set_stroke(AXIS,1.4)
        axes_labels=VGroup(MathTex('O',font_size=24,color=MUTED).next_to(origin,DOWN,buff=.16),
                           MathTex('x',font_size=25,color=MUTED).next_to(xy(3.65,0),DOWN,buff=.1),
                           MathTex('y',font_size=25,color=MUTED).next_to(xy(0,3.05),LEFT,buff=.12))
        ellipse=ParametricFunction(lambda t:xy(model.a*np.cos(t),model.b*np.sin(t)),t_range=[0,TAU],stroke_width=3.8,color=BLUE)
        moving=always_redraw(lambda:drawn_line(intercept.get_value()))
        y_intercept=always_redraw(lambda:Dot(xy(0,intercept.get_value()),radius=.045,color=ORANGE))
        def points():
            roots=model.intersections(intercept.get_value())
            dots=VGroup(*[Dot(xy(x,y),radius=.085,color=GREEN) for x,y in roots])
            if len(roots)==1:
                pos=xy(*roots[0]); direction=UL if intercept.get_value()>0 else DR
                dots.add(Circle(radius=.16,color=GREEN,stroke_width=2.5).move_to(pos),
                         MathTex('T',font_size=30,color=GREEN).next_to(pos,direction,buff=.17))
            return dots
        intersection_points=always_redraw(points)
        mlabel=MathTex('m=',font_size=34,color=INK)
        mnum=DecimalNumber(-3,num_decimal_places=2,include_sign=True,font_size=34,color=ORANGE)
        mreadout=VGroup(mlabel,mnum).arrange(RIGHT,buff=.1).move_to([-2,-3.2,0])
        ma=mnum.get_right().copy()
        mnum.add_updater(lambda m:m.set_value(intercept.get_value()).align_to(ma,RIGHT));mnum.update(0)
        names={0:'相离 · 无交点',1:'相切 · 一个切点',2:'相交 · 两个交点'}
        count_label=always_redraw(lambda:text(names[model.count(intercept.get_value())],27,GREEN if model.count(intercept.get_value())==1 else INK).move_to([1.65,-3.2,0]))
        square_label=MathTex(r'm^2=',font_size=34,color=INK)
        square=DecimalNumber(9.99,num_decimal_places=2,font_size=35,color=ORANGE)
        sign_space=MathTex('=',font_size=38,color=INK)
        rhs=MathTex(r'6.25=S',font_size=34,color=INK)
        comparison=VGroup(square_label,square,sign_space,rhs).arrange(RIGHT,buff=.18).move_to([0,-4.35,0])
        sqanchor=square.get_right().copy(); sign_position=sign_space.get_center().copy()
        square.add_updater(lambda m:m.set_value(intercept.get_value()**2).align_to(sqanchor,RIGHT));square.update(0)
        def symbol():
            count=model.count(intercept.get_value())
            return MathTex({0:'>',1:'=',2:'<'}[count],font_size=38,color=GREEN if count==1 else INK).move_to(sign_position)
        self.remove(sign_space);comparison.remove(sign_space)
        relation=always_redraw(symbol)
        state=text('两个交点：截距平方小于临界值',28).move_to([0,-5.35,0])
        footer=formula(r'S=a^2k^2+b^2=\frac{25}{4}')
        caveat=text('竖直切线 x = ±a 不在斜率式内',22,MUTED).move_to([0,-7.25,0])
        self.add(title,subtitle,equation,line_equation,axes,axes_labels,ellipse,moving,y_intercept,intersection_points,mreadout,count_label,comparison,relation,state,footer,caveat)
        self.wait(1.2)
        def caption(s,color=INK):
            self.play(Transform(state,text(s,28,color).move_to([0,-5.35,0])),run_time=.3)
        caption('直线上移，两个交点逐渐合并')
        self.play(intercept.animate.set_value(model.critical),run_time=2.4,rate_func=smooth)
        caption('恰好相切：截距平方等于临界值',GREEN)
        self.play(Transform(footer,formula(r'm^2=a^2k^2+b^2',43,GREEN)),run_time=.3)
        self.wait(1.6)
        caption('继续上移：直线与椭圆相离')
        self.play(intercept.animate.set_value(3),Transform(footer,formula(r'S=a^2k^2+b^2=\frac{25}{4}')),run_time=1.7,rate_func=smooth)
        self.wait(1.2)
        caption('向下平移，重新穿过椭圆中心')
        self.play(intercept.animate.set_value(0),run_time=2.6,rate_func=smooth)
        self.wait(.6)
        caption('继续下移，走向另一条平行切线')
        self.play(intercept.animate.set_value(-model.critical),run_time=2.4,rate_func=smooth)
        caption('负截距也能相切，不能漏掉负号',GREEN)
        self.play(Transform(footer,formula(r'm=-\frac52,\quad T=\left(\frac95,-\frac85\right)',35,GREEN)),run_time=.3)
        self.wait(1.4)
        upper_m,upper_t=model.tangent(1)
        ghost=VGroup(DashedVMobject(drawn_line(upper_m,BLUE,2.7),num_dashes=35),Circle(radius=.13,color=BLUE,stroke_width=2.5).move_to(xy(*upper_t)))
        ghost_label=MathTex(r'm=+2.5',font_size=25,color=BLUE).move_to([-2.65,2.64,0])
        self.play(FadeIn(ghost),FadeIn(ghost_label),run_time=.4)
        caption('同一斜率，对应两条平行切线',GREEN)
        self.play(Transform(footer,formula(r'y=kx\pm\sqrt{a^2k^2+b^2}',37,GREEN)),run_time=.3)
        self.wait(1.6)
        caption('回到相交位置，再观察一次')
        self.play(FadeOut(ghost),FadeOut(ghost_label),run_time=.3)
        self.play(intercept.animate.set_value(2),Transform(footer,formula(r'S=a^2k^2+b^2=\frac{25}{4}')),run_time=2.6,rate_func=smooth)
        self.play(Transform(state,text('两个交点：截距平方小于临界值',28).move_to([0,-5.35,0])),run_time=.3)
        self.wait(.7)
