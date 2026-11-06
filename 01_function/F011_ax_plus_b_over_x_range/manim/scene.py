"""Two F011 lessons. Render/export only through scripts/manim's frozen tools."""
from pathlib import Path
import sys
import json
sys.path.insert(0,str(Path(__file__).resolve().parent))
from model import value, branch_points, branch_distance, support_distance
from manim import *

config.frame_width=9
config.frame_height=16
config.background_color="#F7F8FA"
BG="#F7F8FA"
INK="#213044"
MUTED="#526275"
BLUE="#2778BD"
ORANGE="#CD6031"
PURPLE="#8055B2"
GREEN="#158068"
AXIS="#A7B4C2"


def text(s,size=30,color=INK):
    return Text(s,font="Microsoft YaHei",font_size=size,color=color)


def math(s,size=34,color=INK):
    return MathTex(s,font_size=size,color=color)


def smooth(t): return t*t*(3-2*t)


def footer(scene):
    group=VGroup(text("查结论 · 看图解 · 学证明｜知树 App",25,MUTED),
                 text("公众号 ok-shuxue｜获取入口",23,MUTED)).arrange(DOWN,buff=.16).move_to([0,-7.12,0])
    scene.add(group)
    return group


class Audit:
    """UID-local evidence: actual scene times and per-frame text safe-area checks."""
    def __init__(self,scene,name):
        self.scene=scene;self.name=name;self.states=[];self.texts=[];self.violations=[];self.samples=0
        self.probe=Mobject()
        self.probe.add_updater(lambda _: self.check())
        scene.add(self.probe)

    def watch(self,*objects):
        self.texts.extend(objects)

    def check(self):
        self.samples+=1
        for i,obj in enumerate(self.texts):
            if obj.width==0: continue
            if obj.get_left()[0]<-4.15 or obj.get_right()[0]>4.15 or obj.get_top()[1]>7.55 or obj.get_bottom()[1]<-7.7:
                self.violations.append({"time":round(float(self.scene.time),3),"object":i})

    def mark(self,label,**params):
        self.states.append({"time":round(float(self.scene.time),3),"label":label,**params})

    def finish(self):
        self.check()
        folder=Path("build/manim/F011-production/F011")/self.name
        folder.mkdir(parents=True,exist_ok=True)
        (folder/"scene_audit.json").write_text(json.dumps({"states":self.states,"layout_samples":self.samples,
            "safe_area_violations":self.violations},ensure_ascii=False,indent=2),encoding="utf-8")
        if self.violations: raise ValueError(f"Text outside safe area: {self.violations[:4]}")


