"""Three T037 teaching loops; geometry and displayed values share one model."""
from pathlib import Path
import json
import sys
import numpy as np
from manim import *

sys.path.insert(0,str(Path(__file__).resolve().parent))
from model import Triangle, varying_base, equilateral, right_triangle

config.frame_width=9
config.frame_height=16
config.background_color='#F7F8FA'
INK='#213044'; MUTED='#526275'; BLUE='#2778BD'; ORANGE='#AE512A'
PURPLE='#8055B2'; GREEN='#158068'; LIGHT='#A7B4C2'
FONT='Microsoft YaHei'
FOOTER=('查结论 · 看图解 · 学证明｜知树 App','公众号 ok-shuxue｜获取入口')


def text(value,size=26,color=INK):
    return Text(value,font=FONT,font_size=size,color=color)


def formula(value,size=38,color=INK):
    return MathTex(value,font_size=size,color=color)


def fit(m,width=7.8):
    if m.width>width:m.scale_to_fit_width(width)
    return m


def project(t,p,scale=.72,base=.55):
    # Same scale in x and y, including throughout every motion.
    return np.array([(p[0]-t.c/2)*scale,p[1]*scale+base,0.])


def outline(t,scale=.72,fill=True):
    return Polygon(*(project(t,p,scale) for p in (t.A,t.B,t.C)),
                   stroke_color=INK,stroke_width=3,fill_color=BLUE,fill_opacity=.12 if fill else 0)


def outward(u,v,offset=.34):
    dx,dy=v[0]-u[0],v[1]-u[1]
    return np.array([dy,-dx,0.])*offset/np.hypot(dx,dy)


def labels(getter,scale=.72,side_names=('a','b','c')):
    result=VGroup()
    for name,attr,delta in (('A','A',DL*.29),('B','B',DR*.29),('C','C',UP*.32)):
        m=formula(name,29)
        m.add_updater(lambda mob,dt,a=attr,d=delta:mob.move_to(project(getter(),getattr(getter(),a),scale)+d))
        result.add(m)
    for name,attrs in zip(side_names,(('B','C'),('C','A'),('A','B'))):
        if not name:continue
        m=formula(name,31,BLUE)
        def update(mob,dt,pair=attrs):
            t=getter();u=project(t,getattr(t,pair[0]),scale);v=project(t,getattr(t,pair[1]),scale)
            mob.move_to((u+v)/2+outward(u,v))
        m.add_updater(update);result.add(m)
    result.update(0)
    return result


def right_mark(t,h,u,v,scale):
    h,u,v=(project(t,p,scale) for p in (h,u,v))
    a=(u-h)/np.linalg.norm(u-h)*.17;b=(v-h)/np.linalg.norm(v-h)*.17
    return VMobject(color=MUTED,stroke_width=1.7).set_points_as_corners([h+a,h+a+b,h+b])


def circle_geometry(t,scale=.4,radii=False,connect=False):
    result=VGroup()
    if connect:
        for v in (t.A,t.B,t.C):
            result.add(DashedLine(project(t,t.I,scale),project(t,v,scale),color=LIGHT,stroke_width=1.8,dash_length=.12))
    result.add(Circle(radius=t.r*scale,color=BLUE,stroke_width=2.6).move_to(project(t,t.I,scale)))
    if radii:
        for h,v in zip(t.feet,(t.C,t.A,t.B)):
            result.add(Line(project(t,t.I,scale),project(t,h,scale),color=BLUE,stroke_width=2.7),right_mark(t,h,t.I,v,scale))
        result.add(formula('r',28,BLUE).move_to((project(t,t.I,scale)+project(t,t.feet[2],scale))/2+RIGHT*.26))
    result.add(Dot(project(t,t.I,scale),radius=.04,color=INK))
    result.add(formula('I',28).move_to(project(t,t.I,scale)+RIGHT*.45))
    return result


