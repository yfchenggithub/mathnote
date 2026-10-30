"""C089: a moving tangent changes the triangle, not its area."""
from pathlib import Path
import sys
import json
import numpy as np
from manim import *

sys.path.insert(0,str(Path(__file__).resolve().parent))
from model import state

config.frame_width=9
config.frame_height=16
config.background_color='#F7F8FA'

INK='#213044'
MUTED='#526275'
BLUE='#2778BD'
ORANGE='#CD6031'
GREEN='#158068'
GOLD='#B77D12'
AXIS='#A7B4C2'
FONT='Microsoft YaHei'


class C089TangentArea(Scene):
    def construct(self):
        def text(s,size,y,color=INK):
            obj=Text(s,font=FONT,font_size=size,color=color)
            if obj.width>8.05:
                raise ValueError(f'text exceeds safe width: {s}')
            return obj.move_to([0,y,0])

        title=text('形状在变，面积不变',37,7.25)
        equation=MathTex(r'\frac{x^2}{1.5^2}-y^2=1',font_size=36,color=INK).move_to([0,6.45,0])
        parameters=text('图取 a = 1.5，b = 1',25,5.83,MUTED)
        status=text('顶点切线：底 2b，高 a',28,5.27)
        footer1=text('查结论 · 看图解 · 学证明｜知树 App',25,-6.84,MUTED)
        footer2=text('公众号 ok-shuxue｜获取入口',24,-7.39,MUTED)
        # Footer is added once, before any wait/play, and never faded out.
        self.add(title,equation,parameters,status,footer1,footer2)

        origin=np.array([-3.0,.62,0.0])
        unit=1.45  # Same scale in x and y, unchanged for the entire animation.
        def point(q):
            return origin+unit*np.array([q[0],q[1],0.0])
        axes=VGroup(
            Arrow(point((-.22,0)),point((4.25,0)),buff=0,stroke_width=1.5,color=AXIS,max_tip_length_to_length_ratio=.025),
            Arrow(point((0,-2.8)),point((0,2.8)),buff=0,stroke_width=1.5,color=AXIS,max_tip_length_to_length_ratio=.025),
        )
        axislabels=VGroup(
            MathTex('x',font_size=26,color=MUTED).move_to(point((4.34,0))),
            MathTex('y',font_size=26,color=MUTED).move_to(point((0,2.94))),
            MathTex('O',font_size=27,color=INK).move_to(point((-.19,-.2))),
        )
        asymptotes=VGroup(*[
            DashedLine(point((0,0)),point((4.1,sign*4.1/1.5)),
              dash_length=.13,dashed_ratio=.58,stroke_width=2.2,color=BLUE)
            for sign in [-1,1]
        ])
        curve=ParametricFunction(lambda u: point((1.5*np.cosh(u),np.sinh(u))),
              t_range=[-1.65,1.65,.015],color=BLUE,stroke_width=3.5)
        tracker=ValueTracker(0)
        current=lambda: state(tracker.get_value())
        triangle=Polygon(point((0,0)),point((1.5,1)),point((1.5,-1)),
              stroke_width=0,fill_color=ORANGE,fill_opacity=.18)
        def update_triangle(m):
            s=current()
            m.set_points_as_corners([point((0,0)),point(s.A),point(s.B),point((0,0))])
        triangle.add_updater(update_triangle)
        tangent=Line(point((1.5,-1.2)),point((1.5,1.2)),color=ORANGE,stroke_width=4)
        def update_tangent(m):
            s=current();A=point(s.A);B=point(s.B)
            m.put_start_and_end_on(B-.10*(A-B),A+.10*(A-B))
        tangent.add_updater(update_tangent)
        points=VGroup()
        for key,color in [('A',ORANGE),('B',ORANGE),('p',GOLD)]:
            dot=Dot(radius=.065,color=color)
            dot.add_updater(lambda m,key=key: m.move_to(point(getattr(current(),key))))
            points.add(dot)
        labels=VGroup()
        for key,label,offset in [
            ('A','A',(-.36,.10,0)),('B','B',(-.36,-.10,0)),('p','P',(.32,0,0))]:
            obj=MathTex(label,font_size=29,color=INK)
            obj.add_updater(lambda m,key=key,offset=np.array(offset): m.move_to(point(getattr(current(),key))+offset))
            labels.add(obj)
        self.add(triangle,axes,asymptotes,curve,tangent,points,axislabels,labels)

        area_label=MathTex(r'S_{\triangle AOB}=',font_size=43,color=GREEN)
        number=DecimalNumber(1.5,num_decimal_places=2,font_size=43,color=GREEN)
        area_row=VGroup(area_label,number).arrange(RIGHT,buff=.15).move_to([0,-4.16,0])
        number.add_updater(lambda m:m.set_value(current().area))
        explanation=MathTex(r'S=\tfrac12(2b)\,a=ab',font_size=34,color=INK).move_to([0,-5.02,0])
        scope=text('左右两支及顶点均成立',25,-5.85,MUTED)
        self.add(area_row,explanation,scope)
        # Manim may freeze the first wait before nested updaters have run.
        self.update_mobjects(0)
        telemetry=[]
        guard=Mobject()
        def audit_frame(m,dt):
            s=current()
            assert abs(s.area-1.5)<1e-10
            assert max(abs(s.tangent_residual(q)) for q in (s.A,s.B,s.p))<1e-10
            for obj in [title,equation,parameters,status,footer1,footer2,
                        area_row,explanation,scope,*axislabels,*labels]:
                assert obj.get_left()[0]>-4.3 and obj.get_right()[0]<4.3
                assert obj.get_bottom()[1]>-7.8 and obj.get_top()[1]<7.8
            telemetry.append({'time':float(self.time),'t':float(s.t),
                              'P':s.p,'A':s.A,'B':s.B,'area':s.area})
        guard.add_updater(audit_frame)
        self.add(guard)
        self.wait(1.8)
        status.become(text('移动切点，观察阴影面积',28,5.27))
        self.play(tracker.animate.set_value(.75),run_time=3.2,rate_func=smooth)
        self.wait(1)
        explanation.become(MathTex(r'OA\cdot OB=a^2+b^2',font_size=34,color=INK).move_to([0,-5.02,0]))
        status.become(text('两边乘积不变，夹角不变',28,5.27))
        self.play(tracker.animate.set_value(0),run_time=2.6,rate_func=smooth)
        self.wait(.6)
        status.become(text('切点越过顶点，面积仍不变',28,5.27))
        self.play(tracker.animate.set_value(-.75),run_time=3.2,rate_func=smooth)
        self.wait(1)
        self.play(tracker.animate.set_value(0),run_time=2.6,rate_func=smooth)
        status.become(text('切线变，形状变，面积恒为 ab',28,5.27))
        explanation.become(MathTex(r'S=\tfrac12\,OA\cdot OB\,\sin\angle AOB=ab',font_size=31,color=INK).move_to([0,-5.02,0]))
        self.wait(2.2)
        # Close the loop at exactly the same vertex and opening text.
        status.become(text('顶点切线：底 2b，高 a',28,5.27))
        explanation.become(MathTex(r'S=\tfrac12(2b)\,a=ab',font_size=34,color=INK).move_to([0,-5.02,0]))
        self.wait(.8)
        evidence=Path(config.media_dir).parent/'frame_model_checks.json'
        evidence.write_text(json.dumps(telemetry,indent=2),encoding='utf-8')
