from manim import *
import numpy as np
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from centers_model import centers,blended_point,GENERAL,EQUILATERAL,RIGHT_TRIANGLE

config.background_color='#F7F8FA'
config.frame_width=8
config.frame_height=128/9
INK='#213044'; BLUE='#2778BD'; GREEN='#158068'; ORANGE='#CD6031'; PURPLE='#8055B2'
def txt(s,size=27,color=INK):
    return Text(s,font='Microsoft YaHei',font_size=size,color=color)

class V009CentroidIncenter(Scene):
    def construct(self):
        apex=VectorizedPoint(GENERAL)
        title=txt('重心与内心：何时重合？',33).move_to([0,6.2,0])
        status=txt('一般三角形：G 与 I 通常不同',27).move_to([0,5.35,0])
        legend=VGroup(txt('● G 重心：中线交点',23,ORANGE),txt('● I 内心：角平分线交点',23,GREEN)).arrange(DOWN,buff=.16).move_to([0,-1.9,0])
        formulas=VGroup(MathTex(r'\vec{OG}=\frac{\vec{OA}+\vec{OB}+\vec{OC}}3',font_size=32,color=ORANGE),MathTex(r'\vec{OI}=\frac{a\vec{OA}+b\vec{OB}+c\vec{OC}}{a+b+c}',font_size=32,color=GREEN)).arrange(DOWN,buff=.35).move_to([0,-3.6,0])
        note=txt('a=BC，b=CA，c=AB',24).move_to([0,-4.9,0])
        footer=VGroup(txt('查结论 · 看图解 · 学证明｜知树 App',21),txt('公众号 ok-shuxue｜获取入口',19)).arrange(DOWN,buff=.18).move_to([0,-6.25,0])
        def diagram():
            V,w,G,I,r=centers(apex.get_center()); A,B,C=V
            group=VGroup(Polygon(*V,color=BLUE,stroke_width=3),Circle(radius=r,color=GREEN,stroke_width=2).move_to(I))
            for j in range(3):
                P,Q=V[(j+1)%3],V[(j+2)%3]
                group.add(DashedLine(V[j],(P+Q)/2,color=ORANGE,stroke_width=1.5,dash_length=.1))
                D=(w[(j+1)%3]*P+w[(j+2)%3]*Q)/(w[(j+1)%3]+w[(j+2)%3])
                group.add(Line(V[j],D,color=GREEN,stroke_width=1.4,stroke_opacity=.65))
            for P,name,direction in [(A,'A',UP),(B,'B',LEFT+DOWN*.2),(C,'C',RIGHT+DOWN*.2)]:
                group.add(Dot(P,radius=.045,color=BLUE),MathTex(name,color=INK,font_size=29).move_to(P+.32*direction))
            if abs(A[0]+2.6)<1e-5 and abs(A[1]-3.2)<1e-5:
                group.add(VMobject(color=INK,stroke_width=2).set_points_as_corners([B+UP*.22,B+(UP+RIGHT)*.22,B+RIGHT*.22]))
            group.add(Dot(G,radius=.073,color=ORANGE),Dot(I,radius=.05,color=GREEN))
            if np.linalg.norm(G-I)<1e-4:
                group.add(MathTex('G=I',color=GREEN,font_size=30).move_to(G+UP*.38))
            else:
                group.add(MathTex('G',color=ORANGE,font_size=29).move_to(G+UP*.3+RIGHT*.15),MathTex('I',color=GREEN,font_size=29).move_to(I+DOWN*.3+LEFT*.1))
            return group
        shape=always_redraw(diagram)
        self.add(title,status,legend,formulas,note,footer,shape)
        self.wait(2)
        self.play(Transform(status,txt('逐渐变为等边三角形',27).move_to(status)),run_time=.4)
        self.play(apex.animate.move_to(EQUILATERAL),run_time=3)
        self.play(Transform(status,txt('等边三角形：G = I',27).move_to(status)),Transform(note,txt('a=b=c，对边权重也变为相等',24).move_to(note)),run_time=.4)
        self.wait(2)
        self.play(Transform(status,txt('再变为直角三角形',27).move_to(status)),Transform(note,txt('a=BC，b=CA，c=AB',24).move_to(note)),run_time=.4)
        self.play(apex.animate.move_to(RIGHT_TRIANGLE),run_time=3)
        self.play(Transform(status,txt('直角三角形：G 与 I 仍不同',27).move_to(status)),Transform(note,txt('直角不会让重心与内心重合',24).move_to(note)),run_time=.4)
        self.wait(2)
        self.play(FadeOut(legend),FadeOut(formulas),Transform(status,txt('固定三角形，只改变计算权重',27).move_to(status)),Transform(note,txt('移动的是计算点 P；G、I 保持不动',23).move_to(note)),run_time=.5)
        blend=ValueTracker(0)
        path=always_redraw(lambda:Line(centers(apex.get_center())[2],centers(apex.get_center())[3],color=PURPLE,stroke_width=5))
        point=always_redraw(lambda:VGroup(Dot(blended_point(apex.get_center(),blend.get_value()),color=PURPLE,radius=.08),MathTex('P',font_size=28,color=PURPLE).move_to(blended_point(apex.get_center(),blend.get_value())+UP*.55)))
        eq=VGroup(MathTex(r'\vec{OP}_t=(1-t)\vec{OG}+t\vec{OI}',font_size=31,color=PURPLE),txt('t=0：等权 → t=1：按对边长',25),txt('P 从重心 G 沿线段移动到内心 I',24)).arrange(DOWN,buff=.3).move_to([0,-3,0])
        self.add(path,point); self.play(FadeIn(eq)); self.wait(.8)
        self.play(blend.animate.set_value(1),run_time=3); self.wait(2)
        self.play(FadeOut(eq),FadeOut(point),FadeOut(path),Transform(status,txt('回到一般三角形',27).move_to(status)),Transform(note,txt('a=BC，b=CA，c=AB',24).move_to(note)),run_time=.4)
        self.play(apex.animate.move_to(GENERAL),run_time=2)
        self.play(FadeIn(legend),FadeIn(formulas),Transform(status,txt('一般三角形：G 与 I 通常不同',27).move_to(status)),Transform(note,txt('a=BC，b=CA，c=AB',24).move_to(note)),run_time=.4)
        self.wait(.5)