class Lesson:
    def start(self,title,status):
        self.events=[]
        self.title=fit(text(title,30)).move_to([0,6.95,0])
        self.status=fit(text(status,25,MUTED)).move_to([0,5.95,0])
        self.footer=VGroup(Line([-3.9,-6.45,0],[3.9,-6.45,0],color='#CDD3DB',stroke_width=1),
            fit(text(FOOTER[0],22,MUTED)).move_to([0,-6.95,0]),
            fit(text(FOOTER[1],20,MUTED)).move_to([0,-7.47,0]))
        self.panel=VGroup();self.add(self.title,self.status,self.footer)

    def state(self,status,rows=(),extra=(),duration=.4):
        next_status=fit(text(status,25,MUTED)).move_to(self.status)
        panel=VGroup(*(fit((formula(s,size,color) if kind=='m' else text(s,size,color))).move_to([0,y,0])
                       for kind,s,y,size,color in rows))
        anim=[ReplacementTransform(self.status,next_status)]
        if len(self.panel):anim.append(FadeOut(self.panel))
        if len(panel):anim.append(FadeIn(panel))
        self.play(*anim,*extra,run_time=duration)
        self.status=next_status;self.panel=panel

    def mark(self,name):
        self.events.append({'time':round(float(self.time),3),'name':name})

    def evidence(self):
        p=Path(config.media_dir)/f'{type(self).__name__}-story.json'
        p.parent.mkdir(parents=True,exist_ok=True)
        p.write_text(json.dumps({'scene':type(self).__name__,'duration':float(self.time),
                                'keyframes':self.events,'footer':FOOTER},ensure_ascii=False,indent=2),encoding='utf-8')


class T037HeronArea(Lesson,Scene):
    def construct(self):
        self.start('海伦公式：三边直接求面积','只知道三边，没有给高和角')
        t=varying_base(7)
        graph=VGroup(outline(t),labels(lambda:t,side_names=('5','6','7')))
        opening=fit(text('5 + 6 > 7，三边能组成三角形',25,MUTED)).move_to([0,-1.5,0])
        self.add(graph,opening);self.wait(1.4);self.mark('opening')
        self.state('先算半周长，注意除以 2',[
            ('m',r'p=\frac{5+6+7}{2}=9',-1.2,42,BLUE)],extra=(FadeOut(opening),))
        self.wait(1.4);self.mark('semiperimeter')
        self.state('根号里：半周长，乘三个半周长差',[
            ('m',r'S=\sqrt{p(p-a)(p-b)(p-c)}',-1.15,36,INK),
            ('m',r'=\sqrt{9\cdot(9-5)(9-6)(9-7)}',-2.55,37,BLUE),
            ('m',r'=\sqrt{9\cdot4\cdot3\cdot2}=6\sqrt6',-4.0,39,GREEN)])
        self.wait(2.8);self.mark('worked_567')
        c=ValueTracker(7)
        get=lambda:varying_base(c.get_value())
        motion=always_redraw(lambda:outline(get()))
        moving_labels=labels(get,side_names=('a','b','c'))
        self.state('固定 a=5、b=6，只改变底边 c',[
            ('m',r'p=\frac{a+b+c}{2}',-1.1,36,INK),
            ('m',r'S=\sqrt{p(p-a)(p-b)(p-c)}',-2.25,36,INK),
            ('t','1 < c < 11，始终满足三角形不等式',-5.3,24,MUTED)],
            extra=(FadeOut(graph),FadeIn(motion),FadeIn(moving_labels)))
        live=VGroup()
        for x,name,value,color in ((-2.5,'c',lambda:c.get_value(),BLUE),(0,'p',lambda:get().p,INK),(2.5,'S',lambda:get().S,GREEN)):
            prefix=formula(name+'=',30,color).move_to([x-.55,-3.8,0])
            number=DecimalNumber(value(),num_decimal_places=2,font_size=32,color=color)
            number.move_to([x+.40,-3.8,0])
            number.add_updater(lambda mob,dt,f=value,xx=x:mob.set_value(f()).move_to([xx+.40,-3.8,0]))
            live.add(prefix,number)
        self.play(FadeIn(live),run_time=.35)
        self.play(c.animate.set_value(10),run_time=3.6,rate_func=linear)
        self.wait(1);self.mark('c10_smaller_area')
        self.play(c.animate.set_value(7),run_time=3.6,rate_func=linear)
        self.wait(.8);self.mark('return_to_7')
        self.state('三边确定，就能直接算面积',[
            ('m',r'a=5,\quad b=6,\quad c=7',-1.2,35,INK),
            ('m',r'S=6\sqrt6\approx14.70',-2.8,43,GREEN),
            ('t','改变三边，图形和面积一起更新',-4.3,25,MUTED)],extra=(FadeOut(live),))
        self.wait(2);self.mark('conclusion')
        self.state('只知道三边，没有给高和角',extra=(FadeOut(motion),FadeOut(moving_labels),FadeIn(graph),FadeIn(opening)),duration=.6)
        self.wait(.8);self.mark('loop_return');self.evidence()