class F011Range(Scene):
    def construct(self):
        audit=Audit(self,"range")
        brand=footer(self)
        title=text("对勾函数：最值在哪里？",36).move_to([0,6.9,0])
        formula=math(r"y=x+\frac1x\quad (x\ne0)",40).move_to([0,5.95,0])
        example=text("先看 A = B = 1 的情形",25,MUTED).move_to([0,5.2,0])
        self.add(title,formula,example)
        axes=Axes(x_range=[-3.2,3.2,1],y_range=[-4.3,4.3,1],x_length=5.76,y_length=7.74,
                  axis_config={"color":AXIS,"stroke_width":1.8,"include_ticks":False,
                               "tip_width":.11,"tip_height":.14}).move_to([-.4,.45,0])
        xlab=math("x",27,MUTED).next_to(axes.x_axis.get_end(),RIGHT,buff=.08)
        ylab=math("y",27,MUTED).next_to(axes.y_axis.get_end(),UP,buff=.06)
        O=math("O",23,MUTED).next_to(axes.c2p(0,0),DL,buff=.09)
        pos=axes.plot(lambda x:value(x),x_range=[.245,3.2,.02],color=BLUE,stroke_width=4)
        neg=axes.plot(lambda x:value(x),x_range=[-3.2,-.245,.02],color=BLUE,stroke_width=4)
        rail_x=3.25
        rail=Line([rail_x,axes.c2p(0,-4.3)[1],0],[rail_x,axes.c2p(0,4.3)[1],0],color=AXIS,stroke_width=1.6)
        rail_title=text("值域",25,MUTED).next_to(rail,UP,buff=.13)
        bounds=VGroup(*[DashedLine(axes.c2p(-3.1,z),[rail_x,axes.c2p(0,z)[1],0],color=AXIS,stroke_width=1.4,dash_length=.09) for z in (-2,2)])
        boundlabs=VGroup(*[math(str(z),27,MUTED).next_to([rail_x,axes.c2p(0,z)[1],0],RIGHT,buff=.12) for z in (-2,2)])
        self.add(axes,xlab,ylab,O,pos,neg,rail,rail_title,bounds,boundlabs)
        x=ValueTracker(.26)
        dot=always_redraw(lambda:Dot(axes.c2p(x.get_value(),value(x.get_value())),radius=.075,color=ORANGE))
        projection=always_redraw(lambda:DashedLine(axes.c2p(x.get_value(),value(x.get_value())),[rail_x,axes.c2p(0,value(x.get_value()))[1],0],color=ORANGE,stroke_width=1.6,dash_length=.07))
        read=always_redraw(lambda:Dot([rail_x,axes.c2p(0,value(x.get_value()))[1],0],radius=.065,color=ORANGE))
        dynamic=VGroup(dot,projection,read)
        state=text("正半轴：先减后增",30,ORANGE).move_to([0,-4.35,0])
        xlabel=math(r"x\approx",31).move_to([-1.8,-5.15,0]);yvalue_label=math(r"y\approx",31).move_to([.7,-5.15,0])
        xn=DecimalNumber(.26,num_decimal_places=2,font_size=31,color=ORANGE).next_to(xlabel,RIGHT,buff=.12)
        yn=DecimalNumber(value(.26),num_decimal_places=2,font_size=31,color=ORANGE).next_to(yvalue_label,RIGHT,buff=.12)
        xn.add_updater(lambda m:m.set_value(x.get_value()).next_to(xlabel,RIGHT,buff=.12))
        yn.add_updater(lambda m:m.set_value(value(x.get_value())).next_to(yvalue_label,RIGHT,buff=.12))
        numbers=VGroup(xlabel,xn,yvalue_label,yn)
        reason=text("动点的纵坐标，投到右侧值域轴",25,MUTED).move_to([0,-6.0,0])
        self.add(dynamic,state,numbers,reason)
        audit.watch(brand,title,formula,example,xlab,ylab,O,rail_title,boundlabs,state,numbers,reason)
        audit.mark("positive_start",x=.26,y=value(.26));self.wait(1)
        self.play(x.animate.set_value(1),run_time=2.4,rate_func=smooth)
        equality=math(r"x=1/x=1\quad\Rightarrow\quad y_{\min}=2",32,GREEN).move_to([0,-6,0])
        self.play(Transform(reason,equality),run_time=.3)
        pmin=Dot(axes.c2p(1,2),radius=.075,color=GREEN)
        plabel=math("(1,2)",27,GREEN).move_to(axes.c2p(1,2)+[.55,.5,0])
        self.add(pmin,plabel);audit.watch(plabel)
        audit.mark("positive_minimum",x=1,y=2);self.wait(1.2)
        self.play(x.animate.set_value(3.2),run_time=2.3,rate_func=smooth);self.wait(.4)
        self.play(FadeOut(dynamic),run_time=.25)
        x.set_value(-.26)
        dynamic.update(0)
        self.play(FadeIn(dynamic),Transform(state,text("负半轴：先增后减",30,PURPLE).move_to(state)),
                  Transform(reason,text("关于原点对称，最小变最大",25,MUTED).move_to(reason)),run_time=.35)
        self.play(x.animate.set_value(-1),run_time=2.4,rate_func=smooth)
        nmax=Dot(axes.c2p(-1,-2),radius=.075,color=GREEN)
        nlabel=math("(-1,-2)",27,GREEN).move_to(axes.c2p(-1,-2)+[.8,.5,0])
        self.add(nmax,nlabel);audit.watch(nlabel)
        self.play(Transform(reason,math(r"x=-1\quad\Rightarrow\quad y_{\max}=-2",32,GREEN).move_to(reason)),run_time=.3)
        audit.mark("negative_maximum",x=-1,y=-2);self.wait(1.2)
        self.play(x.animate.set_value(-3.2),run_time=2.3,rate_func=smooth);self.wait(.4)
        band=Polygon(axes.c2p(-3.2,-2),axes.c2p(3.2,-2),axes.c2p(3.2,2),axes.c2p(-3.2,2),stroke_width=0,fill_color="#E4E9EF",fill_opacity=.6).set_z_index(-1)
        gap=text("中间的 y 值取不到",25,MUTED).move_to(axes.c2p(.4,.8))
        intervals=VGroup(Arrow([rail_x,axes.c2p(0,2)[1],0],[rail_x,axes.c2p(0,4.3)[1],0],buff=0,color=GREEN,stroke_width=4),
            Arrow([rail_x,axes.c2p(0,-2)[1],0],[rail_x,axes.c2p(0,-4.3)[1],0],buff=0,color=GREEN,stroke_width=4),
            Dot([rail_x,axes.c2p(0,2)[1],0],radius=.07,color=GREEN),Dot([rail_x,axes.c2p(0,-2)[1],0],radius=.07,color=GREEN))
        self.play(FadeOut(dynamic),FadeIn(band),FadeIn(gap),FadeIn(intervals),
                  Transform(state,text("值域是两段，端点能取到",30,GREEN).move_to(state)),
                  FadeOut(numbers),Transform(reason,math(r"(-\infty,-2]\cup[2,+\infty)",34,GREEN).move_to([0,-5.2,0])),run_time=.5)
        general=math(r"A,B>0:\quad y\le-2\sqrt{AB}\ \mathrm{or}\ y\ge2\sqrt{AB}",28).move_to([0,-6.05,0])
        self.add(general);audit.watch(gap,general)
        audit.mark("range_and_generalization");self.wait(3.2)
        # Fade back to the exact opening configuration; no motion through x=0.
        self.play(FadeOut(band),FadeOut(gap),FadeOut(intervals),FadeOut(general),FadeOut(pmin),FadeOut(plabel),FadeOut(nmax),FadeOut(nlabel),run_time=.3)
        x.set_value(.26)
        dynamic.update(0)
        numbers.update(0)
        self.play(FadeIn(dynamic),FadeIn(numbers),Transform(state,text("正半轴：先减后增",30,ORANGE).move_to(state)),
                  Transform(reason,text("动点的纵坐标，投到右侧值域轴",25,MUTED).move_to([0,-6,0])),run_time=.3)
        self.wait(.5);audit.mark("loop_reset");audit.finish()


