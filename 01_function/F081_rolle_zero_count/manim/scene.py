from manim import *
import math,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import model

config.frame_width=9
config.frame_height=16
BG='#F7F8FA';INK='#213044';MUTED='#526275';BLUE='#2778BD';ORANGE='#CD6031';GREEN='#158068';PURPLE='#8055B2';AXIS='#A7B4C2'
BUILD=Path(__file__).resolve().parents[3]/'build/manim/F081-production-20261119'

class CaptionSwap(Animation):
    """Brief crossfade at fixed coordinates, without warping Chinese glyphs."""
    def __init__(self,mobject,target):
        self.target_caption=target.copy()
        super().__init__(mobject,rate_func=linear)
    def begin(self):
        self.old_caption=self.mobject.copy()
        super().begin()
    def interpolate_mobject(self,alpha):
        q=min(1,max(0,alpha*max(1,self.run_time/.25)))
        self.mobject.become(self.old_caption if q<.5 else self.target_caption)
        self.mobject.set_opacity(1-2*q if q<.5 else 2*q-1)

def cn(s,y,size=29,color=INK):
    m=Text(s,font='Microsoft YaHei',font_size=size,color=color)
    if m.width>7.95:m.scale_to_fit_width(7.95)
    return m.move_to([0,y,0])
def eq(s,y,size=37,color=INK):
    m=MathTex(s,font_size=size,color=color)
    if m.width>7.8:m.scale_to_fit_width(7.8)
    return m.move_to([0,y,0])
def header(scene,title,condition):
    scene.camera.background_color=BG
    scene.add(cn(title,7.15,32),cn(condition,6.35,26,MUTED))
    scene.add(cn('查结论 · 看图解 · 学证明｜知树 App',-6.85,22,MUTED),cn('公众号 ok-shuxue｜获取入口',-7.42,20,MUTED))
def axes(xr,yr,w,h,center):
    a=Axes(x_range=xr,y_range=yr,x_length=w,y_length=h,tips=True,axis_config={'color':AXIS,'stroke_width':1.6,'include_ticks':False,'tip_width':.09,'tip_height':.12}).move_to(center)
    return a
def labels(a):
    return VGroup(MathTex('x',font_size=26,color=MUTED).next_to(a.x_axis.get_end(),RIGHT,buff=.1),MathTex('y',font_size=26,color=MUTED).next_to(a.y_axis.get_end(),UP,buff=.1))
def point(a,x,y,color=ORANGE):return Dot(a.c2p(x,y),radius=.07,color=color)
def tangent(a,x,y,slope,half=.19,color=ORANGE):
    return Line(a.c2p(x-half,y-half*slope),a.c2p(x+half,y+half*slope),stroke_width=4,color=color)
def mark(scene,records,name,**values):
    visible=[m for m in scene.mobjects if m.width>.001 and m.height>.001]
    bounds=[min(m.get_left()[0] for m in visible),max(m.get_right()[0] for m in visible),min(m.get_bottom()[1] for m in visible),max(m.get_top()[1] for m in visible)]
    assert bounds[0]>-4.42 and bounds[1]<4.42 and bounds[2]>-7.85 and bounds[3]<7.85,(name,bounds)
    records.append({'name':name,'time':float(scene.time),'values':values,'bounds':bounds})
def save(name,records):
    BUILD.mkdir(parents=True,exist_ok=True)
    (BUILD/(name+'_key_states.json')).write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')

