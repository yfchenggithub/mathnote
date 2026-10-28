"""C086: rods -> focal circles -> vertex -> exact existence bound."""
from manim import *
from pathlib import Path
import sys
import json
import math
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from model import snapshot

config.background_color = '#F7F8FA'
config.frame_width = 9
config.frame_height = 16
INK, MUTED = '#213044', '#526275'
LONG, SHORT, GREEN = '#CD6031', '#8055B2', '#158068'
AXIS = '#A7B4C2'
FONT = 'Microsoft YaHei'


def txt(s, size=30, color=INK):
    m = Text(s, font=FONT, font_size=size, color=color)
    if m.width > 7.7:
        m.scale_to_fit_width(7.7)
    return m


def eq(s, size=39, color=INK):
    m = MathTex(s, font_size=size, color=color)
    if m.width > 7.5:
        m.scale_to_fit_width(7.5)
    return m


class C086FocalRatioRange(Scene):
    def construct(self):
        audit = []
        c = ValueTracker(2)
        title = txt('底边能拉到多长？', 39).move_to([0, 7.05, 0])
        sub = txt('先看两根定长线段', 30, MUTED).move_to([0, 5.9, 0])
        brand = txt('知树数学 · C086', 20, MUTED).move_to([0, -7.38, 0])
        self.add(title, sub, brand)

        def rods():
            s = snapshot(1, c.get_value(), 2)
            x, y = s['points'][0]
            def m(x, y):
                return np.array([.95*x, 1.65+.95*y, 0])
            A, B, T = m(-s['c'], 0), m(s['c'], 0), m(x, y)
            g = VGroup(Line(A, B, color=AXIS, stroke_width=3),
                       Line(A, T, color=LONG, stroke_width=6),
                       Line(T, B, color=SHORT, stroke_width=6))
            for point, label, direction in [(A,'A',DOWN),(B,'B',DOWN),(T,'T',UP)]:
                g.add(Dot(point, radius=.065, color=INK), eq(label,32).next_to(point,direction,buff=.18))
            g.add(eq('4',37,LONG).move_to((A+T)/2+UP*.32),
                  eq('2',37,SHORT).move_to((T+B)/2+UP*.32))
            return g

        geometry = always_redraw(rods)
        panel = VGroup(eq(r'AB\le 4+2=6',44).move_to([0,-2.2,0]),
                       txt('两边之和，不小于第三边',30).move_to([0,-3.5,0]),
                       txt('拉直时，底边达到最大值',30,GREEN).move_to([0,-4.6,0]))
        self.add(geometry, panel)
        self.wait(2)
        self.play(c.animate.set_value(3), run_time=2.5, rate_func=smooth)
        self.wait(1.7)
        # Introduce focal notation only after the familiar triangle is understood.
        geometry.clear_updaters()
        self.play(FadeOut(geometry), FadeOut(panel), FadeOut(sub), run_time=.4)
        self.remove(geometry)
        c.set_value(2)
        title2 = txt('把线段放回双曲线',39).move_to(title)
        sub = eq(r'a=1,\quad \lambda=\frac{PF_1}{PF_2}=2',35).move_to([0,5.9,0])
        self.play(ReplacementTransform(title,title2), FadeIn(sub),run_time=.4)
        title = title2

        def focal_geometry():
            s = snapshot(1, c.get_value(), 2)
            audit.append(dict(time=round(self.time,5), **s))
            def m(x,y):
                return np.array([.5+.5*x,1.65+.5*y,0])
            f1, f2 = m(-s['c'],0), m(s['c'],0)
            g = VGroup(Line(m(-7.7,0),m(5.7,0),color=AXIS,stroke_width=2),
                       Circle(radius=2,color=LONG,stroke_width=3).move_to(f1),
                       Circle(radius=1,color=SHORT,stroke_width=3).move_to(f2))
            # Same metric on both axes; actual hyperbola changes with c.
            for sign in [-1,1]:
                curve = ParametricFunction(lambda y,sgn=sign:m(sgn*math.sqrt(1+y*y/s['b2']),y),
                    t_range=[-4.6,4.6,.04],color=GREEN,stroke_width=3)
                g.add(curve)
            for point,label in [(f1,'F_1'),(f2,'F_2')]:
                g.add(Dot(point,radius=.06,color=INK),eq(label,30).next_to(point,DOWN,buff=.17))
            for j,(x,y) in enumerate(s['points']):
                p = m(x,y)
                g.add(Line(f1,p,color=LONG,stroke_width=5),Line(f2,p,color=SHORT,stroke_width=5),
                      Dot(p,radius=.08,color=GREEN))
                label = 'P' if j==0 else "P'"
                if s['count']==1:
                    label='A(1,0)'
                g.add(eq(label,32,GREEN).next_to(p,UP if j==0 else DOWN,buff=.22))
            return g

        graph = always_redraw(focal_geometry)
        legend = VGroup(eq(r'r_1=PF_1=4',34,LONG),eq(r'r_2=PF_2=2',34,SHORT)).arrange(RIGHT,buff=.5).move_to([0,4.8,0])
        panel = VGroup(eq(r'|PF_1-PF_2|=2a=2',36).move_to([0,-1.9,0]),
                       txt('定比 + 定差 → 两条长度都确定',28).move_to([0,-3.05,0]),
                       txt('两个焦点圆的交点，就是所求点',28).move_to([0,-4.2,0]),
                       txt('绿色曲线：双曲线',26,GREEN).move_to([0,-5.35,0]))
        self.play(FadeIn(graph),FadeIn(legend),FadeIn(panel),run_time=.6)
        self.wait(3.5)
        self.play(FadeOut(panel),FadeOut(title),run_time=.35)
        title = txt('焦点拉远，两点靠拢',39).move_to([0,7.05,0])
        status = txt('相交：有两个对称点',31,GREEN).move_to([0,-2,0])
        # Approximation explicitly marks rounded live values.
        live = always_redraw(lambda: eq(r'e=\frac ca\approx '+f'{c.get_value():.2f}',39).move_to([0,-3.25,0]))
        note = txt('两条半径始终为 4 和 2',30).move_to([0,-4.55,0])
        self.add(title,status,live,note)
        self.play(c.animate.set_value(3),run_time=3,rate_func=smooth)
        self.remove(status,live,note,title)
        title = txt('拉直的边界，就是顶点',38).move_to([0,7.05,0])
        boundary = VGroup(txt('外切：只剩一个点',31,GREEN).move_to([0,-2,0]),
                          eq(r'2c=4+2=6\quad\Rightarrow\quad e=3',38).move_to([0,-3.45,0]),
                          txt('等号能取到：右顶点 A(1, 0)',29).move_to([0,-4.9,0]))
        self.add(title,boundary)
        self.wait(2.6)
        self.play(FadeOut(boundary),FadeOut(title),run_time=.35)
        title = txt('超过总长，就没有交点',38).move_to([0,7.05,0])
        # After departure from tangency there is no point to track.
        self.add(title)
        live = always_redraw(lambda:eq(r'e\approx '+f'{c.get_value():.2f}',40).move_to([0,-3.3,0]))
        self.add(live)
        self.play(c.animate.set_value(3.5),run_time=1.8,rate_func=smooth)
        self.remove(live)
        none = VGroup(txt('分离：没有所求点',31,LONG).move_to([0,-2,0]),
                      eq(r'e=3.5>3,\qquad 2c=7>6',38).move_to([0,-3.4,0]),
                      txt('半径不变，圆心距已超过半径和',29).move_to([0,-4.9,0]))
        self.add(none)
        self.wait(2.3)
        self.play(FadeOut(none),FadeOut(title),run_time=.35)
        # Return continuously to the equality case for the general proof.
        self.play(c.animate.set_value(3),run_time=1.3,rate_func=smooth)
        title = txt('记住“差定、比定、和有界”',36).move_to([0,7.05,0])
        self.add(title)
        result = VGroup(eq(r'2c\le r_1+r_2,\quad |r_1-r_2|=2a',35).move_to([0,-1.8,0]),
                        eq(r'e=\frac ca\le\frac{r_1+r_2}{|r_1-r_2|}=\frac{1+\lambda}{|1-\lambda|}',38).move_to([0,-3.3,0]),
                        eq(r'\boxed{\lambda>0,\ \lambda\ne1,\quad 1<e\le\frac{1+\lambda}{|1-\lambda|}}',36,GREEN).move_to([0,-4.95,0]),
                        txt('等号在顶点；λ = 1 与焦半径差矛盾',26).move_to([0,-6.35,0]))
        self.play(FadeIn(result),run_time=.5)
        self.wait(4.2)
        graph.clear_updaters()
        (Path(config.media_dir)/'C086_frame_math.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf-8')
