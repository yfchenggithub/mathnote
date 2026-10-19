"""C008: moving point-form tangents, axis endpoints, and an external-point polar."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from model import PointTangentModel,clip_line
from manim import *
import numpy as np

config.background_color='#F7F8FA'
config.frame_width,config.frame_height=9,16
INK,MUTED,BLUE,ORANGE,GREEN,AXIS='#213044','#526275','#2778BD','#CD6031','#158068','#A7B4C2'


class C008TangentPointFormula(Scene):
    def construct(self):
        m=PointTangentModel(); tracker=ValueTracker(PI/4); visibility=ValueTracker(1)
        origin=np.array([0.,.65,0.]); scale=1.4
        def xy(x,y):
            return origin+scale*np.array([x,y,0.])
        def text(s,size=28,color=INK):
            return Text(s,font='Microsoft YaHei',font_size=size,color=color)
        def footer(s,size=39,color=INK):
            return MathTex(s,font_size=size,color=color).move_to([0,-5.65,0])
        def drawn_line(coeff,color=ORANGE,width=3.6):
            ends=clip_line(*coeff)
            return Line(xy(*ends[0]),xy(*ends[1]),color=color,stroke_width=width)
        title=text('切点已知，切线就确定',38).move_to([0,6.92,0])
        subtitle=text('先确认点在椭圆上，再用切点式',27,MUTED).move_to([0,6.02,0])
        equation=MathTex(r'\frac{x^2}{4}+y^2=1',font_size=38,color=INK).move_to([0,5.1,0])
        general=MathTex(r'\frac{x_0x}{a^2}+\frac{y_0y}{b^2}=1',font_size=38,color=ORANGE).move_to([0,4.17,0])
        axes=VGroup(Line(xy(-2.75,0),xy(2.75,0)),Line(xy(0,-2.25),xy(0,2.25))).set_stroke(AXIS,1.4)
        labels=VGroup(MathTex('O',font_size=24,color=MUTED).next_to(origin,DOWN,buff=.15),
                      MathTex('x',font_size=24,color=MUTED).next_to(xy(2.75,0),DOWN,buff=.1),
                      MathTex('y',font_size=24,color=MUTED).next_to(xy(0,2.25),LEFT,buff=.1))
        ellipse=ParametricFunction(lambda t:xy(*m.point(t)),t_range=[0,TAU],color=BLUE,stroke_width=3.8)
        def tangent_diagram():
            p=xy(*m.point(tracker.get_value())); A,B,C=m.tangent(tracker.get_value())
            n=np.array([A,B,0.]);n/=np.linalg.norm(n)
            label=MathTex('P',font_size=31,color=ORANGE).move_to(p+.35*n)
            return VGroup(drawn_line((A,B,C)),Dot(p,radius=.085,color=ORANGE),label).fade(1-visibility.get_value())
        moving=always_redraw(tangent_diagram)
        xnum=DecimalNumber(-2,num_decimal_places=2,font_size=34,color=ORANGE)
        ynum=DecimalNumber(-1,num_decimal_places=2,font_size=34,color=ORANGE)
        coords=VGroup(MathTex('P=(',font_size=34,color=INK),xnum,MathTex(',',font_size=34,color=INK),ynum,MathTex(')',font_size=34,color=INK)).arrange(RIGHT,buff=.09).move_to([0,-3.3,0])
        xa,ya=xnum.get_right().copy(),ynum.get_right().copy()
        def clean(v):
            return 0 if abs(v)<.0001 else v
        xnum.add_updater(lambda obj:obj.set_value(clean(m.point(tracker.get_value())[0])).align_to(xa,RIGHT));xnum.update(0)
        ynum.add_updater(lambda obj:obj.set_value(clean(m.point(tracker.get_value())[1])).align_to(ya,RIGHT));ynum.update(0)
        state=text('平方拆成“切点 × 变量”',29).move_to([0,-4.4,0])
        result=footer(r'\frac{\sqrt2}{4}x+\frac{\sqrt2}{2}y=1',38)
        reminder=text('点在椭圆上，才能称为该点处的切线',25,MUTED).move_to([0,-6.9,0])
        self.add(title,subtitle,equation,general,axes,labels,ellipse,moving,coords,state,result,reminder)
        self.wait(1.2)
        def caption(s,color=INK):
            self.play(Transform(state,text(s,28,color).move_to([0,-4.4,0])),run_time=.3)
        def move_with_formula(target,duration,expression,size=40):
            self.play(Transform(result,footer(expression,size)),run_time=.25)
            self.play(tracker.animate.set_value(target),run_time=duration,rate_func=smooth)
        caption('切点移动，切线始终只在 P 处接触')
        move_with_formula(PI/2,1.6,r'\frac{x_0x}{4}+y_0y=1')
        caption('上短轴端点：得到水平切线',GREEN)
        self.play(Transform(result,footer('y=1',43,GREEN)),run_time=.25)
        self.wait(.9)
        caption('继续移动，切点式无需先求斜率')
        move_with_formula(PI,1.9,r'\frac{x_0x}{4}+y_0y=1')
        caption('左长轴端点：斜率不存在，切线仍存在',GREEN)
        self.play(Transform(result,footer('x=-2',43,GREEN)),run_time=.25)
        self.wait(.9)
        caption('沿下半椭圆继续移动')
        move_with_formula(3*PI/2,1.9,r'\frac{x_0x}{4}+y_0y=1')
        caption('下短轴端点：得到另一条水平切线',GREEN)
        self.play(Transform(result,footer('y=-1',43,GREEN)),run_time=.25)
        self.wait(.7)
        caption('切点继续走向右长轴端点')
        move_with_formula(TAU,1.9,r'\frac{x_0x}{4}+y_0y=1')
        caption('右长轴端点：同样得到竖直切线',GREEN)
        self.play(Transform(result,footer('x=2',43,GREEN)),run_time=.25)
        self.wait(.9)
        move_with_formula(9*PI/4,1.6,r'\frac{x_0x}{4}+y_0y=1')
        # Switch diagrams explicitly: M is not a moving contact point on the ellipse.
        self.play(visibility.animate.set_value(0),FadeOut(coords),run_time=.3)
        self.play(Transform(title,text('外点代入，得到什么？',38).move_to([0,6.92,0])),
                  Transform(subtitle,text('M 在椭圆外，可以引出两条实切线',26,MUTED).move_to([0,6.02,0])),
                  Transform(state,text('先看两条切线和它们的切点',28).move_to([0,-4.4,0])),
                  Transform(result,footer(r'T_1=(2,0),\quad T_2=\left(-\frac65,\frac45\right)',34)),run_time=.35)
        M=(2,2); contacts=sorted(m.contacts_from(M)); t2,t1=contacts
        external=VGroup(drawn_line(m.tangent_at(t1)),drawn_line(m.tangent_at(t2)),
                        Dot(xy(*M),radius=.075,color=INK),MathTex('M',font_size=29,color=INK).next_to(xy(*M),RIGHT,buff=.15),
                        Dot(xy(*t1),radius=.085,color=ORANGE),Dot(xy(*t2),radius=.085,color=ORANGE),
                        MathTex('T_1',font_size=28,color=ORANGE).next_to(xy(*t1),DR,buff=.12),
                        MathTex('T_2',font_size=28,color=ORANGE).next_to(xy(*t2),UL,buff=.12))
        external_info=MathTex(r'M=(2,2),\quad S=5>1',font_size=34,color=INK).move_to([0,-3.3,0])
        self.play(FadeIn(external),FadeIn(external_info),run_time=.5)
        self.wait(1)
        polar=VGroup(DashedVMobject(drawn_line(m.polar(M),GREEN,2.4),num_dashes=36),Line(xy(*t1),xy(*t2),color=GREEN,stroke_width=4.5))
        self.play(FadeIn(polar),Transform(general,MathTex(r'\frac{x_1x}{a^2}+\frac{y_1y}{b^2}=1',font_size=38,color=GREEN).move_to([0,4.17,0])),
                  Transform(state,text('外点代入：得到两切点的连线',28,GREEN).move_to([0,-4.4,0])),
                  Transform(result,footer('x+4y-2=0',42,GREEN)),
                  Transform(reminder,text('极线经过 T₁、T₂，不经过外点 M',25,GREEN).move_to([0,-6.9,0])),run_time=.6)
        self.wait(2.4)
        self.play(FadeOut(external),FadeOut(polar),FadeOut(external_info),run_time=.35)
        self.play(Transform(title,text('切点已知，切线就确定',38).move_to([0,6.92,0])),
                  Transform(subtitle,text('先确认点在椭圆上，再用切点式',27,MUTED).move_to([0,6.02,0])),
                  Transform(general,MathTex(r'\frac{x_0x}{a^2}+\frac{y_0y}{b^2}=1',font_size=38,color=ORANGE).move_to([0,4.17,0])),
                  Transform(state,text('平方拆成“切点 × 变量”',29).move_to([0,-4.4,0])),
                  Transform(result,footer(r'\frac{\sqrt2}{4}x+\frac{\sqrt2}{2}y=1',38)),
                  Transform(reminder,text('点在椭圆上，才能称为该点处的切线',25,MUTED).move_to([0,-6.9,0])),run_time=.4)
        self.play(visibility.animate.set_value(1),FadeIn(coords),run_time=.3)
        self.wait(.7)