class F081EqualHeight(Scene):
    def construct(self):
        header(self,'两端等高，中间总有一处走平','在闭区间连续 · 在开区间处处可导')
        self.add(eq(r'f(-1)=f(1)=1',5.55,35))
        a=axes([-1.3,1.3,1],[-.65,2.65,1],7.1,6.7,[0,1.2,0])
        self.add(a,labels(a))
        for xx,letter in [(-1,'A'),(1,'B')]:
            d=point(a,xx,1,BLUE);self.add(d,MathTex(letter,font_size=29,color=INK).next_to(d,LEFT if xx<0 else RIGHT,buff=.15))
            self.add(MathTex(str(xx),font_size=26,color=MUTED).next_to(a.c2p(xx,0),DOWN,buff=.12))
        self.add(DashedLine(a.c2p(-1,1),a.c2p(1,1),color=AXIS,stroke_width=1.3,dash_length=.09))
        h=ValueTracker(1);s=ValueTracker(0);u=ValueTracker(0)
        f=lambda x:model.equal_height(x,h.get_value(),s.get_value(),u.get_value())
        df=lambda x:model.equal_slope(x,h.get_value(),s.get_value(),u.get_value())
        graph=always_redraw(lambda:a.plot(f,x_range=[-1,1,.008],color=BLUE,stroke_width=3.5,use_smoothing=False))
        x=ValueTracker(-.95)
        scan=always_redraw(lambda:VGroup(tangent(a,x.get_value(),f(x.get_value()),df(x.get_value())),point(a,x.get_value(),f(x.get_value()))))
        status=cn('从 A 走到 B，观察切线的方向',-3.15,29)
        formula=eq(r'-1<c<1,\quad f\,^{\prime}(c)=0',-4.15,35)
        note=cn('图中的形状是典型例子',-5.3,25,MUTED)
        self.add(graph,scan,status,formula,note);records=[]
        self.wait(.8);self.play(x.animate.set_value(0),run_time=1.8,rate_func=linear);self.wait(.85)
        mark(self,records,'moving_tangent_horizontal',x=0,slope=0)
        self.play(x.animate.set_value(.95),run_time=1.8,rate_func=linear);self.wait(.45);self.remove(scan)
        c=lambda:model.stationary(s.get_value())
        selected=always_redraw(lambda:VGroup(tangent(a,c(),f(c()),0),point(a,c(),f(c())),MathTex('C',font_size=29,color=ORANGE).next_to(a.c2p(c(),f(c())),UR if h.get_value()>=0 else DR,buff=.14)))
        self.add(selected)
        self.play(CaptionSwap(status,cn('上拱：内部最高处的切线水平',-3.15,29)),CaptionSwap(formula,eq(r'f\,^{\prime}(c)=0',-4.15,39)),run_time=.25)
        self.wait(.8);mark(self,records,'arch',amplitude=1,skew=0,c=c())
        self.play(CaptionSwap(status,cn('改变形状，水平切线仍然存在',-3.15,29)),run_time=.25)
        self.play(h.animate.set_value(0),run_time=1.6)
        self.play(CaptionSwap(status,cn('平走：内部每一点的导数都为 0',-3.15,29)),run_time=.25)
        flat=VGroup(*[VGroup(tangent(a,z,1,0,half=.13),point(a,z,1)) for z in [-.65,.65]])
        self.add(flat);self.wait(1.2);mark(self,records,'constant',amplitude=0,all_interior_slopes=0)
        self.remove(flat)
        self.play(CaptionSwap(status,cn('继续改变形状，观察水平切点',-3.15,29)),run_time=.25)
        self.play(h.animate.set_value(-1),run_time=1.6)
        self.play(CaptionSwap(status,cn('下凹：内部最低处的切线水平',-3.15,29)),run_time=.25)
        self.wait(1);mark(self,records,'valley',amplitude=-1,skew=0,c=c())
        self.play(CaptionSwap(note,cn('c 不必在两个端点的正中间',-5.3,27,MUTED)),s.animate.set_value(.75),run_time=1.8)
        self.wait(1);mark(self,records,'asymmetric_valley',amplitude=-1,skew=.75,c=c(),slope=df(c()))
        self.remove(selected)
        self.play(CaptionSwap(status,cn('把曲线逐渐变成多次起伏',-3.15,29)),u.animate.set_value(1),run_time=1.8)
        many=VGroup(*[VGroup(tangent(a,z,f(z),0,half=.1),point(a,z,f(z))) for z in model.WAVE_STATIONARY])
        self.add(many)
        self.play(CaptionSwap(note,cn('“至少一处”，不是“只有一处”',-5.3,27,MUTED)),run_time=.25)
        self.wait(2);mark(self,records,'four_horizontal_tangents',mixture=1,critical=list(model.WAVE_STATIONARY))
        self.remove(many)
        self.play(u.animate.set_value(0),h.animate.set_value(1),s.animate.set_value(0),CaptionSwap(status,cn('两端等高，内部至少有一条水平切线',-3.15,28)),run_time=1.8)
        self.wait(1.3);mark(self,records,'summary');save('equal_height',records)

