"""C084: familiar triangle -> moving tangent -> two intercept roots."""
from manim import *
import sys
from pathlib import Path
import math
sys.path.insert(0,str(Path(__file__).resolve().parent))
from model import state,clip_line,direction,sweep

config.frame_width=9
config.frame_height=16
config.background_color='#F7F8FA'
INK='#213044';MUTED='#526275';BLUE='#2778BD';ORANGE='#CD6031'
PURPLE='#8055B2';GREEN='#158068';GOLD='#B77D12';AXIS='#A7B4C2'

class C084FocalBisector(Scene):
    def construct(self):
        self.camera.background_color='#F7F8FA'
        self.layout_audit=[]
        def txt(s,y,size=28,color=INK):
            m=Text(s,font='Microsoft YaHei',font_size=size,color=color).move_to([0,y,0])
            if m.width>8:raise ValueError(('text too wide',s,m.width))
            return m
        def formula(s,y,size=40,color=INK):
            m=MathTex(s,font_size=size,color=color).move_to([0,y,0])
            if m.width>8:raise ValueError(('formula too wide',s,m.width))
            return m
        def stamp(label):
            for mob in self.mobjects:
                if mob.width and mob.height:
                    self.layout_audit.append({'phase':label,'left':float(mob.get_left()[0]),'right':float(mob.get_right()[0]),'bottom':float(mob.get_bottom()[1]),'top':float(mob.get_top()[1])})
                    if mob.get_left()[0]<-4.3 or mob.get_right()[0]>4.3 or mob.get_bottom()[1]<-7.8 or mob.get_top()[1]>7.8:
                        raise ValueError(('out of safe frame',label,mob))
        def mapper(scale=.57,cx=0,cy=.5):
            return lambda q: np.array([(q[0]-cx)*scale,q[1]*scale+cy,0])
        point=mapper();t=ValueTracker(math.log(2))
        get=lambda:state(t.get_value())
        title=txt('角平分线，为什么也是切线？',6.9,34)
        status=txt('先看熟悉的三角形',5.75,29)
        brand=txt('知树数学  ·  C084',-7.35,21,MUTED)
        note=txt('两边的角一样大',-2.2,30,PURPLE)
        relation=formula(r'\angle ACD=\angle DCB',-3.35,40,PURPLE)
        foot=txt('先看几何结构，再加入双曲线',-5.0,26,MUTED)
        initial=state(math.log(2))
        edge1=always_redraw(lambda:Line(point(get().f1),point(get().p),color=BLUE,stroke_width=3.5))
        edge2=always_redraw(lambda:Line(point(get().p),point(get().f2),color=ORANGE,stroke_width=3.5))
        base=Line(point(initial.f1),point(initial.f2),color=AXIS,stroke_width=2)
        bisector=always_redraw(lambda:Line(point((get().m,0)),point(get().p),color=PURPLE,stroke_width=5))
        pdot=always_redraw(lambda:Dot(point(get().p),radius=.075,color=GOLD))
        mdot=always_redraw(lambda:Dot(point((get().m,0)),radius=.06,color=PURPLE))
        fdots=VGroup(Dot(point(initial.f1),radius=.055,color=INK),Dot(point(initial.f2),radius=.055,color=INK))
        def arcs():
            s=get();angles=[direction(s.p,s.f1),direction(s.p,(s.m,0)),direction(s.p,s.f2)]
            return VGroup(*[Arc(radius=r,start_angle=angles[i],angle=sweep(angles[i],angles[i+1]),arc_center=point(s.p),color=PURPLE,stroke_width=2.5) for i,r in enumerate([.39,.49])])
        angle_marks=always_redraw(arcs)
        labels=VGroup(MathTex('A',font_size=34,color=INK).next_to(point(initial.f1),DOWN,buff=.17),MathTex('B',font_size=34,color=INK).next_to(point(initial.f2),DOWN,buff=.17),MathTex('C',font_size=34,color=INK).next_to(point(initial.p),UL,buff=.14),MathTex('D',font_size=34,color=INK).next_to(point((initial.m,0)),DL,buff=.14))
        self.add(title,brand,status,base,edge1,edge2,fdots,pdot,labels,bisector,mdot,angle_marks,note,relation,foot)
        self.wait(4);stamp('elementary')
        # Relabel the exact same geometry before revealing the hyperbola.
        f1=MathTex('F_1',font_size=34,color=INK).next_to(point(initial.f1),DOWN,buff=.17)
        f2=MathTex('F_2',font_size=34,color=INK).next_to(point(initial.f2),DOWN,buff=.17)
        plabel=always_redraw(lambda:MathTex('P',font_size=34,color=INK).next_to(point(get().p),UL,buff=.16))
        mlabel=always_redraw(lambda:MathTex('M',font_size=34,color=PURPLE).next_to(point((get().m,0)),DL,buff=.16))
        newlabels=VGroup(f1,f2,plabel,mlabel)
        axis=Arrow(point((-5.8,0)),point((6,0)),buff=0,color=AXIS,stroke_width=2,max_tip_length_to_length_ratio=.02)
        origin=Dot(point((0,0)),radius=.035,color=AXIS)
        olabel=MathTex('O',font_size=30,color=MUTED).next_to(point((0,0)),DOWN,buff=.17)
        curves=VGroup(*[ParametricFunction(lambda v,sig=sig:point((sig*3*math.cosh(v),4*math.sinh(v))),t_range=[-.31,1.22],color=GREEN,stroke_width=3) for sig in [-1,1]])
        self.play(ReplacementTransform(status,txt('放回双曲线：紫线仍平分顶角',5.75,28)),FadeOut(labels),FadeIn(newlabels),Create(curves),Create(axis),FadeIn(origin),FadeIn(olabel),ReplacementTransform(relation,formula(r'\frac{x^2}{9}-\frac{y^2}{16}=1',-3.35)),ReplacementTransform(note,txt('两个焦点，就是三角形的底边端点',-2.2,27)),ReplacementTransform(foot,txt('P 取非顶点，焦点三角形才不退化',-5,25,MUTED)),run_time=1.2)
        self.wait(1.5);stamp('hyperbola')
        # Replace segment with the actual analytic tangent, on the SAME line.
        tangent=always_redraw(lambda:Line(*[point(q) for q in clip_line(get().p,get().tangent,(-5.6,5.8,-1.4,6.7))],color=PURPLE,stroke_width=4))
        self.play(FadeOut(bisector),Create(tangent),run_time=.7)
        # Clear only the lower explanatory band, leaving the geometry continuous.
        lower=[m for m in list(self.mobjects) if m is not brand and m.get_center()[1]<-1.5]
        status_current=[m for m in self.mobjects if 5.3<m.get_center()[1]<6.1]
        self.play(*[FadeOut(m) for m in lower+status_current],run_time=.3)
        motionstatus=txt('P 沿曲线移动，观察 M',5.75,29)
        invariant=formula(r'x_0m=a^2=9',-2.3,46,PURPLE)
        reading=always_redraw(lambda:VGroup(
            Text(f'x₀ = {get().x:.2f}',font='Microsoft YaHei',font_size=28,color=GOLD),
            Text(f'm = {get().m:.2f}',font='Microsoft YaHei',font_size=28,color=PURPLE)
        ).arrange(RIGHT,buff=.65).move_to([0,-3.45,0]))
        observe=txt('P 向右走，M 向原点靠近',-4.5,27)
        tangentnote=txt('紫线：内角平分线，也是切线',-5.45,27,PURPLE)
        conditions=txt('右支非顶点：0 < m < a；左支同理',-6.35,23,MUTED)
        self.play(FadeIn(motionstatus),FadeIn(invariant),FadeIn(reading),FadeIn(observe),FadeIn(tangentnote),FadeIn(conditions),run_time=.6)
        self.play(t.animate.set_value(1.15),run_time=3,rate_func=smooth);stamp('farther_P')
        self.wait(.7)
        self.play(Transform(observe,txt('P 返回，乘积仍然等于 9',-4.5,27)),t.animate.set_value(.45),run_time=2.5,rate_func=smooth);stamp('nearer_P')
        self.play(t.animate.set_value(math.log(2)),run_time=1.2,rate_func=smooth)
        self.wait(1)
        # Exterior root: use a wider, isotropic view; no interpolation across branches.
        all_middle=[m for m in list(self.mobjects) if m not in [title,brand]]
        self.play(*[FadeOut(m) for m in all_middle],run_time=.5)
        epoint=mapper(.43,2.6,1.1);s=initial
        estatus=txt('倒角公式，会得到两个交点',5.75,29)
        eaxis=Arrow(epoint((-5.8,0)),epoint((11.6,0)),buff=0,color=AXIS,stroke_width=2,max_tip_length_to_length_ratio=.02)
        etriangle=VGroup(Line(epoint(s.f1),epoint(s.p),color=BLUE,stroke_width=3),Line(epoint(s.p),epoint(s.f2),color=ORANGE,stroke_width=3))
        ei=Line(epoint((s.m,0)),epoint(s.p),color=PURPLE,stroke_width=4)
        eo=DashedLine(epoint(s.p),epoint((s.n,0)),color=GREEN,stroke_width=3,dash_length=.12)
        edots=VGroup(*[Dot(epoint(q),radius=.06,color=col) for q,col in [(s.f1,INK),(s.f2,INK),(s.p,GOLD),((s.m,0),PURPLE),((s.n,0),GREEN)]])
        elabels=VGroup(*[MathTex(name,font_size=34,color=col).next_to(epoint(q),d,buff=.16) for name,q,d,col in [('F_1',s.f1,DOWN,INK),('F_2',s.f2,DOWN,INK),('P',s.p,UP,INK),('M',(s.m,0),DL,PURPLE),('N',(s.n,0),DOWN,GREEN)]])
        angle1=direction(s.p,(s.m,0));angle2=direction(s.p,(s.n,0));v1=np.array([math.cos(angle1),math.sin(angle1),0]);v2=np.array([math.cos(angle2),math.sin(angle2),0]);p=epoint(s.p)
        rightangle=VMobject(color=MUTED,stroke_width=2).set_points_as_corners([p+.2*v1,p+.2*v1+.2*v2,p+.2*v2])
        inside=txt('M 在两焦点之间：取内根',-1.45,28,PURPLE)
        innerformula=formula(r'm=\frac{a^2}{x_0}=\frac{12}{5}',-2.5,39,PURPLE)
        outside=txt('N 在底边外：舍去外根',-3.6,28,GREEN)
        outerformula=formula(r'x_N=\frac{c^2x_0}{a^2}=\frac{125}{12}',-4.65,39,GREEN)
        conclusion=txt('两条角平分线互相垂直',-5.8,27,MUTED)
        self.play(FadeIn(estatus),Create(eaxis),Create(etriangle),Create(ei),FadeIn(edots),FadeIn(elabels),FadeIn(inside),FadeIn(innerformula),run_time=.9)
        self.play(Create(eo),Create(rightangle),FadeIn(outside),FadeIn(outerformula),FadeIn(conclusion),run_time=.9)
        self.wait(3.2);stamp('two_roots')
        self.play(*[FadeOut(m) for m in list(self.mobjects) if m not in [title,brand]],run_time=.5)
        # End and start share the same familiar triangle: reconstruct for a clean loop.
        self.remove(title)
        self.add(title,base,edge1,edge2,fdots,pdot,labels,bisector,mdot,angle_marks)
        self.add(txt('先看熟悉的三角形',5.75,29),txt('两边的角一样大',-2.2,30,PURPLE),formula(r'\angle ACD=\angle DCB',-3.35,40,PURPLE),txt('先看几何结构，再加入双曲线',-5,26,MUTED))
        self.wait(1.2)
        import json
        dest=Path(__file__).resolve().parents[3]/'build/manim/C084/focal_bisector/layout_audit.json'
        dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_text(json.dumps(self.layout_audit,indent=2),encoding='utf8')