class T037HeronIncircle(Lesson,Scene):
    def construct(self):
        self.start('半周长的三个差，原来是切线段','同一顶点引出的两条切线段等长')
        t=Triangle(13,14,15);s=.4
        D,E,F=t.feet
        basic=VGroup(outline(t,s,False),labels(lambda:t,s,('','','')),circle_geometry(t,s))
        foot_labels=VGroup(*(formula(name,27).move_to(project(t,h,s)+delta)
            for name,h,delta in (('D',D,RIGHT*.35),('E',E,LEFT*.35),('F',F,DOWN*.34))))
        initial=VGroup(basic,foot_labels)
        note=formula(r'a=13,\quad b=14,\quad c=15',34).move_to([0,-1.3,0])
        self.add(initial,note);self.wait(1.4);self.mark('opening')
        pairs=VGroup()
        for name,vertex,feet,color,statement in (
            ('x',t.A,(E,F),BLUE,r'AF=AE=x=p-a=8'),
            ('y',t.B,(F,D),ORANGE,r'BF=BD=y=p-b=7'),
            ('z',t.C,(D,E),PURPLE,r'CD=CE=z=p-c=6')):
            pair=VGroup()
            for h in feet:
                u=project(t,vertex,s);v=project(t,h,s)
                pair.add(Line(u,v,color=color,stroke_width=4.2))
                midpoint=(u+v)/2
                # Outward from triangle centroid, with extra clearance on AB.
                center=sum((project(t,p,s) for p in (t.A,t.B,t.C)))/3
                d=midpoint-center;d=d/np.linalg.norm(d)*.30
                pair.add(formula(name,29,color).move_to(midpoint+d))
            self.state('三边已知，三对切线段都能算',[
                ('m',r'p=\frac{13+14+15}{2}=21',-1.1,36,INK),
                ('m',statement,-2.6,39,color),
                ('t','每条边，都是相邻两段切线段之和',-4.4,25,MUTED)],
                extra=(FadeOut(note),Create(pair)) if len(pairs)==0 else (Create(pair),),duration=.7)
            pairs.add(pair);self.wait(1.3);self.mark('tangent_'+name)
        self.state('三个差有几何含义；代入海伦公式',[
            ('m',r'x=p-a=8,\ y=p-b=7,\ z=p-c=6',-1.0,31,INK),
            ('m',r'S=\sqrt{p\,x\,y\,z}',-2.4,43,BLUE),
            ('m',r'=\sqrt{21\cdot8\cdot7\cdot6}=84',-3.9,39,GREEN),
            ('t','这里展示对应关系；完整证明见 PDF',-5.35,23,MUTED)])
        self.wait(2.8);self.mark('heron_correspondence')
        areas=VGroup(*(Polygon(*(project(t,p,s) for p in (t.I,u,v)),stroke_opacity=0,fill_color=color,fill_opacity=.18)
                      for u,v,color in ((t.B,t.C,BLUE),(t.C,t.A,ORANGE),(t.A,t.B,GREEN))))
        area_graph=VGroup(areas,outline(t,s,False),labels(lambda:t,s,('a','b','c')),circle_geometry(t,s,True,True))
        self.state('连接内心与三个顶点，三块的高都是 r',[
            ('m',r'S=\frac{ar}{2}+\frac{br}{2}+\frac{cr}{2}',-1.3,38,INK),
            ('m',r'=\frac{a+b+c}{2}r=pr',-2.9,41,BLUE)],
            extra=(FadeOut(initial),FadeOut(pairs),FadeIn(area_graph)),duration=.7)
        self.wait(2.3);self.mark('three_equal_heights')
        self.state('面积已经求出，内切圆半径随之求出',[
            ('m',r'r=\frac Sp=\frac{84}{21}=4',-1.6,46,GREEN),
            ('t','海伦公式求面积，S=pr 再求半径',-3.4,25,INK),
            ('t','三边 13、14、15，得到 S=84、r=4',-4.75,24,MUTED)])
        self.wait(2.3);self.mark('radius_4')
        self.state('同一顶点引出的两条切线段等长',extra=(FadeOut(area_graph),FadeIn(initial),FadeIn(note)),duration=.6)
        self.wait(.8);self.mark('loop_return');self.evidence()