class F081ZeroCount(Scene):
    def construct(self):
        header(self,'相邻零点之间，一定夹着什么？','以下均为多项式，连续且处处可导')
        self.add(eq(r'f_t(x)=x^3-3x+t',5.55,35))
        a=axes([-2.4,2.4,1],[-5.7,5.7,1],7.1,6.5,[0,1.3,0])
        self.add(a,labels(a));t=ValueTracker(0)
        def graph():
            group=VGroup()
            for seg in model.visible_cubic(t.get_value()):
                group.add(VMobject(color=BLUE,stroke_width=3.5).set_points_as_corners([a.c2p(x,y) for x,y in seg]))
            return group
        g=always_redraw(graph)
        critical=always_redraw(lambda:VGroup(*[VGroup(tangent(a,z,model.cubic(z,t.get_value()),0,half=.26),point(a,z,model.cubic(z,t.get_value()))) for z in [-1,1]]))
        roots=always_redraw(lambda:VGroup(*[point(a,z,0,GREEN) for z in model.cubic_roots(t.get_value())]))
        self.add(g,critical,roots)
        read=VGroup(MathTex('t=',font_size=32,color=INK),DecimalNumber(0,num_decimal_places=2,font_size=32,color=BLUE)).arrange(RIGHT,buff=.14).move_to([0,-2.45,0])
        read[1].add_updater(lambda m:m.set_value(t.get_value()))
        self.add(read,eq(r'f\,^{\prime}_t(x)=3x^2-3',-3.22,33))
        ny=-4.05
        self.add(Line([-3.5,ny,0],[3.5,ny,0],color=AXIS,stroke_width=1.5))
        for z in [-1,1]:
            p=[a.c2p(z,0)[0],ny,0];self.add(Dot(p,radius=.07,color=ORANGE),MathTex(str(z),font_size=26,color=ORANGE).next_to(p,DOWN,buff=.1))
        status=cn('相邻两个函数零点之间',-4.95,28)
        note=cn('至少夹着一个导数零点',-5.63,28)
        self.add(status,note);records=[]
        self.wait(.9)
        rs=model.cubic_roots(0)
        for j in range(2):
            interval=Line(a.c2p(rs[j],0),a.c2p(rs[j+1],0),color=PURPLE,stroke_width=6,stroke_opacity=.85)
            z=[-1,1][j]
            projection=DashedLine(a.c2p(z,0),a.c2p(z,model.cubic(z)),color=ORANGE,stroke_width=1.7,dash_length=.09)
            tag=MathTex('c_'+str(j+1),font_size=27,color=ORANGE).next_to(a.c2p(z,model.cubic(z)),UL if j==0 else DR,buff=.15)
            self.play(Create(interval),Create(projection),FadeIn(tag),run_time=.65)
            pulse=point(a,[-1,1][j],model.cubic([-1,1][j]))
            self.play(Indicate(pulse,scale_factor=1.8,color=ORANGE),run_time=.7)
            self.wait(.55);self.remove(interval,pulse,projection,tag)
        mark(self,records,'three_roots_two_derivative_roots',t=0,roots=rs,critical=[-1,1])
        self.play(CaptionSwap(status,cn('导数只有 2 个零点',-4.95,29)),CaptionSwap(note,cn('原函数最多有 3 个不同零点',-5.63,28)),run_time=.3)
        self.wait(1)
        self.play(CaptionSwap(status,cn('曲线整体上移，观察零点变化',-4.95,28)),CaptionSwap(note,cn('导数的零点始终是 -1、1',-5.63,27)),run_time=.25)
        self.play(t.animate.set_value(2),run_time=2.4)
        self.play(CaptionSwap(status,cn('t = 2：只有 2 个不同零点',-4.95,28)),CaptionSwap(note,cn('相切也算零点，同一位置只算一次',-5.63,26)),run_time=.3)
        self.wait(1.7);mark(self,records,'double_root',t=2,roots=model.cubic_roots(2))
        self.play(CaptionSwap(status,cn('继续上移，观察相切点的变化',-4.95,28)),CaptionSwap(note,cn('导数的两个零点仍然不变',-5.63,27)),run_time=.25)
        self.play(t.animate.set_value(3),run_time=1.8)
        self.play(CaptionSwap(status,cn('t = 3：只有 1 个零点',-4.95,29)),CaptionSwap(note,cn('导数的两个零点仍是 -1、1',-5.63,27)),run_time=.3)
        self.wait(1.5);mark(self,records,'one_root',t=3,roots=model.cubic_roots(3))
        self.play(CaptionSwap(status,cn('向下移动，观察零点如何出现',-4.95,28)),CaptionSwap(note,cn('原函数的不同零点数会改变',-5.63,27)),run_time=.25)
        self.play(t.animate.set_value(1),run_time=2.1)
        self.play(CaptionSwap(status,cn('t = 1：有 3 个不同零点',-4.95,29)),CaptionSwap(note,cn('“最多三个”，不保证“恰好三个”',-5.63,27)),run_time=.3)
        self.wait(1.8);mark(self,records,'three_roots_again',t=1,roots=model.cubic_roots(1))
        self.play(CaptionSwap(status,cn('两个导数零点，原函数最多三个',-4.95,27)),run_time=.25)
        self.play(t.animate.set_value(0),run_time=1.3)
        self.wait(.8);mark(self,records,'summary',t=0);save('zero_count',records)
