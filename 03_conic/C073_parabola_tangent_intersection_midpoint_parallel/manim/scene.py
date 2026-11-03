from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from model import Configuration
from manim import *

config.frame_width=9
config.frame_height=16
config.background_color='#F7F8FA'

INK='#213044'
MUTED='#526275'
BLUE='#2778BD'
ORANGE='#CD6031'
GREEN='#158068'
PURPLE='#8055B2'
AXIS='#A7B4C2'
FONT='Microsoft YaHei'


class C073TangentMidpoint(Scene):
    def construct(self):
        def text(s,size=25,color=INK):
            return Text(s,font=FONT,font_size=size,color=color)
        def xy(pt):
            return np.array([-1.35+.88*pt[0], .65+.88*pt[1],0])

        b=ValueTracker(4)
        def state(): return Configuration(2,-2,b.get_value())
        title=text('切线交点与弦中点，为何同高？',30).move_to([0,6.9,0])
        subtitle=text('y² = 4x  ·  固定 A，沿抛物线移动 B',23,MUTED).move_to([0,6.15,0])
        footer=VGroup(text('查结论 · 看图解 · 学证明｜知树 App',22,MUTED),
                      text('公众号 ok-shuxue｜获取入口',20,MUTED)).arrange(DOWN,buff=.22).move_to([0,-6.95,0])
        self.add(title,subtitle,footer)
        axes=VGroup(Line(xy((-2.5,0)),xy((5,0)),color=AXIS,stroke_width=1.8),
                    Line(xy((0,-2.65)),xy((0,4.65)),color=AXIS,stroke_width=1.8))
        axis_labels=VGroup(text('x',22,MUTED).move_to(xy((5.25,0))),
                           text('y',22,MUTED).move_to(xy((0,4.95))),
                           text('O',19,MUTED).move_to(xy((-.22,-.28))))
        curve=ParametricFunction(lambda y:xy((y*y/4,y)),t_range=[-2.65,4.4],color=BLUE,stroke_width=3.5)
        curve_label=MathTex('y^2=4x',font_size=27,color=BLUE).move_to([2.8,5.2,0])
        self.add(axes,axis_labels,curve,curve_label)
        point_labels={name:text(name,25,color) for name,color in [('A',BLUE),('B',BLUE),('M',PURPLE),('N',GREEN)]}
        def diagram():
            c=state()
            tangents=VGroup(*[Line(*[xy(pt) for pt in c.tangent_segment(y)],color=ORANGE,stroke_width=2.7) for y in (-2,c.b)])
            chord=Line(xy(c.A),xy(c.B),color=MUTED,stroke_width=2.4)
            guide=DashedLine(xy((-2.5,c.M[1])),xy((5,c.M[1])),color=GREEN,stroke_width=1.3,dash_length=.09).set_opacity(.5)
            segment=Line(xy(c.M),xy(c.N),color=GREEN,stroke_width=6)
            dots=VGroup(Dot(xy(c.A),radius=.065,color=BLUE),Dot(xy(c.B),radius=.065,color=BLUE),
                        Dot(xy(c.M),radius=.078,color=PURPLE),Dot(xy(c.N),radius=.078,color=GREEN))
            tangent=np.array([c.b/2,1,0]); tangent=tangent/np.linalg.norm(tangent)
            normal=np.array([tangent[1],-tangent[0],0])
            b_offset=.5*normal+.35*tangent
            labels=VGroup(point_labels['A'].copy().move_to(xy(c.A)+[.55,-.08,0]),
                          point_labels['B'].copy().move_to(xy(c.B)+b_offset),
                          point_labels['M'].copy().move_to(xy(c.M)+[-.55,.24,0]),
                          point_labels['N'].copy().move_to(xy(c.N)+[.35,-.35,0]))
            return VGroup(guide,tangents,chord,segment,dots,labels)
        drawing=always_redraw(diagram)
        self.add(drawing)
        legend=text('橙：两条切线   灰：弦 AB   绿：MN',21,MUTED).move_to([0,-2.65,0])
        self.add(legend)
        status=text('B 在动，M 与 N 始终处于同一高度',26,GREEN).move_to([0,-3.45,0])
        formula=MathTex(r'y_M=y_N=\frac{y_A+y_B}{2}',font_size=36,color=INK).move_to([0,-4.3,0])
        live_label=text('当前共同纵坐标',23,MUTED).move_to([-.8,-5.25,0])
        live=DecimalNumber(1,num_decimal_places=2,font_size=30,color=GREEN).move_to([2,-5.25,0])
        live.add_updater(lambda m:m.set_value(state().M[1]).move_to([2,-5.25,0]))
        self.add(status,formula,live_label,live)
        self.wait(1.5)
        self.play(b.animate.set_value(2),run_time=3,rate_func=smooth)
        special=text('两切点关于 x 轴对称：MN 与 x 轴重合',24,GREEN).move_to(status)
        self.play(Transform(status,special),run_time=.3)
        self.wait(1.5)
        ordinary=text('继续移动 B，MN 保持水平',26,GREEN).move_to(status)
        self.play(Transform(status,ordinary),run_time=.3)
        self.play(b.animate.set_value(0),run_time=3,rate_func=smooth)
        vertex=text('B 到达顶点，竖直切线仍满足结论',25,GREEN).move_to(status)
        self.play(Transform(status,vertex),run_time=.3)
        self.wait(1.5)
        self.play(Transform(status,ordinary),run_time=.3)
        self.play(b.animate.set_value(4),run_time=4,rate_func=smooth)
        original=text('B 在动，M 与 N 始终处于同一高度',26,GREEN).move_to(status)
        self.play(Transform(status,original),run_time=.3)
        self.wait(1.5)
