"""C004 storyboard: obtuse vertex angle, bisected maximum, open domain."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from model import VertexAngleModel, UPPER, LOWER
from manim import *
import numpy as np

config.background_color = '#F7F8FA'
config.frame_width, config.frame_height = 9, 16
INK, MUTED, BLUE = '#213044', '#526275', '#2778BD'
ORANGE, GREEN, AXIS = '#CD6031', '#158068', '#A7B4C2'


class C004MaxVertexAngle(Scene):
    def construct(self):
        model = VertexAngleModel()
        scale, origin = 1.65, np.array([0., 1.1, 0.])
        def xy(x, y):
            return origin+scale*np.array([x,y,0.])
        def txt(s, size=29, color=INK):
            return Text(s, font='Microsoft YaHei', font_size=size, color=color)
        def formula(s, size=40, color=INK):
            return MathTex(s, color=color, font_size=size).move_to([0,-4.9,0])
        tracker, visible = ValueTracker(UPPER[0]), ValueTracker(1)
        def p():
            return xy(*model.point(tracker.get_value()))
        a1, a2 = xy(-model.a,0), xy(model.a,0)
        title = txt('顶角最大在哪里？',40).move_to([0,6.9,0])
        subtitle = txt('连接长轴两端点，观察 P 处的钝角',26,MUTED).move_to([0,6,0])
        equation = MathTex(r'\frac{x^2}{4}+y^2=1\quad (a=2,\ b=1)',color=INK,font_size=33).move_to([0,5.08,0])
        axes = VGroup(Line(xy(-2.35,0),xy(2.35,0)),Line(xy(0,-2.25),xy(0,2.25))).set_stroke(AXIS,1.3)
        circle = DashedVMobject(Circle(radius=scale*model.a).move_to(origin),num_dashes=72).set_stroke(AXIS,1.5,opacity=.75)
        circle_label = txt('长轴直径圆',21,MUTED).move_to([2.05,3.97,0])
        ellipse = ParametricFunction(lambda t:xy(*model.point(t)),t_range=[0,TAU],color=BLUE,stroke_width=4)
        base = Line(a1,a2,color=BLUE,stroke_width=2.5)
        endpoints = VGroup(*[Circle(radius=.075,color=INK,stroke_width=2.4,fill_color=config.background_color,fill_opacity=1).move_to(q) for q in (a1,a2)])
        labels = VGroup(MathTex('A_1',font_size=30,color=INK).next_to(a1,DOWN,buff=.19),
                        MathTex('A_2',font_size=30,color=INK).next_to(a2,DOWN,buff=.19),
                        MathTex('O',font_size=25,color=MUTED).next_to(origin,DOWN,buff=.18))
        def geometry():
            pos = p()
            v1,v2 = a1-pos,a2-pos
            sweep = np.arctan2(v1[0]*v2[1]-v1[1]*v2[0],np.dot(v1,v2))
            projection = pos.copy(); projection[1]=origin[1]
            # A small arc at the actual vertex; its sweep is the obtuse interior angle.
            # Cap its radius by the shorter side near the open endpoints.
            radius = min(.46,.36*min(np.linalg.norm(v1),np.linalg.norm(v2)))
            objects = VGroup(Polygon(a1,a2,pos,fill_color=BLUE,fill_opacity=.075,stroke_width=0),
                          DashedLine(projection,pos,color=GREEN,stroke_width=2,dash_length=.09),
                          Line(pos,a1,color=ORANGE,stroke_width=3.4),Line(pos,a2,color=ORANGE,stroke_width=3.4),
                          Arc(radius=radius,start_angle=np.arctan2(v1[1],v1[0]),angle=sweep,arc_center=pos,color=ORANGE,stroke_width=3),
                          Dot(pos,radius=.085,color=ORANGE),
                          MathTex('P',font_size=31,color=ORANGE).next_to(pos,UP if pos[1]>=origin[1] else DOWN,buff=.16))
            # Multiply existing alpha: preserve the translucent triangle and unfilled arc.
            objects.fade(1-visible.get_value())
            return objects
        moving = always_redraw(geometry)
        angle_label = MathTex(r'\alpha=\angle A_1PA_2=',font_size=34,color=INK)
        digits = DecimalNumber(180,num_decimal_places=1,font_size=38,color=ORANGE)
        degree = MathTex(r'{}^\circ',font_size=35,color=ORANGE)
        readout = VGroup(angle_label,digits,degree).arrange(RIGHT,buff=.1).move_to([0,-2.75,0])
        anchor = digits.get_right().copy()
        digits.add_updater(lambda m:m.set_value(model.angle(tracker.get_value())*180/PI).align_to(anchor,RIGHT))
        digits.update(0)
        state = txt('P 在直径圆内，顶角始终大于 90°',28).move_to([0,-3.75,0])
        relation = formula(r'\tan(\alpha-90^\circ)=\frac{(a^2-b^2)|y_P|}{2ab^2}',35)
        footer = txt('P 不取长轴两端点，端点处角无定义',26,MUTED).move_to([0,-6.3,0])
        self.add(title,subtitle,equation,axes,circle,circle_label,ellipse,base,moving,endpoints,labels,readout,state,relation,footer)
        self.wait(1.6)
        def caption(s, color=INK):
            self.play(Transform(state,txt(s,28,color).move_to([0,-3.75,0])),run_time=.3)
        caption('沿同一椭圆增大 |y|，顶角随之增大')
        self.play(tracker.animate.set_value(UPPER[1]),circle.animate.set_stroke(opacity=.25),circle_label.animate.set_opacity(.35),run_time=3,rate_func=smooth)
        caption('短轴端点：作高，顶角被平分',GREEN)
        max_top = Circle(radius=.17,color=GREEN,stroke_width=3).move_to(xy(0,model.b))
        altitude_detail = VGroup(Line(origin,xy(model.a,0),color=GREEN,stroke_width=4),
                                MathTex('a',font_size=30,color=GREEN).move_to(xy(model.a/2,-.25)),
                                MathTex('b',font_size=30,color=GREEN).move_to(xy(-.22,model.b/2)),
                                VMobject(color=GREEN,stroke_width=2).set_points_as_corners([origin+RIGHT*.18,origin+(RIGHT+UP)*.18,origin+UP*.18]))
        self.play(FadeIn(max_top),FadeIn(altitude_detail),Transform(relation,formula(r'\tan\frac{\alpha_{\max}}2=\frac ab\quad\Rightarrow\quad\alpha_{\max}=2\arctan\frac ab',34,GREEN)),run_time=.4)
        self.wait(2.3)
        self.play(FadeOut(altitude_detail),run_time=.3)
        caption('离开短轴端点，顶角逐渐减小')
        self.play(Transform(relation,formula(r'\alpha_{\max}=2\arctan2\approx126.87^\circ',39,GREEN)),run_time=.3)
        self.play(tracker.animate.set_value(UPPER[2]),run_time=2.8,rate_func=smooth)
        caption('趋近长轴端点：趋近 90°，但取不到')
        self.play(Transform(relation,formula(r'90^\circ<\alpha\leq2\arctan\frac ab',42)),run_time=.3)
        self.wait(1.1)
        # Hide and switch arcs; never animate P through an excluded long-axis vertex.
        self.play(visible.animate.set_value(0),run_time=.25)
        tracker.set_value(LOWER[0]); moving.update(0); digits.update(0)
        caption('下半椭圆对称：仍由 |y| 决定顶角')
        self.play(visible.animate.set_value(1),run_time=.25)
        self.play(tracker.animate.set_value(LOWER[1]),run_time=2.7,rate_func=smooth)
        caption('下短轴端点：取得相同最大值',GREEN)
        max_bottom = Circle(radius=.17,color=GREEN,stroke_width=3).move_to(xy(0,-model.b))
        self.play(FadeIn(max_bottom),Transform(relation,formula(r'P=(0,\pm b),\quad\alpha_{\max}=2\arctan\frac ab',38,GREEN)),run_time=.4)
        self.wait(2)
        caption('两短轴端点最大；没有最小值')
        self.play(tracker.animate.set_value(LOWER[2]),run_time=2.6,rate_func=smooth)
        self.wait(.8)
        self.play(visible.animate.set_value(0),run_time=.25)
        tracker.set_value(UPPER[0]); moving.update(0); digits.update(0)
        self.play(FadeOut(max_top),FadeOut(max_bottom),
                  circle.animate.set_stroke(opacity=.75),circle_label.animate.set_opacity(1),
                  Transform(state,txt('P 在直径圆内，顶角始终大于 90°',28).move_to([0,-3.75,0])),
                  Transform(relation,formula(r'\tan(\alpha-90^\circ)=\frac{(a^2-b^2)|y_P|}{2ab^2}',35)),run_time=.4)
        self.play(visible.animate.set_value(1),run_time=.25)
        self.wait(.7)