class T037HeronSpecial(Lesson,Scene):
    def construct(self):
        self.start('特殊三角形，也藏在海伦公式里','等边三角形：三个半周长差都相同')
        ell=ValueTracker(4)
        get=lambda:equilateral(ell.get_value())
        graph=VGroup(always_redraw(lambda:outline(get(),.75)),labels(get,.75,(r'\ell',r'\ell',r'\ell')))
        opening=formula(r'a=b=c=\ell>0',38,BLUE).move_to([0,-1.2,0])
        self.add(graph,opening);self.wait(1.3);self.mark('opening')
        self.state('把三条相同的边，分别代入四个因子',[
            ('m',r'p=\frac{3\ell}{2},\quad p-a=p-b=p-c=\frac\ell2',-1.2,35,INK),
            ('m',r'S=\sqrt{\frac{3\ell}{2}\left(\frac\ell2\right)^3}',-2.8,43,BLUE),
            ('m',r'=\frac{\sqrt3}{4}\ell^2',-4.4,47,GREEN)],extra=(FadeOut(opening),))
        self.wait(2.6);self.mark('equilateral_substitution')
        self.state('边长变成 6：面积按边长的平方变化',[
            ('m',r'S=\frac{\sqrt3}{4}\ell^2',-1.3,43,INK),
            ('t','边长变为 k 倍，面积变为 k² 倍',-4.7,24,MUTED)])
        live=VGroup()
        for x,name,value in ((-1.9,r'\ell=',lambda:ell.get_value()),(1.6,'S=',lambda:get().S)):
            prefix=formula(name,34,BLUE).move_to([x-.6,-3.0,0])
            n=DecimalNumber(value(),num_decimal_places=2,font_size=34,color=GREEN).move_to([x+.4,-3.,0])
            n.add_updater(lambda mob,dt,f=value,xx=x:mob.set_value(f()).move_to([xx+.4,-3.,0]))
            live.add(prefix,n)
        self.play(FadeIn(live),run_time=.3)
        self.play(ell.animate.set_value(6),run_time=2.8,rate_func=linear)
        self.wait(.8);self.mark('equilateral_side_6')
        self.state('边长 6，海伦公式得到熟悉的面积',[
            ('m',r'S=\frac{\sqrt3}{4}\cdot6^2=9\sqrt3',-1.4,43,GREEN),
            ('t','等边三角形面积公式，是海伦公式的特例',-3.3,24,MUTED)],extra=(FadeOut(live),))
        self.wait(1.8);self.mark('equilateral_result')
        t=right_triangle(3,4)
        right=VGroup(outline(t,1.02),labels(lambda:t,1.02,('a','b','c')),
                     right_mark(t,t.C,t.A,t.B,1.02))
        self.state('直角三角形：C 为直角，c 是斜边',[
            ('m',r'c^2=a^2+b^2,\qquad a,b>0',-1.25,37,BLUE)],
            extra=(FadeOut(graph),FadeIn(right)),duration=.65)
        self.wait(1.3);self.mark('right_triangle_C')
        self.state('用勾股关系，把四个因子配成两对',[
            ('m',r'p(p-c)=\frac{(a+b)^2-c^2}{4}=\frac{ab}{2}',-1.1,33,BLUE),
            ('m',r'(p-a)(p-b)=\frac{c^2-(a-b)^2}{4}=\frac{ab}{2}',-2.6,32,ORANGE),
            ('m',r'S=\sqrt{\frac{ab}{2}\cdot\frac{ab}{2}}=\frac{ab}{2}',-4.3,41,GREEN)])
        self.wait(3.1);self.mark('right_factor_pairing')
        numeric_labels=labels(lambda:t,1.02,('3','4','5'))
        numeric=VGroup(outline(t,1.02),numeric_labels,right_mark(t,t.C,t.A,t.B,1.02))
        self.state('3、4、5 代入，与底乘高完全一致',[
            ('m',r'p=6,\quad S=\sqrt{6\cdot3\cdot2\cdot1}=6',-1.2,36,INK),
            ('m',r'\frac12\cdot3\cdot4=6',-2.9,44,GREEN),
            ('t','解题已知直角边时，直接用 ab/2 更省步骤',-4.6,23,MUTED)],
            extra=(FadeOut(right),FadeIn(numeric)))
        self.wait(2.4);self.mark('right_345_result')
        ell.set_value(4)
        self.state('等边三角形：三个半周长差都相同',extra=(FadeOut(numeric),FadeIn(graph),FadeIn(opening)),duration=.6)
        self.wait(.8);self.mark('loop_return');self.evidence()
