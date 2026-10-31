"""Four real intersections: a confocal family and its focal-radius explanation."""
import json
from pathlib import Path
import sys

import numpy as np
from manim import *

sys.path.insert(0,str(Path(__file__).resolve().parent))
from model import ConfocalPair

config.frame_width=9
config.frame_height=16
config.background_color="#F7F8FA"

BG="#F7F8FA"
INK="#213044"
MUTED="#526275"
ELLIPSE="#2778BD"
HYPERBOLA="#CD6031"
POINT="#B77D12"
RESULT="#158068"
AXIS="#A7B4C2"
FOOTER=("查结论 · 看图解 · 学证明｜知树 App", "公众号 ok-shuxue｜获取入口")


class C094FourIntersections(Scene):
    def text(self,content,size=32,color=INK):
        return Text(content,font="Microsoft YaHei",font_size=size,color=color)

    def formula(self,content,size=37,color=INK):
        return MathTex(content,font_size=size,color=color)

    def xy(self,x,y):
        # Identical x and y scale is essential to the geometric argument.
        return np.array([.82*x,1.15+.82*y,0.0])

    def construct(self):
        self.audit=[]
        self.a_h=ValueTracker(1.0)
        title=self.text("共焦，为什么恰有四个交点？",36).move_to([0,7.0,0])
        conditions=self.formula(r"a_E>c>a_H>0",32,MUTED).move_to([0,6.28,0])
        legend=VGroup(self.text("椭圆 E",28,ELLIPSE),self.text("双曲线 H",28,HYPERBOLA))
        legend.arrange(RIGHT,buff=.8).move_to([0,5.55,0])
        brand1=self.text(FOOTER[0],23,MUTED).move_to([0,-6.9,0])
        brand2=self.text(FOOTER[1],21,MUTED).move_to([0,-7.43,0])
        brand=VGroup(brand1,brand2)
        self.add(title,conditions,legend,brand)

        axes=VGroup(Line(self.xy(-4.55,0),self.xy(4.55,0),color=AXIS,stroke_width=1.5),
                    Line(self.xy(0,-4.05),self.xy(0,4.05),color=AXIS,stroke_width=1.5))
        axis_labels=VGroup(self.formula('x',25,MUTED).move_to(self.xy(4.72,0)),
                           self.formula('y',25,MUTED).move_to(self.xy(0,4.26)),
                           self.formula('O',24,MUTED).move_to(self.xy(-.28,-.32)))
        model=ConfocalPair()
        ellipse=ParametricFunction(lambda t:self.xy(*model.ellipse(t)),t_range=[0,TAU,TAU/180],
                                   color=ELLIPSE,stroke_width=3.3)
        foci=VGroup(*[Dot(self.xy(x,0),radius=.055,color=INK) for x in (-2,2)])
        flabels=VGroup(self.formula('F_1',27).move_to(self.xy(-2,-.44)),
                      self.formula('F_2',27).move_to(self.xy(2,-.44)))
        self.add(axes,axis_labels,ellipse,foci,flabels)

        def current():
            return ConfocalPair(a_h=self.a_h.get_value())

        # No arbitrary screen endpoints: all curve and point positions come from the model.
        def hyperbolas():
            m=current()
            ymax=m.visible_hyperbola_y()
            return VGroup(*[ParametricFunction(lambda y,s=sign:self.xy(*m.hyperbola(y,s)),
                           t_range=[-ymax,ymax,.06],color=HYPERBOLA,stroke_width=3.1)
                           for sign in (-1,1)])

        curves=always_redraw(hyperbolas)
        points=always_redraw(lambda:VGroup(*[Dot(self.xy(x,y),radius=.085,color=POINT)
                                             for x,y in current().points()]))
        rectangle=always_redraw(lambda:Polygon(*[self.xy(*p) for p in
                                   (current().points()[0],current().points()[1],
                                    current().points()[3],current().points()[2])],
                                   color=AXIS,stroke_width=1.3,fill_opacity=0))
        # Parameters are numeric readouts, never regenerated TeX on each frame.
        ah_label=self.formula(r'a_E=4,\ c=2,\ a_H=',29,MUTED)
        number=DecimalNumber(1,num_decimal_places=2,font_size=29,color=HYPERBOLA)
        readout=VGroup(ah_label,number).arrange(RIGHT,buff=.1).move_to([0,-2.72,0])
        number.add_updater(lambda obj:obj.set_value(self.a_h.get_value()))
        self.add(curves,rectangle,points,readout)

        step=self.text("共用两焦点，左右两支各交两点",30).move_to([0,-3.48,0])
        detail=self.formula(r"P=(\pm2,\,\pm3)",36,RESULT).move_to([0,-4.5,0])
        note=self.text("两处正负号独立取值",28,MUTED).move_to([0,-5.65,0])
        self.add(step,detail,note)
        self.guard=[title,conditions,legend,brand,axis_labels,readout,step,detail,note]
        self.wait(1.6)

        def change(message,formula,note_text,math_note=False):
            nonlocal step,detail,note
            newstep=self.text(message,30).move_to([0,-3.48,0])
            newdetail=self.formula(formula,36,RESULT).move_to([0,-4.5,0])
            newnote=(self.formula(note_text,29,MUTED) if math_note else
                     self.text(note_text,28,MUTED)).move_to([0,-5.65,0])
            self.play(FadeOut(step),FadeOut(detail),FadeOut(note),run_time=.2)
            self.remove(step,detail,note)
            step,detail,note=newstep,newdetail,newnote
            self.guard=[title,conditions,legend,brand,axis_labels,readout,step,detail,note]
            self.play(FadeIn(step),FadeIn(detail),FadeIn(note),run_time=.25)

        change("改变实半轴，四点仍同时存在",r"0<a_H<c", "椭圆与焦点固定，双曲线改变")
        self.play(self.a_h.animate.set_value(.65),run_time=1.8,rate_func=smooth)
        self.wait(.65)
        self.play(self.a_h.animate.set_value(1.65),run_time=3.0,rate_func=smooth)
        self.wait(.8)
        self.play(self.a_h.animate.set_value(1.0),run_time=2,rate_func=smooth)
        self.wait(.6)

        # Freeze one valid pair and reveal the focal geometry without moving the point.
        self.remove(rectangle)
        x,y=current().positive_point
        radii=VGroup(Line(self.xy(-2,0),self.xy(x,y),color=MUTED,stroke_width=2.2),
                     Line(self.xy(2,0),self.xy(x,y),color=MUTED,stroke_width=2.2))
        plabel=self.formula('P',29,POINT).move_to(self.xy(2.55,3.4))
        r1=self.formula('r_1',28,MUTED).move_to(self.xy(-.6,1.65))
        r2=self.formula('r_2',28,MUTED).move_to(self.xy(2.42,1.5))
        self.play(Create(radii),FadeIn(plabel),FadeIn(r1),FadeIn(r2),run_time=.6)
        self.guard += [plabel,r1,r2]
        change("同一对距离：椭圆定和，双曲线定差",r"r_1+r_2=2a_E,\quad r_1-r_2=2a_H", "右上交点：较远距离为 r₁")
        self.wait(2)
        change("焦半径的平方差，确定横坐标",r"4cX=r_1^2-r_2^2=4a_Ea_H", "相同高度消去，确定横坐标 X")
        self.wait(2)
        self.play(FadeOut(radii),FadeOut(plabel),FadeOut(r1),FadeOut(r2),run_time=.35)
        self.add(rectangle)
        change("横纵坐标各有两个符号，恰好四点",r"X=\frac{a_Ea_H}{c},\qquad Y=\frac{b_Eb_H}{c}",
               r"b_E^2=a_E^2-c^2,\quad b_H^2=c^2-a_H^2",math_note=True)
        independent=self.formula(r"(X,Y),\ (X,-Y),\ (-X,Y),\ (-X,-Y)",27,INK).move_to([0,-6.25,0])
        self.add(independent)
        self.guard.append(independent)
        self.wait(2.8)
        self.play(FadeOut(independent),run_time=.2)
        change("共用两焦点，左右两支各交两点",r"P=(\pm2,\,\pm3)", "两处正负号独立取值")
        self.wait(.8)
        output=Path(config.media_dir).resolve().parent/'scene_audit.json'
        output.write_text(json.dumps(self.audit,ensure_ascii=False),encoding='utf-8')

    def update_mobjects(self,dt):
        super().update_mobjects(dt)
        if not hasattr(self,'guard'):
            return
        for obj in self.guard:
            if obj.width and (obj.get_left()[0]<-4.15 or obj.get_right()[0]>4.15
                              or obj.get_top()[1]>7.7 or obj.get_bottom()[1]<-7.7):
                raise ValueError(f"C094 text exceeds safety bounds: {obj}")
        model=ConfocalPair(a_h=self.a_h.get_value())
        self.audit.append({'time':float(self.renderer.time),'a_h':model.a_h,
                           'points':[list(p) for p in model.points()]})
