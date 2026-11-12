from manim import *
import numpy as np
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from model import geometry

config.background_color='#F7F8FA'
config.frame_width=8
config.frame_height=128/9

INK='#213044'; BLUE='#2778BD'; GOLD='#B77D12'; GREEN='#158068'
COLORS=[BLUE,'#CD6031','#8055B2']

def text(s,size=28,color=INK):
    return Text(s,font='Microsoft YaHei',font_size=size,color=color)

class V009Incenter(Scene):
    def construct(self):
        title=text('内心：为什么按对边长计算？',31).move_to([0,6.2,0])
        status=text('从内心到三边，距离都相等',26).move_to([0,5.35,0])
        footer=VGroup(text('查结论 · 看图解 · 学证明｜知树 App',21),
                      text('公众号 ok-shuxue｜获取入口',19)).arrange(DOWN,buff=.18).move_to([0,-6.25,0])
        self.add(title,status,footer)
        t=ValueTracker(0)
        def diagram(mode):
            V,s,I,F,r=geometry(t.get_value()); A,B,C=V
            g=VGroup()
            if mode>=2:
                for j,(P,Q) in enumerate([(B,C),(C,A),(A,B)]):
                    g.add(Polygon(I,P,Q,fill_color=COLORS[j],fill_opacity=.12,stroke_width=0))
            g.add(Polygon(A,B,C,stroke_color=BLUE,stroke_width=3,fill_opacity=0))
            for j,(P,Q) in enumerate([(B,C),(C,A),(A,B)]):
                mid=(P+Q)/2; outward=mid-I; outward=outward/np.linalg.norm(outward)
                g.add(MathTex('abc'[j],color=INK,font_size=30).move_to(mid+.3*outward))
            if mode>=1:
                g.add(Circle(radius=r,color=GREEN,stroke_width=3).move_to(I))
                for foot in F:
                    line=Line(I,foot,color=GREEN,stroke_width=2)
                    g.add(line,Dot(foot,radius=.035,color=GREEN))
                    u=(I-foot)/r; v=np.array([-u[1],u[0],0])
                    g.add(VMobject(color=GREEN,stroke_width=1.5).set_points_as_corners([foot+.12*u,foot+.12*(u+v),foot+.12*v]))
                g.add(MathTex('r',font_size=27,color=GREEN).move_to((I+F[0])/2+RIGHT*.18))
            if mode>=2:
                for P in V: g.add(Line(I,P,color='#A7B4C2',stroke_width=2))
            for P,name,offset in [(A,'A',UP*.35),(B,'B',LEFT*.3+DOWN*.2),(C,'C',RIGHT*.3+DOWN*.2),(I,'I',UP*.25+RIGHT*.18)]:
                g.add(Dot(P,radius=.055,color=GOLD if name=='I' else BLUE),MathTex(name,font_size=29,color=INK).move_to(P+offset))
            return g
        shape=diagram(0); self.add(shape); self.wait(1)
        self.play(Transform(shape,diagram(1)),run_time=1.3); self.wait(1.2)
        self.play(Transform(shape,diagram(2)),run_time=1)
        f1=MathTex(r'S_{IBC}:S_{ICA}:S_{IAB}=a:b:c',font_size=31,color=INK).move_to([0,-2.15,0])
        note=text('同高 r，面积之比就是底边之比',25).move_to([0,-3,0])
        self.play(FadeIn(f1),FadeIn(note)); self.wait(2)
        newstatus=text('改变三角形，关系始终成立',26).move_to(status)
        f2=MathTex(r'\vec{OI}=\frac{a\vec{OA}+b\vec{OB}+c\vec{OC}}{a+b+c}',font_size=34,color=INK).move_to([0,-3.55,0])
        self.play(Transform(status,newstatus),FadeOut(note),FadeIn(f2))
        self.remove(shape); shape=always_redraw(lambda:diagram(2)); self.add(shape)
        self.play(t.animate.set_value(PI),run_time=4,rate_func=smooth); self.wait(.8)
        self.play(t.animate.set_value(2*PI),run_time=4,rate_func=smooth); self.wait(.8)
        result=MathTex(r'a\vec{IA}+b\vec{IB}+c\vec{IC}=\vec0',font_size=34,color=GREEN).move_to([0,-4.7,0])
        self.play(FadeIn(result)); self.wait(2.5)
        self.play(FadeOut(f1),FadeOut(f2),FadeOut(result),Transform(status,text('从内心到三边，距离都相等',26).move_to(status)),run_time=.5)
        self.remove(shape); self.add(diagram(0)); self.wait(.5)
