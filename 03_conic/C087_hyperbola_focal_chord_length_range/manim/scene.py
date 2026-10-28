"""C087: familiar segment -> rotating focal chord -> two minima -> boundary."""
from manim import *
from pathlib import Path
import sys
import json
import math
import numpy as np

sys.path.insert(0,str(Path(__file__).resolve().parent))
from model import snapshot, screen, CRITICAL

config.background_color='#F7F8FA'
config.frame_width=9
config.frame_height=16
INK,MUTED,BLUE,ORANGE,PURPLE,GREEN,AXIS=(
    '#213044','#526275','#2778BD','#CD6031','#8055B2','#158068','#A7B4C2')


def text(s,size=31,color=INK):
    m=Text(s,font='Microsoft YaHei',font_size=size,color=color)
    if m.width>7.7: m.scale_to_fit_width(7.7)
    return m


def eq(s,size=40,color=INK):
    m=MathTex(s,font_size=size,color=color)
    if m.width>7.7: m.scale_to_fit_width(7.7)
    return m


class C087FocalChordRange(Scene):
    def construct(self):
        angle=ValueTracker(0)
        phase={'name':'opposite'}
        audit=[]
        title=text('焦点弦，哪一条最短？',39).move_to([0,7.05,0])
        subtitle=text('先看两顶点之间的线段',30,MUTED).move_to([0,5.95,0])
        # Explicit user requirement: retained in every stage, including transitions.
        footer=VGroup(
            text('查结论 · 看图解 · 学证明｜知树 App',26,MUTED).move_to([0,-6.98,0]),
            text('公众号 ok-shuxue｜获取入口',24,MUTED).move_to([0,-7.5,0]))
        self.add(title,subtitle,footer)
        labels={s:eq(s,36) for s in ['A','B','F_2','P','x','y']}
        def xy(x,y,s=.4): return np.array(screen((x,y),s))
        plain=lambda x:np.array([.8*x,1.2,0])
        segment=VGroup(Line(plain(-3),plain(3),color=ORANGE,stroke_width=6))
        for x,lab in [(-3,'A'),(3,'B')]:
            segment.add(Dot(plain(x),color=ORANGE,radius=.075),
                        labels[lab].copy().next_to(plain(x),DOWN,buff=.22))
        intro=VGroup(eq(r'AB=2a=6',44,ORANGE).move_to([0,-3.4,0]),
                     text('连接两个顶点，长度就是实轴长',29).move_to([0,-4.65,0]))
        self.add(segment,intro)
        self.wait(2)

        def geometry():
            state=snapshot(angle.get_value())
            s=state['scale']
            p=lambda x,y:xy(x,y,s)
            color=PURPLE if state['kind']=='same' else ORANGE
            g=VGroup(Line([-3.6,1.2,0],[3.6,1.2,0],color=AXIS,stroke_width=1.6),
                     Line(p(0,-3.25/s),p(0,3.25/s),color=AXIS,stroke_width=1.6))
            ymax=3.25/s
            for sign in [-1,1]:
                points=[p(sign*3*math.sqrt(1+y*y/16),y) for y in np.linspace(-ymax,ymax,161)]
                points=[q for q in points if abs(q[0])<=3.6]
                curve=VMobject(color=BLUE,stroke_width=2.8)
                curve.set_points_smoothly(points)
                g.add(curve)
            if phase['name'] in ('approach','boundary'):
                # The actual asymptote y=(4/3)x; same metric on both axes.
                xlo=max(1-3.5/s,-3.15/s*3/4)
                xhi=min(1+3.5/s,3.15/s*3/4)
                g.add(DashedLine(p(xlo,4*xlo/3),p(xhi,4*xhi/3),
                                 color=AXIS,stroke_width=2,dash_length=.12))
            f=p(5,0)
            pts=[p(x,y) for x,y in state['points']]
            if state['kind']=='boundary':
                # Finite visible part of the focal line; the only intersection is P.
                v=np.array([math.cos(CRITICAL),math.sin(CRITICAL),0])
                g.add(Line(f-3.45*v,f+3.45*v,color=ORANGE,stroke_width=4))
                g.add(Dot(pts[0],color=GREEN,radius=.08),
                      labels['P'].copy().next_to(pts[0],LEFT,buff=.18))
            else:
                A,B=pts
                if state['kind']=='opposite':
                    g.add(DashedLine(B,f,color=color,stroke_width=2,dash_length=.1))
                g.add(Line(A,B,color=color,stroke_width=5))
                for point,lab,direction in [(A,'A',LEFT),(B,'B',LEFT if state['kind']=='same' else UP+LEFT)]:
                    g.add(Dot(point,color=color,radius=.065))
                    if lab=='B' and phase['name']=='approach':
                        label=labels[lab].copy().move_to(point+np.array([.95,-.55,0]))
                        g.add(Line(point+np.array([.1,-.06,0]),label.get_corner(UL),
                                   color=MUTED,stroke_width=1.2),label)
                    else:
                        g.add(labels[lab].copy().next_to(point,direction,buff=.18))
            fdir=RIGHT if state['kind']=='boundary' else UP+RIGHT
            g.add(Dot(f,color=INK,radius=.06),labels['F_2'].copy().next_to(f,fdir,buff=.18))
            state['time']=round(self.time,6)
            state['phase']=phase['name']
            state['bounds']=[float(g.get_left()[0]),float(g.get_bottom()[1]),
                             float(g.get_right()[0]),float(g.get_top()[1])]
            audit.append(state)
            return g

        graph=always_redraw(geometry)
        self.remove(segment,intro)
        self.add(graph)
        subtitle2=eq(r'\frac{x^2}{9}-\frac{y^2}{16}=1,\quad F_2(5,0)',34).move_to(subtitle)
        self.play(ReplacementTransform(subtitle,subtitle2),run_time=.4)
        subtitle=subtitle2
        status=text('异支：两个端点分居两支',31,ORANGE).move_to([0,5.05,0])
        lprefix=eq(r'L\approx',43).move_to([-1.1,-3.0,0])
        lvalue=DecimalNumber(6,num_decimal_places=2,font_size=43,color=INK).next_to(lprefix,RIGHT,buff=.15)
        lvalue.add_updater(lambda m:m.set_value(snapshot(angle.get_value())['length'] or 0).next_to(lprefix,RIGHT,buff=.15))
        live=VGroup(lprefix,lvalue)
        minimum=eq(r'L\ge 2a=6',43,ORANGE).move_to([0,-4.25,0])
        note=text('水平时，两端点恰好是两个顶点',29).move_to([0,-5.5,0])
        self.add(status,live,minimum,note)
        self.wait(.8)
        self.play(angle.animate.set_value(math.pi/6),run_time=2.1,rate_func=smooth)
        self.play(angle.animate.set_value(0),run_time=2.1,rate_func=smooth)
        self.wait(1.3)

        # Do not interpolate a finite chord across the forbidden asymptote direction.
        self.play(FadeOut(graph),FadeOut(status),FadeOut(minimum),FadeOut(note),run_time=.35)
        self.remove(graph)
        angle.set_value(78*DEGREES)
        phase['name']='same'
        graph=always_redraw(geometry)
        status=text('同支：两个端点都在右支',31,PURPLE).move_to([0,5.05,0])
        minimum=eq(r'L\ge\frac{2b^2}{a}=\frac{32}{3}',43,PURPLE).move_to([0,-4.25,0])
        note=text('转到竖直，弦长达到同支最小值',29).move_to([0,-5.5,0])
        self.add(graph,status,minimum,note)
        self.play(angle.animate.set_value(PI/2),run_time=2,rate_func=smooth)
        self.wait(1.3)
        self.play(angle.animate.set_value(102*DEGREES),run_time=1.3,rate_func=smooth)
        self.play(angle.animate.set_value(PI/2),run_time=1.3,rate_func=smooth)
        self.wait(1)

        self.play(FadeOut(graph),FadeOut(status),FadeOut(minimum),FadeOut(note),run_time=.35)
        self.remove(graph)
        angle.set_value(PI/6)
        phase['name']='approach'
        graph=always_redraw(geometry)
        status=text('接近平行渐近线的方向',31,ORANGE).move_to([0,5.05,0])
        minimum=text('远端越来越远，弦长无界增长',30).move_to([0,-4.25,0])
        note=text('视图等比缩小；双曲线参数不变',27,MUTED).move_to([0,-5.5,0])
        self.add(graph,status,minimum,note)
        self.play(angle.animate.set_value(50*DEGREES),run_time=3,rate_func=linear)
        self.wait(.8)

        self.play(FadeOut(graph),FadeOut(status),FadeOut(minimum),FadeOut(note),FadeOut(live),run_time=.35)
        self.remove(graph,live)
        phase['name']='boundary'
        angle.set_value(CRITICAL)
        graph=always_redraw(geometry)
        status=text('恰好平行时，不再有两点焦点弦',30,ORANGE).move_to([0,5.05,0])
        boundary=VGroup(eq(r'k=\frac ba=\frac43',43).move_to([0,-3.2,0]),
                        text('只有一个有限交点 P',32,GREEN).move_to([0,-4.4,0]),
                        text('与渐近线平行，不能误认为切线',28).move_to([0,-5.55,0]))
        self.add(graph,status,boundary)
        self.wait(2.5)

        self.play(FadeOut(graph),FadeOut(status),FadeOut(boundary),run_time=.35)
        self.remove(graph)
        phase['name']='same'
        angle.set_value(PI/2)
        graph=always_redraw(geometry)
        status=text('先分同支、异支，再判断范围',31).move_to([0,5.05,0])
        result=VGroup(text('异支：水平最短',29,ORANGE).move_to([0,-2.9,0]),
                      eq(r'L\in[2a,+\infty)',41,ORANGE).move_to([0,-3.8,0]),
                      text('同支：竖直最短',29,PURPLE).move_to([0,-4.9,0]),
                      eq(r'L\in[2b^2/a,+\infty)',41,PURPLE).move_to([0,-5.8,0]),
                      text('负斜率情形关于 x 轴对称',24,MUTED).move_to([0,-6.4,0]))
        self.add(graph,status,result)
        self.wait(2.2)
        path=Path(config.media_dir).resolve().parent/'audit.json'
        path.write_text(json.dumps(audit,ensure_ascii=False),encoding='utf8')
