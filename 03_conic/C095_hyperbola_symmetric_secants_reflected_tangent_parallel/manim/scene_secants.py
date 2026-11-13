from manim import *
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).parent))
from model import P,Q,secants,intercept

config.background_color='#F7F8FA'
config.frame_width=9
config.frame_height=16
INK='#213044'; BLUE='#2778BD'; GREEN='#158068'; RED='#B8444F'; ORANGE='#CD6031'; GRAY='#A7B4C2'

class C095ParallelChord(Scene):
    def construct(self):
        def text(s,y,size=28,color=INK):
            t=Text(s,font='Microsoft YaHei',font_size=size,color=color).move_to([0,y,0])
            assert t.width<8.05,(s,t.width)
            return t
        def pt(x,y):return np.array([.95*(x-3.5),.95*(y+1.5)+.8,0])
        def label(s,point,color=INK,size=25):
            return Text(s,font='Microsoft YaHei',font_size=size,color=color).move_to(point)
        self.add(text('割线在转，弦的方向不变',6.9,33))
        self.add(MathTex(r'C:\ \frac{x^2}{2}-y^2=1,\quad P(2,1)',font_size=32,color=BLUE).move_to([0,6.05,0]))
        self.add(text('查结论 · 看图解 · 学证明｜知树 App',-6.7,23),text('公众号 ok-shuxue｜获取入口',-7.25,21))
        self.add(text('仅示右支；横纵单位等长',-5.75,23))
        axes=VGroup(Arrow(pt(0,0),pt(7.1,0),buff=0,color=GRAY,stroke_width=2),
                    Arrow(pt(0,-4.8),pt(0,2),buff=0,color=GRAY,stroke_width=2))
        self.add(axes,label('x',pt(7.15,-.25),size=22),label('y',pt(.2,2.1),size=22))
        for x in [2,4,6]:
            self.add(Line(pt(x,-.07),pt(x,.07),color=GRAY,stroke_width=2),label(str(x),pt(x,-.3),size=18))
        curve=ParametricFunction(lambda y:pt(np.sqrt(2*(1+y*y)),y),t_range=[-4.7,1.7,.025],color=BLUE,stroke_width=3)
        mirror=DashedLine(pt(2,-4.7),pt(2,1.8),color=GREEN,stroke_width=2,dash_length=.12).set_opacity(.65)
        tangent=Line(pt(.2,.8),pt(5.8,-4.8),color=ORANGE,stroke_width=4)
        self.add(curve,mirror,Dot(pt(*P),radius=.065,color=INK),label('P',pt(2.55,1.25)))
        status=text('先找镜像点 Q 处的切线',5.15,29)
        result=MathTex(r'Q(2,-1),\quad \ell_Q:x+y=1',font_size=39,color=ORANGE).move_to([0,-4.65,0])
        self.add(status,result)
        qobjects=VGroup(Dot(pt(*Q),radius=.065,color=ORANGE),label('Q',pt(1.3,-1.25),ORANGE))
        self.play(Create(tangent),FadeIn(qobjects),run_time=1.2)
        self.wait(1.3)
        m=ValueTracker(2)
        def endpoints():return secants(m.get_value())
        segments=always_redraw(lambda:VGroup(Line(pt(*P),pt(*endpoints()[0]),color=GREEN,stroke_width=3),
                                             Line(pt(*P),pt(*endpoints()[1]),color=GREEN,stroke_width=3)))
        chord=always_redraw(lambda:Line(pt(*endpoints()[0]),pt(*endpoints()[1]),color=RED,stroke_width=5))
        points=always_redraw(lambda:VGroup(Dot(pt(*endpoints()[0]),radius=.065,color=RED),Dot(pt(*endpoints()[1]),radius=.065,color=RED)))
        lm=always_redraw(lambda:label('M',pt(*endpoints()[0])+np.array([-.38,-.25,0]),RED))
        ln=always_redraw(lambda:label('N',pt(*endpoints()[1])+np.array([.3,.23,0]),RED))
        legend=text('绿：对称割线   红：弦   橙：切线',-3.05,25)
        # Numerals update from the very same model as the moving points.
        mnumber=DecimalNumber(2,num_decimal_places=2,font_size=33,color=GREEN)
        mnumber.add_updater(lambda d:d.set_value(m.get_value()))
        tnumber=DecimalNumber(intercept(2),num_decimal_places=2,font_size=33,color=RED)
        tnumber.add_updater(lambda d:d.set_value(intercept(m.get_value())))
        readout=VGroup(MathTex('m=',font_size=33,color=GREEN),mnumber,
                      MathTex(r'x_M+y_M=x_N+y_N\approx',font_size=29,color=RED),tnumber)
        readout.arrange(RIGHT,buff=.2).move_to([0,-3.85,0])
        assert readout.width<8.05
        def change(caption,tex,color=RED):
            nonlocal status,result
            self.play(FadeOut(status),FadeOut(result),run_time=.15)
            status=text(caption,5.15,29)
            result=MathTex(tex,font_size=39,color=color).move_to([0,-4.65,0])
            self.play(FadeIn(status),FadeIn(result),run_time=.15)
        change('两条割线始终关于 x=2 对称',r'k_{PM}=m,\quad k_{PN}=-m',GREEN)
        self.add(segments,chord,points,lm,ln,legend,readout)
        self.wait(1.5)
        self.play(m.animate.set_value(1.25),run_time=4,rate_func=smooth)
        self.wait(1.5)
        change('位置改变，弦与切线始终平行',r'MN\parallel\ell_Q,\quad k_{MN}=-1')
        self.play(m.animate.set_value(2.5),run_time=4,rate_func=smooth)
        self.wait(2)
        self.play(m.animate.set_value(2),run_time=3,rate_func=smooth)
        change('两条割线始终关于 x=2 对称',r'k_{PM}=m,\quad k_{PN}=-m',GREEN)
        self.wait(2)
        self.play(*[FadeOut(o) for o in [segments,chord,points,lm,ln,legend,readout,tangent,qobjects]],run_time=1)
        change('先找镜像点 Q 处的切线',r'Q(2,-1),\quad \ell_Q:x+y=1',ORANGE)
        self.wait(.5)
