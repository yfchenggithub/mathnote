from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from model import UpwardConfiguration
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


class C073UpwardTangentMidpoint(Scene):
    def construct(self):
        def text(s,size=25,color=INK):
            return Text(s,font=FONT,font_size=size,color=color)
        def xy(pt):
            return np.array([-.4+1.05*pt[0], .4+1.05*pt[1],0])
        b=ValueTracker(3)
        def state(): return UpwardConfiguration(2,-2,b.get_value())
        title=text('开口向上，MN 为何始终竖直？',30).move_to([0,6.9,0])
        subtitle=text('x² = 4y  ·  固定 A，沿抛物线移动 B',23,MUTED).move_to([0,6.15,0])
        footer=VGroup(text('查结论 · 看图解 · 学证明｜知树 App',22,MUTED),
                      text('公众号 ok-shuxue｜获取入口',20,MUTED)).arrange(DOWN,buff=.22).move_to([0,-6.95,0])
        self.add(title,subtitle,footer)
        axes=VGroup(Line(xy((-3,0)),xy((3.5,0)),color=AXIS,stroke_width=1.8),
                    Line(xy((0,-2.2)),xy((0,3.8)),color=AXIS,stroke_width=1.8))
        axis_labels=VGroup(text('x',22,MUTED).move_to(xy((3.85,0))),
                           text('y',22,MUTED).move_to(xy((0,4.12))))
        curve=ParametricFunction(lambda x:xy((x,x*x/4)),t_range=[-3,3.5],color=BLUE,stroke_width=3.5)
        curve_label=MathTex('x^2=4y',font_size=27,color=BLUE).move_to([2.3,4.95,0])
        self.add(axes,axis_labels,curve,curve_label)
        point_labels={name:text(name,25,color) for name,color in [('A',BLUE),('B',BLUE),('M',PURPLE),('N',GREEN)]}

        def diagram():
            c=state()
            guide=DashedLine(xy((c.M[0],-2.2)),xy((c.M[0],3.8)),color=GREEN,stroke_width=1.3,dash_length=.09).set_opacity(.5)
            tangents=VGroup(*[Line(*[xy(pt) for pt in c.tangent_segment(x)],color=ORANGE,stroke_width=2.7) for x in (-2,c.b)])
            chord=Line(xy(c.A),xy(c.B),color=MUTED,stroke_width=2.4)
            segment=Line(xy(c.M),xy(c.N),color=GREEN,stroke_width=6)
            dots=VGroup(Dot(xy(c.A),radius=.065,color=BLUE),Dot(xy(c.B),radius=.065,color=BLUE),
                        Dot(xy(c.M),radius=.078,color=PURPLE),Dot(xy(c.N),radius=.078,color=GREEN))
            tangent=np.array([1,c.b/2,0]); tangent=tangent/np.linalg.norm(tangent)
            normal=np.array([tangent[1],-tangent[0],0])
            b_label=xy(c.B)+.5*normal+.35*tangent
            if abs(b_label[1]-.4)<.35:
                b_label[1]=.4-.4
            n_offset=[.5,.5,0] if c.M[0]>=0 else [-.5,.5,0]
            labels=VGroup(point_labels['A'].copy().move_to(xy(c.A)+[-.45,-.25,0]),
                          point_labels['B'].copy().move_to(b_label),
                          point_labels['M'].copy().move_to(xy(c.M)+[.3,-.7,0]),
                          point_labels['N'].copy().move_to(xy(c.N)+n_offset))
            return VGroup(guide,tangents,chord,segment,dots,labels)

        self.add(always_redraw(diagram))
        self.add(text('橙：两条切线   灰：弦 AB   绿：MN',21,MUTED).move_to([0,-2.65,0]))
        status=text('B 在动，M 与 N 始终横坐标相同',26,GREEN).move_to([0,-3.45,0])
        formula=MathTex(r'x_M=x_N=\frac{x_A+x_B}{2}',font_size=36,color=INK).move_to([0,-4.3,0])
        live_label=text('当前共同横坐标',23,MUTED).move_to([-.8,-5.25,0])
        live=DecimalNumber(.5,num_decimal_places=2,font_size=30,color=GREEN).move_to([2,-5.25,0])
        live.add_updater(lambda m:m.set_value(state().M[0]).move_to([2,-5.25,0]))
        self.add(status,formula,live_label,live)
        self.wait(1.5)
        self.play(b.animate.set_value(2),run_time=3,rate_func=smooth)
        self.play(Transform(status,text('两切点关于 y 轴对称：MN 与 y 轴重合',24,GREEN).move_to(status)),run_time=.3)
        self.wait(1.5)
        ordinary=text('继续移动 B，MN 保持竖直',26,GREEN).move_to(status)
        self.play(Transform(status,ordinary),run_time=.3)
        self.play(b.animate.set_value(0),run_time=3,rate_func=smooth)
        self.play(Transform(status,text('B 到达顶点，水平切线仍满足结论',25,GREEN).move_to(status)),run_time=.3)
        self.wait(1.5)
        self.play(Transform(status,ordinary),run_time=.3)
        self.play(b.animate.set_value(3),run_time=4,rate_func=smooth)
        self.play(Transform(status,text('B 在动，M 与 N 始终横坐标相同',26,GREEN).move_to(status)),run_time=.3)
        self.wait(1.5)
