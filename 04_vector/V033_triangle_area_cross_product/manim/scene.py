"""Four independent auxiliary constructions, then continuous area/orientation motion."""
from pathlib import Path
import sys
import json
import numpy as np
from manim import *

sys.path.insert(0, str(Path(__file__).parent))
from model import A, B, O, KINDS, construct, determinant, area, moving_b_y

config.frame_width = 9
config.frame_height = 16
config.background_color = '#F7F8FA'
INK = '#213044'
MUTED = '#526275'
BLUE = '#2778BD'
ORANGE = '#CD6031'
PURPLE = '#8055B2'
GREEN = '#158068'
AXIS = '#A7B4C2'
FONT = 'Microsoft YaHei'


class V033FourAuxiliaryArea(Scene):
    def construct(self):
        key_times = {'first': 0.0}
        def mark(name):
            key_times[name] = max(0, float(self.time)-.15)

        def txt(s, size=27, color=INK):
            return Text(s, font=FONT, font_size=size, color=color)

        def math(s, size=38, color=INK):
            return MathTex(s, font_size=size, color=color)

        def xy(p):
            return np.array([-2.5 + p[0]*1.05, -.35 + p[1]*1.05, 0])

        def poly(points, color, opacity=.2):
            return Polygon(*[xy(p) for p in points], color=color,
                           stroke_width=0, fill_color=color, fill_opacity=opacity)

        title = txt('同一面积，四种辅助线', 35).move_to([0,7.05,0])
        subtitle = txt('从 A 或 B 出发，水平、竖直都可以', 24, MUTED).move_to([0,6.32,0])
        # These two lines are permanent: no FadeOut/group operation includes them.
        footer = VGroup(txt('查结论 · 看图解 · 学证明｜知树 App', 23, MUTED),
                        txt('公众号 ok-shuxue｜获取入口', 21, MUTED)).arrange(DOWN,buff=.16).move_to([0,-7.1,0])
        self.add(title,subtitle,footer)

        axes = VGroup(Line(xy((-.25,0)),xy((5,0)),color=AXIS,stroke_width=1.5),
                      Line(xy((0,-.25)),xy((0,5)),color=AXIS,stroke_width=1.5),
                      math('x',25,MUTED).move_to(xy((5.25,0))),
                      math('y',25,MUTED).move_to(xy((0,5.2))))
        triangle = poly((O,A,B),BLUE)
        edges = Polygon(xy(O),xy(A),xy(B),color=BLUE,stroke_width=3,fill_opacity=0)
        points = VGroup(Dot(xy(O),radius=.045,color=INK),
                        Dot(xy(A),radius=.055,color=BLUE),
                        Dot(xy(B),radius=.055,color=GREEN))
        labels = VGroup(math('O',28).move_to(xy(O)+[-.24,-.27,0]),
                        math('A(3,2)',32,BLUE).move_to(xy(A)+[.72,-.17,0]),
                        math('B(2,3)',32,GREEN).move_to(xy(B)+[-.85,.19,0]))
        status = txt('四种作法，算出同一个面积',29,BLUE).move_to([0,5.58,0])
        self.add(status)
        general = math(r'S_{\triangle OAB}=\frac12|x_1y_2-x_2y_1|',43,GREEN).move_to([0,-4.65,0])
        self.play(Create(axes),FadeIn(triangle),Create(edges),FadeIn(points),FadeIn(labels),run_time=1.2)
        intro = math(r'S=\frac12|3\times3-2\times2|=2.5',40).move_to([0,-2.6,0])
        self.play(FadeIn(intro),FadeIn(general),run_time=.4)
        self.wait(1)
        mark('intro')
        self.play(FadeOut(intro),run_time=.3)

        specs = [
            ('① 过 B 作竖直线','交点在线段 OA 内：两片面积相加',r'E_v=(2,\frac43)',
             r'S=\frac12\times\frac53\times(2+1)=2.5','E_v',(.4,-.32)),
            ('② 过 B 作水平线','交点在 OA 延长线上：大面积减小面积',r'E_h=(\frac92,3)',
             r'S=\frac12\times\frac52\times(3-1)=2.5','E_h',(.02,.38)),
            ('③ 过 A 作竖直线','交点在 OB 延长线上：大面积减小面积',r'F_v=(3,\frac92)',
             r'S=\frac12\times\frac52\times(3-1)=2.5','F_v',(.38,.28)),
            ('④ 过 A 作水平线','交点在线段 OB 内：两片面积相加',r'F_h=(\frac43,2)',
             r'S=\frac12\times\frac53\times(2+1)=2.5','F_h',(-.48,-.25)),
        ]
        for kind,(heading,desc,coord,equation,tag,offset) in zip(KINDS,specs):
            c = construct(kind)
            next_status=txt(heading,30,BLUE).move_to(status)
            self.play(ReplacementTransform(status,next_status),run_time=.25)
            status=next_status
            helper=Line(xy(c.start),xy(c.intersection),color=ORANGE,stroke_width=5)
            extension=DashedLine(xy(c.other),xy(c.intersection),color=MUTED,stroke_width=2) if not c.internal else VGroup()
            hit=Dot(xy(c.intersection),radius=.05,color=ORANGE)
            hit_label=math(tag,30,ORANGE).move_to(xy(c.intersection)+[offset[0],offset[1],0])
            caption=txt(desc,23,MUTED).move_to([0,-1.3,0])
            coord_label=math(coord,36).move_to([0,-2.25,0])
            calc=math(equation,38).move_to([0,-3.25,0])
            assert calc.width < 8, 'Formula exceeds safe width'
            self.play(Create(extension),Create(helper),FadeIn(hit),FadeIn(hit_label),run_time=.8)
            if c.internal:
                first=poly((O,c.start,c.intersection),BLUE,.32)
                second=poly((c.other,c.start,c.intersection),PURPLE,.32)
                self.play(FadeIn(first),FadeIn(second),FadeIn(caption),FadeIn(coord_label),run_time=.5)
                self.play(FadeIn(calc),run_time=.35)
                self.wait(1.6)
                mark(kind)
                patches=VGroup(first,second)
            else:
                large=poly((O,c.start,c.intersection),PURPLE,.22)
                small=poly((c.other,c.start,c.intersection),ORANGE,.48)
                self.play(FadeIn(large),FadeIn(small),FadeIn(caption),FadeIn(coord_label),run_time=.5)
                # Remove only the small region: the remaining blue region is OAB.
                self.wait(.4)
                mark(kind+'_big')
                self.play(FadeOut(small),FadeOut(large),FadeIn(calc),run_time=.6)
                self.wait(1.1)
                mark(kind)
                patches=VGroup()
            self.play(FadeOut(VGroup(helper,extension,hit,hit_label,caption,coord_label,calc,patches)),run_time=.3)

        self.play(FadeOut(VGroup(triangle,edges,points,labels)),run_time=.35)
        y=ValueTracker(B[1])
        moving_triangle=always_redraw(lambda: poly((O,A,(2,y.get_value())),BLUE,.23))
        moving_edges=always_redraw(lambda: Polygon(xy(O),xy(A),xy((2,y.get_value())),color=BLUE,stroke_width=3,fill_opacity=0))
        moving_point=always_redraw(lambda: Dot(xy((2,y.get_value())),radius=.06,color=GREEN))
        moving_label=always_redraw(lambda: math('B',32,GREEN).move_to(xy((2,y.get_value()))+[.35,.15,0]))
        anchors=VGroup(Dot(xy(O),radius=.045,color=INK),Dot(xy(A),radius=.055,color=BLUE),labels[0].copy(),labels[1].copy())
        motion_group=VGroup(moving_triangle,moving_edges,moving_point,moving_label,anchors)
        stage=txt('移动 B：面积变，公式始终成立',28,BLUE).move_to(status)
        self.play(ReplacementTransform(status,stage),FadeIn(motion_group),run_time=.35)
        status=stage
        explanation=txt('固定 A(3,2)，让 B 沿 x=2 上下移动',23,MUTED).move_to([0,-1.3,0])
        det_label=math(r'\Delta=3y_B-4=',35).move_to([-1.05,-2.3,0])
        det_value=DecimalNumber(determinant(A,B),num_decimal_places=2,font_size=39,color=INK).move_to([2.05,-2.3,0])
        det_value.add_updater(lambda m:m.set_value(determinant(A,(2,y.get_value()))).move_to([2.05,-2.3,0]))
        area_label=math(r'S=\frac12|\Delta|=',38).move_to([-.95,-3.35,0])
        area_value=DecimalNumber(area(A,B),num_decimal_places=2,font_size=43,color=GREEN).move_to([1.65,-3.35,0])
        area_value.add_updater(lambda m:m.set_value(area(A,(2,y.get_value()))).move_to([1.65,-3.35,0]))
        self.play(FadeIn(VGroup(explanation,det_label,det_value,area_label,area_value)),run_time=.4)
        for segment,duration in enumerate((1.8,1.5,2.0)):
            if segment:
                neutral=txt('继续移动 B：观察行列式的符号',27,BLUE).move_to(status)
                self.play(ReplacementTransform(status,neutral),run_time=.25)
                status=neutral
            target=moving_b_y(segment,1)
            self.play(y.animate.set_value(target),run_time=duration,rate_func=smooth)
            mark('motion_end_'+str(segment))
            if segment==0:
                info=txt('三点共线：面积恰好为 0',28,GREEN)
            elif segment==1:
                info=txt('行列式变负，普通面积仍非负',26,ORANGE)
            else:
                info=txt('起点与方向可选，核心公式不变',27,GREEN)
            info.move_to(status)
            self.play(ReplacementTransform(status,info),run_time=.25)
            status=info
            self.wait(1)
            mark(('collinear','negative_determinant','return')[segment])
        det_value.clear_updaters();area_value.clear_updaters()
        self.wait(.8)
        mark('last')
        (Path(config.media_dir).resolve().parent/'keyframe_times.json').write_text(
            json.dumps(key_times,indent=2),encoding='utf-8')