class F011BranchDistance(Scene):
    def construct(self):
        audit=Audit(self,"branch_distance")
        brand=footer(self)
        title=text("两支曲线，最近有多近？",36).move_to([0,6.9,0])
        formula=math(r"y=\frac1x\quad (k=1)",40).move_to([0,5.95,0])
        state=text("两点在各自分支上独立移动",28,MUTED).move_to([0,5.0,0])
        self.add(title,formula,state)
        axes=Axes(x_range=[-3,3,1],y_range=[-3,3,1],x_length=6.6,y_length=6.6,
            axis_config={"color":AXIS,"stroke_width":1.8,"include_ticks":False,"tip_width":.1,"tip_height":.14}).move_to([0,.75,0])
        xlab=math("x",27,MUTED).next_to(axes.x_axis.get_end(),RIGHT,buff=.07)
        ylab=math("y",27,MUTED).next_to(axes.y_axis.get_end(),UP,buff=.06)
        O=math("O",23,MUTED).next_to(axes.c2p(0,0),UL,buff=.1)
        curves=VGroup(axes.plot(lambda x:1/x,x_range=[1/3,3,.02],color=BLUE,stroke_width=4),
                      axes.plot(lambda x:1/x,x_range=[-3,-1/3,.02],color=BLUE,stroke_width=4))
        self.add(axes,xlab,ylab,O,curves)
        a,b=ValueTracker(.55),ValueTracker(1.8)
        def P():return axes.c2p(*branch_points(a.get_value(),b.get_value())[0])
        def Q():return axes.c2p(*branch_points(a.get_value(),b.get_value())[1])
        pdot=always_redraw(lambda:Dot(P(),radius=.075,color=ORANGE))
        qdot=always_redraw(lambda:Dot(Q(),radius=.075,color=PURPLE))
        join=always_redraw(lambda:Line(P(),Q(),color=ORANGE,stroke_width=3))
        pt=math("P",30,ORANGE);qt=math("Q",30,PURPLE)
        pt.move_to(P()+[.23,.27,0]);qt.move_to(Q()+[-.23,-.27,0])
        pt.add_updater(lambda m:m.move_to(P()+[.23,.27,0]));qt.add_updater(lambda m:m.move_to(Q()+[-.23,-.27,0]))
        moving=VGroup(join,pdot,qdot,pt,qt)
        dl=math(r"PQ\approx",34).move_to([-.65,-3.35,0])
        dn=DecimalNumber(branch_distance(.55,1.8),num_decimal_places=3,font_size=34,color=ORANGE).next_to(dl,RIGHT,buff=.16)
        dn.add_updater(lambda m:m.set_value(branch_distance(a.get_value(),b.get_value())).next_to(dl,RIGHT,buff=.16))
        numeric=VGroup(dl,dn)
        hint=text("图形对称，不代表任意 P、Q 对称",26,MUTED).move_to([0,-4.2,0])
        proof=math(r"P:\ x+y\ge2\qquad Q:\ x+y\le-2",31).move_to([0,-5.1,0])
        bottom=text("先观察变化，再找能取到的下界",25,MUTED).move_to([0,-6.05,0])
        self.add(moving,numeric,hint,proof,bottom)
        audit.watch(brand,title,formula,state,xlab,ylab,O,pt,qt,numeric,hint,proof,bottom)
        audit.mark("independent_start",a=.55,b=1.8,d=branch_distance(.55,1.8));self.wait(1)
        self.play(a.animate.set_value(2.3),b.animate.set_value(.7),run_time=2.6,rate_func=smooth)
        audit.mark("independent_state_2",a=2.3,b=.7,d=branch_distance(2.3,.7));self.wait(.5)
        self.play(a.animate.set_value(1.4),b.animate.set_value(2.4),run_time=2.6,rate_func=smooth)
        self.wait(.5)
        support=VGroup(Line(axes.c2p(-1,3),axes.c2p(3,-1),color=GREEN,stroke_width=2.5),
                      Line(axes.c2p(-3,1),axes.c2p(1,-3),color=GREEN,stroke_width=2.5))
        labels=VGroup(math("x+y=2",27,GREEN).move_to(axes.c2p(1.65,2.35)),
                      math("x+y=-2",27,GREEN).move_to(axes.c2p(-1.65,-2.35)))
        self.play(Create(support),FadeIn(labels),Transform(state,text("两条平行线，把两支曲线隔开",28,GREEN).move_to(state)),
                  Transform(hint,text("曲线上的点，都在两条线的外侧",26,MUTED).move_to(hint)),run_time=.8)
        audit.watch(labels);audit.mark("parallel_supports",a=1.4,b=2.4);self.wait(1)
        normal=Line(axes.c2p(-1,-1),axes.c2p(1,1),color=GREEN,stroke_width=5)
        r=RightAngle(Line(axes.c2p(1,1),axes.c2p(-1,-1)),Line(axes.c2p(1,1),axes.c2p(-1,3)),length=.18,color=GREEN)
        self.play(Create(normal),Create(r),Transform(bottom,math(r"d_{\rm lines}=\frac{2-(-2)}{\sqrt2}=2\sqrt2",32,GREEN).move_to(bottom)),run_time=.6)
        self.wait(1)
        self.play(a.animate.set_value(1),b.animate.set_value(1),run_time=2.5,rate_func=smooth)
        self.play(Transform(state,text("接触点连线垂直，恰好取到下界",28,GREEN).move_to(state)),
                  Transform(hint,math(r"P(1,1),\quad Q(-1,-1)",33,GREEN).move_to(hint)),
                  Transform(proof,math(r"PQ_{\min}=2\sqrt2\approx2.828",34,GREEN).move_to(proof)),run_time=.4)
        audit.mark("minimum",a=1,b=1,d=support_distance());self.wait(1.8)
        self.play(Transform(bottom,math(r"k>0:\quad d_{\min}=2\sqrt{2k}",34,GREEN).move_to(bottom)),run_time=.3)
        self.wait(2.6)
        # Independent initial pair restored only after motion objects fade out.
        self.play(FadeOut(moving),FadeOut(support),FadeOut(labels),FadeOut(normal),FadeOut(r),run_time=.3)
        a.set_value(.55);b.set_value(1.8)
        self.play(FadeIn(moving),Transform(state,text("两点在各自分支上独立移动",28,MUTED).move_to(state)),
                  Transform(hint,text("图形对称，不代表任意 P、Q 对称",26,MUTED).move_to(hint)),
                  Transform(proof,math(r"P:\ x+y\ge2\qquad Q:\ x+y\le-2",31).move_to(proof)),
                  Transform(bottom,text("先观察变化，再找能取到的下界",25,MUTED).move_to(bottom)),run_time=.3)
        self.wait(.5);audit.mark("loop_reset");audit.finish()
