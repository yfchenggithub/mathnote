import math
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from manim import *
from model import point, tangent, slopes, clip_line

config.background_color='#F7F8FA'
config.frame_width=9
config.frame_height=16
INK='#213044'
MUTED='#526275'
BLUE='#2778BD'
ORANGE='#CD6031'
GREEN='#158068'
AXIS='#A7B4C2'


class C011SlopeProduct(Scene):
    def construct(self):
        def cn(s,size=28,color=INK):
            return Text(s,font='Microsoft YaHei',font_size=size,color=color)
        def eq(s,size=36,color=INK):
            return MathTex(s,font_size=size,color=color)
        def xy(p):
            return np.array([1.42*p[0],1.42*p[1]+.8,0])
        title=cn('切线与 OP：斜率积不变',32).move_to([0,6.9,0])
        subtitle=eq(r'\frac{x^2}{4}+y^2=1',32).move_to([0,5.9,0])
        caption=cn('切点移动，两个斜率怎样变化？',25).move_to([0,4.85,0])
        axes=VGroup(Line(xy((-2.65,0)),xy((2.65,0)),color=AXIS,stroke_width=1.7),Line(xy((0,-2.15)),xy((0,2.15)),color=AXIS,stroke_width=1.7))
        labels=VGroup(eq('O',25).move_to(xy((-.16,-.23))),eq('x',25).move_to(xy((2.62,-.22))),eq('y',25).move_to(xy((-.18,2.12))))
        ellipse=ParametricFunction(lambda u:xy(point(u)),t_range=[0,TAU],color=INK,stroke_width=3.6)
        theta=ValueTracker(PI/4)
        radial=always_redraw(lambda:Line(xy((0,0)),xy(point(theta.get_value())),color=BLUE,stroke_width=5))
        tang=always_redraw(lambda:Line(*[xy(p) for p in clip_line(*tangent(theta.get_value()))],color=ORANGE,stroke_width=4))
        dot=always_redraw(lambda:Dot(xy(point(theta.get_value())),radius=.075,color=ORANGE))
        plabel=always_redraw(lambda:eq('P',27).move_to(xy(point(theta.get_value()))+np.array([.23,.3,0])))
        legend=VGroup(cn('中心连线 OP',23,BLUE),cn('切线 ℓ',23,ORANGE)).arrange(RIGHT,buff=.7).move_to([0,-2.9,0])
        def readout(index,symbol,color,x):
            lab=eq(symbol+r'\approx',34,color)
            num=DecimalNumber(-8.88,num_decimal_places=2,font_size=34,color=color)
            group=VGroup(lab,num).arrange(RIGHT,buff=.12).move_to([x,-3.85,0])
            anchor=num.get_right().copy()
            num.add_updater(lambda m:m.set_value(slopes(theta.get_value())[index]).align_to(anchor,RIGHT))
            num.update(0)
            return group
        numbers=VGroup(readout(0,'k_{OP}',BLUE,-1.9),readout(1,r'k_\ell',ORANGE,1.9))
        result=eq(r'k_\ell\,k_{OP}=-\frac14',43,GREEN).move_to([0,-5.05,0])
        foot=cn('当前切点不在坐标轴上',23,MUTED).move_to([0,-6.5,0])
        self.add(title,subtitle,caption,axes,labels,ellipse,radial,tang,dot,plabel,legend,numbers,result,foot)
        self.wait(1.5)
        self.play(theta.animate.set_value(20*DEGREES),run_time=2)
        self.wait(.7)
        self.play(theta.animate.set_value(70*DEGREES),run_time=3)
        self.wait(.7)
        self.play(theta.animate.set_value(PI/4),run_time=1.5)
        self.play(Transform(caption,cn('一个变大，另一个的绝对值变小',25).move_to(caption)),run_time=.3)
        self.wait(1)
        proof=VGroup(eq(r'k_{OP}=\frac{y_0}{x_0}',35,BLUE),eq(r'k_\ell=-\frac{b^2x_0}{a^2y_0}',35,ORANGE)).arrange(RIGHT,buff=.65).move_to([0,-3.85,0])
        general=eq(r'k_\ell\,k_{OP}=-\frac{b^2}{a^2}=e^2-1',38,GREEN).move_to([0,-5.2,0])
        self.play(FadeOut(numbers),FadeIn(proof),Transform(result,general),Transform(caption,cn('为什么不变？相乘后消去切点坐标',25).move_to(caption)),Transform(foot,eq(r'a>b>0,\quad x_0y_0\ne0',29,MUTED).move_to(foot)),run_time=.4)
        self.wait(3)
        self.play(FadeOut(proof),FadeOut(result),Transform(caption,cn('轴顶点要单独判断',27).move_to(caption)),Transform(foot,cn('先看两条直线的斜率是否存在',23,MUTED).move_to(foot)),run_time=.4)
        self.play(theta.animate.set_value(0),run_time=1.2)
        exception=VGroup(cn('OP 水平，切线竖直',27),cn('切线斜率不存在',27,ORANGE),cn('斜率积无定义',31,GREEN)).arrange(DOWN,buff=.32).move_to([0,-4.6,0])
        self.play(FadeIn(exception),run_time=.3)
        self.wait(1.6)
        self.play(FadeOut(exception),run_time=.25)
        self.play(theta.animate.set_value(PI/2),run_time=1.4)
        exception2=VGroup(cn('OP 竖直，切线水平',27),cn('OP 斜率不存在',27,BLUE),cn('斜率积无定义',31,GREEN)).arrange(DOWN,buff=.32).move_to([0,-4.6,0])
        self.play(FadeIn(exception2),run_time=.3)
        self.wait(1.6)
        self.play(FadeOut(exception2),run_time=.25)
        self.play(theta.animate.set_value(PI/4),run_time=1.2)
        result.become(eq(r'k_\ell\,k_{OP}=-\frac14',43,GREEN).move_to([0,-5.05,0]))
        self.play(FadeIn(numbers),FadeIn(result),Transform(caption,cn('切点移动，两个斜率怎样变化？',25).move_to(caption)),Transform(foot,cn('当前切点不在坐标轴上',23,MUTED).move_to(foot)),run_time=.4)
        self.wait(1.2)
