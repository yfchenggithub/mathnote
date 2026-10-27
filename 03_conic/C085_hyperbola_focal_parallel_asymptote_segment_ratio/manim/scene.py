"""C085: familiar division -> actual construction -> invariant -> projection."""
from pathlib import Path
import sys,json
sys.path.insert(0,str(Path(__file__).resolve().parent))
from model import Configuration,screen,familiar_points
import numpy as np
from manim import *

config.frame_width=9
config.frame_height=16
config.background_color='#F7F8FA'
INK='#213044';MUTED='#526275';BLUE='#2778BD';ORANGE='#CD6031'
TEAL='#158068';PURPLE='#8055B2';AXIS='#A7B4C2'


class C085FocalAsymptoteRatio(Scene):
    def construct(self):
        b=ValueTracker(4)
        snapshots=[]
        def model():return Configuration(3,b.get_value())
        def txt(s,size=30,color=INK):return Text(s,font='Microsoft YaHei',font_size=size,color=color)
        def math(s,size=36,color=INK):return MathTex(s,font_size=size,color=color)
        def at(m,x,y):
            m.move_to([x,y,0])
            if m.width>8.0 or m.get_left()[0]<-4.15 or m.get_right()[0]>4.15:
                raise ValueError('Text exceeds safe width: '+str(m))
            return m
        title=at(txt('两段之比，为什么这样整齐？',36),0,7.02)
        status=at(txt('先看一条线，分成相邻两段',30),0,5.75)
        brand=at(txt('C085  ·  知树数学',20,MUTED),0,-7.35)
        self.add(title,status,brand)
        def core(points):
            F,M,N=[np.array(P) for P in points]
            lines=VGroup(Line(F,M,color=BLUE,stroke_width=6),Line(M,N,color=ORANGE,stroke_width=6))
            dots=VGroup(*[Dot(P,radius=.065,color=INK) for P in (F,M,N)])
            labels=VGroup(math('F',30).next_to(F,UR,buff=.14),math('M',30).next_to(M,RIGHT,buff=.19),math('N',30).next_to(N,DL,buff=.14))
            return VGroup(lines,dots,labels)
        familiar=core(familiar_points())
        # Intro labels use the familiar collinear order, all above the segment.
        for label,P in zip(familiar[2],familiar_points()):label.next_to(P,UP,buff=.22)
        intro_caption=at(txt('蓝色是 FM，橙色是 MN',30),0,-1.1)
        intro_lengths=at(math(r'FM=\frac83,\qquad MN=\frac32',38),0,-2.4)
        self.add(familiar)
        self.wait(.7)
        self.play(FadeIn(intro_caption),FadeIn(intro_lengths),run_time=.4)
        self.wait(1.8)
        def axes():
            return VGroup(Line(screen((0,0)),screen((6.2,0)),color=AXIS,stroke_width=1.4),
                          Line(screen((0,-4)),screen((0,2.7)),color=AXIS,stroke_width=1.4),
                          math('O',24,MUTED).next_to(screen((0,0)),DL,buff=.1),
                          math('x',24,MUTED).next_to(screen((6.2,0)),RIGHT,buff=.08),
                          math('y',24,MUTED).next_to(screen((0,2.7)),UP,buff=.08))
        def curves(m):
            return ParametricFunction(lambda y:screen(m.curve(y)),t_range=[-3.8,2.5,.04],color=TEAL,stroke_width=3.1)
        def asymptotes(m):
            return VGroup(DashedLine(screen((0,0)),screen((2.5/m.k,2.5)),color=PURPLE,stroke_width=2.2,dash_length=.1),
                          DashedLine(screen((0,0)),screen((3.8/m.k,-3.8)),color=PURPLE,stroke_width=2.2,dash_length=.1))
        axy=axes();cur=curves(model());asy=asymptotes(model())
        newstatus=at(txt('放回双曲线：过焦点，平行一条渐近线',28),0,5.75)
        condition=at(math(r'\frac{x^2}{a^2}-\frac{y^2}{b^2}=1,\quad a=3',32),0,4.9)
        self.play(Transform(status,newstatus),FadeOut(intro_caption),FadeOut(intro_lengths),
                  FadeIn(axy),Create(cur),Create(asy),Transform(familiar,core([screen(P) for P in (model().F,model().M,model().N)])),
                  FadeIn(condition),run_time=1.6)
        self.wait(.6)
        # Fade emphasis travels along the parallel segments, preserving geometry.
        slope_note=at(txt('N 在另一条渐近线上；点序是 F—M—N',28),0,-3.25)
        self.play(FadeIn(slope_note),Indicate(asy[0],color=PURPLE,scale_factor=1),Indicate(familiar[0],color=PURPLE,scale_factor=1),run_time=1)
        self.wait(1.2)
        def live_core():
            m=model();g=core([screen(P) for P in (m.F,m.M,m.N)])
            record=m.snapshot();record['time']=float(self.time)
            record['core_bounds']=[float(g.get_left()[0]),float(g.get_right()[0]),float(g.get_bottom()[1]),float(g.get_top()[1])]
            snapshots.append(record)
            return g
        live=always_redraw(live_core);live_curve=always_redraw(lambda:curves(model()));live_asy=always_redraw(lambda:asymptotes(model()))
        self.remove(familiar,cur,asy);self.add(live_curve,live_asy,live)
        lengths=VGroup()
        for name,color,x,key in [('FM',BLUE,-2.05,'fm'),('MN',ORANGE,1.8,'mn')]:
            lab=math(name+(r'\approx' if key=='fm' else '='),34,color).move_to([x-.55,-3.25,0])
            val=DecimalNumber(getattr(model(),key),num_decimal_places=2,font_size=34,color=color).move_to([x+.65,-3.25,0])
            val.add_updater(lambda z,key=key:z.set_value(getattr(model(),key)))
            lengths.add(lab,val)
        b_label=math(r'b\approx',30,MUTED).move_to([-.65,-2.65,0])
        b_num=DecimalNumber(4,num_decimal_places=2,font_size=30,color=MUTED).move_to([.6,-2.65,0])
        b_num.add_updater(lambda z:z.set_value(b.get_value()))
        ratio_label=at(math(r'\frac{FM}{MN}=\frac{b^2}{a^2}\approx',37),-.6,-4.5)
        ratio_num=DecimalNumber(model().ratio,num_decimal_places=2,font_size=37,color=TEAL).move_to([1.35,-4.5,0])
        ratio_num.add_updater(lambda z:z.set_value(model().ratio))
        invariant=at(txt('固定 a，橙段 MN 始终长 1.50',29,ORANGE),0,-5.7)
        self.play(FadeOut(slope_note),Transform(status,at(txt('改变 b：看橙段长度，不只看位置',29),0,5.75)),
                  FadeIn(lengths),FadeIn(b_label),FadeIn(b_num),FadeIn(ratio_label),FadeIn(ratio_num),FadeIn(invariant),run_time=.5)
        self.wait(.8)
        self.play(b.animate.set_value(2.25),run_time=3,rate_func=smooth)
        self.wait(1.1)
        self.play(b.animate.set_value(3),run_time=2.2,rate_func=smooth)
        self.wait(1.1)
        self.play(b.animate.set_value(4),run_time=2.2,rate_func=smooth)
        self.wait(1.3)
        # One proof idea: same slope -> same projection multiplier cancels.
        for mob in [live,live_curve,live_asy,b_num,ratio_num,*lengths]:mob.clear_updaters()
        self.play(Transform(status,at(txt('为什么？先把两段投影到水平方向',29),0,5.75)),
                  FadeOut(lengths),FadeOut(b_label),FadeOut(b_num),FadeOut(ratio_label),FadeOut(ratio_num),FadeOut(invariant),run_time=.5)
        m=model();base=-4.4
        projection=VGroup(*[DashedLine(screen(P),screen((P[0],base)),color=AXIS,stroke_width=1.4,dash_length=.08) for P in (m.F,m.M,m.N)])
        dims=VGroup(Line(screen((m.M[0],base)),screen((m.F[0],base)),color=BLUE,stroke_width=4),
                    Line(screen((m.N[0],base)),screen((m.M[0],base)),color=ORANGE,stroke_width=4))
        dimlabels=VGroup(math('t',30,BLUE).next_to(dims[0],DOWN,buff=.15),math(r'c/2-t',28,ORANGE).next_to(dims[1],DOWN,buff=.15))
        why=at(txt('同一斜率：长度比等于水平投影比',29),0,-4.2)
        step1=at(math(r't=\frac{b^2}{2c},\qquad \frac c2-t=\frac{a^2}{2c}',36),0,-5.25)
        step2=at(math(r'\frac{FM}{MN}=\frac{t}{c/2-t}=\frac{b^2}{a^2}',39,TEAL),0,-6.35)
        self.play(Create(projection),Create(dims),FadeIn(dimlabels),FadeIn(why),run_time=.9)
        self.play(FadeIn(step1),run_time=.4);self.wait(1.5)
        self.play(FadeIn(step2),run_time=.4);self.wait(2)
        self.play(FadeOut(projection),FadeOut(dims),FadeOut(dimlabels),FadeOut(why),FadeOut(step1),FadeOut(step2),
                  Transform(status,at(txt('记住条件，再记住这一个比例',30),0,5.75)),run_time=.6)
        final1=at(math(r'\frac{FM}{MN}=\frac{b^2}{a^2}=e^2-1',42,TEAL),0,-3.6)
        final2=at(math(r'e=\sqrt{1+\frac{FM}{MN}}',40),0,-5)
        final3=at(txt('过焦点 · 平行一条 · 交另一条',29),0,-6.15)
        self.play(FadeIn(final1),FadeIn(final2),FadeIn(final3),run_time=.5)
        self.wait(2.5)
        # Return to the exact initial state without a blank reset frame.
        reset=core(familiar_points())
        for label,P in zip(reset[2],familiar_points()):label.next_to(P,UP,buff=.22)
        self.play(Transform(live,reset),FadeOut(VGroup(axy,live_curve,live_asy,condition,final1,final2,final3)),
                  Transform(status,at(txt('先看一条线，分成相邻两段',30),0,5.75)),run_time=.8)
        self.wait(.5)
        target=Path(config.media_dir)/'C085_frame_math.json'
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_text(json.dumps(snapshots,indent=2),encoding='utf8')
