import math
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from manim import *
from model import state,area_maximum,clip_line,beam

config.background_color='#F7F8FA'
config.frame_width,config.frame_height=9,16
INK='#213044'; MUTED='#526275'; BLUE='#2778BD'; PURPLE='#7959A6'
ORANGE='#CD6031'; GREEN='#158068'; AXIS='#A7B4C2'


def cn(s,size=26,color=INK): return Text(s,font='Microsoft YaHei',font_size=size,color=color)
def eq(s,size=34,color=INK): return MathTex(s,font_size=size,color=color)
def v(p): return np.array([p[0],p[1],0.])
def mapper(scale=1.,centre=(0,.8)):
    return lambda p:np.array([scale*p[0]+centre[0],scale*p[1]+centre[1],0.])


def base(a,b,xy,box=(-3.5,3.5,-3.1,3.1),circle=False):
    xmin,xmax,ymin,ymax=box; c=math.sqrt(a*a-b*b)
    g=VGroup(Line(xy((xmin,0)),xy((xmax,0)),color=AXIS,stroke_width=1.4),Line(xy((0,ymin)),xy((0,ymax)),color=AXIS,stroke_width=1.4))
    if circle:
        g.add(ParametricFunction(lambda t:xy((a*np.cos(t),a*np.sin(t))),t_range=[0,TAU],color=GREEN,stroke_width=2.2))
    g.add(ParametricFunction(lambda t:xy((a*np.cos(t),b*np.sin(t))),t_range=[0,TAU],color=INK,stroke_width=3.5))
    for x,name,color in ((-c,'F_1',BLUE),(c,'F_2',PURPLE)):
        g.add(Dot(xy((x,0)),color=color,radius=.055),eq(name,24,color).move_to(xy((x,0))+DOWN*.3))
    g.add(eq('O',24).move_to(xy((0,0))+np.array([-.17,-.27,0])),eq('x',24).move_to(xy((xmax+.22,-.23))))
    return g


def foot_geometry(s,xy,box=(-3.5,3.5,-3,3),radii=False,fill=False):
    n=v(s['n']); u=np.array([-n[1],n[0],0.]); g=VGroup()
    if fill:
        g.add(Polygon(*[xy(s[k]) for k in ('f1','h1','h2','f2')],stroke_width=0,fill_color=GREEN,fill_opacity=.14))
    g.add(Line(*[xy(p) for p in clip_line(s['n'],s['h'],box)],color=ORANGE,stroke_width=3.2))
    for j,color in ((1,BLUE),(2,PURPLE)):
        f,h=xy(s[f'f{j}']),xy(s[f'h{j}'])
        g.add(Line(f,h,color=color,stroke_width=4.2),Dot(h,color=color,radius=.065))
        z=.14
        g.add(VMobject(color=color,stroke_width=1.7).set_points_as_corners([h+z*u,h+z*(u-n),h-z*n]))
        visibility=min(1,max(0,(s['chord']-.18)/.35))
        offset=.28*n+(-.16 if j==1 else .16)*u
        g.add(eq(f'H_{j}',25,color).move_to(h+offset).fade(1-visibility))
        if radii:
            g.add(Line(xy((0,0)),h,color=color,stroke_width=2.4,stroke_opacity=.7))
    g.add(Dot(xy(s['p']),color=ORANGE,radius=.065))
    g.add(eq('P',25).move_to(xy(s['p'])+(-.3*n if s['chord']>.3 else .3*n)))
    return g


def readout(formula,value,position,color=INK,size=32):
    label=eq(formula+r'\approx',size,color)
    number=DecimalNumber(88.88,num_decimal_places=2,font_size=size,color=color)
    g=VGroup(label,number).arrange(RIGHT,buff=.12).move_to(position)
    anchor=number.get_right().copy()
    number.add_updater(lambda m:m.set_value(value()).align_to(anchor,RIGHT))
    number.update(0)
    return g


class C014DistanceProduct(Scene):
    def construct(self):
        phi=ValueTracker(40*DEGREES); xy=mapper()
        def s(): return state(phi.get_value())
        title=cn('两焦点垂距，乘积恒定',32).move_to([0,6.9,0])
        sub=eq(r'a=3,\quad b=2,\quad c=\sqrt5',31).move_to([0,5.9,0])
        caption=cn('分别从两个焦点向切线作垂线',25).move_to([0,4.85,0])
        diagram=always_redraw(lambda:foot_geometry(s(),xy))
        numbers=VGroup(readout('d_1',lambda:s()['d1'],[-1.9,-3.55,0],BLUE),readout('d_2',lambda:s()['d2'],[1.9,-3.55,0],PURPLE))
        result=eq(r'd_1d_2=4=b^2',43,GREEN).move_to([0,-4.9,0])
        foot=eq(r'd_i=F_iH_i\quad(i=1,2)',29,MUTED).move_to([0,-6.45,0])
        self.add(title,sub,caption,base(3,2,xy),diagram,numbers,result,foot)
        self.wait(1.5)
        self.play(Transform(caption,cn('一个距离增大，另一个距离减小',25).move_to(caption)),run_time=.3)
        self.play(phi.animate.set_value(140*DEGREES),run_time=5)
        self.wait(.8)
        self.play(Transform(caption,cn('走向长轴顶点，检查特殊位置',25).move_to(caption)),run_time=.3)
        self.play(phi.animate.set_value(0),run_time=3.5)
        self.play(Transform(caption,cn('长轴顶点：两个垂足都与 P 重合',24).move_to(caption)),Transform(foot,eq(r'(a+c)(a-c)=a^2-c^2=b^2',30,MUTED).move_to(foot)),run_time=.3)
        self.wait(2)
        self.play(Transform(caption,cn('距离积对所有切点成立',26).move_to(caption)),run_time=.3)
        self.play(phi.animate.set_value(40*DEGREES),run_time=2)
        self.wait(1)
        self.play(Transform(caption,cn('分别从两个焦点向切线作垂线',25).move_to(caption)),Transform(foot,eq(r'd_i=F_iH_i\quad(i=1,2)',29,MUTED).move_to(foot)),run_time=.3)
        self.wait(.8)


class C014PedalCircle(Scene):
    def construct(self):
        phi=ValueTracker(40*DEGREES); xy=mapper(.98)
        def s(): return state(phi.get_value())
        title=cn('两个垂足，同在主圆上',32).move_to([0,6.9,0])
        sub=eq(r'\frac{x^2}{9}+\frac{y^2}{4}=1',32).move_to([0,5.9,0])
        caption=cn('切点在椭圆上，垂足在主圆上',25).move_to([0,4.85,0])
        diagram=always_redraw(lambda:foot_geometry(s(),xy,radii=True))
        result=eq(r'OH_1=OH_2=3=a',41,GREEN).move_to([0,-3.95,0])
        circle_eq=eq(r'x_{H_i}^2+y_{H_i}^2=a^2',35).move_to([0,-5.15,0])
        foot=cn('主圆半径是 a',25,MUTED).move_to([0,-6.5,0])
        self.add(title,sub,caption,base(3,2,xy,circle=True),diagram,result,circle_eq,foot)
        self.wait(1.5)
        self.play(phi.animate.set_value(400*DEGREES),run_time=10,rate_func=smooth)
        self.play(Transform(caption,cn('垂足到中心的距离始终不变',25).move_to(caption)),Transform(foot,eq(r'OH_i^2=c^2+d_1d_2=a^2',31,MUTED).move_to(foot)),run_time=.35)
        self.wait(3)
        self.play(Transform(caption,cn('切点在椭圆上，垂足在主圆上',25).move_to(caption)),Transform(foot,cn('主圆半径是 a',25,MUTED).move_to(foot)),run_time=.35)
        self.wait(1)


class C014OpticalReflection(Scene):
    def construct(self):
        phi=ValueTracker(55*DEGREES); progress=ValueTracker(0); visibility=ValueTracker(1)
        xy=mapper(1.04)
        def s(): return state(phi.get_value())
        title=cn('从一个焦点，反射到另一个焦点',28).move_to([0,6.9,0])
        sub=eq(r'a=3,\quad b=2',32).move_to([0,5.9,0])
        caption=cn('沿 F₁ → P → F₂ 传播',27).move_to([0,4.85,0])
        def optics():
            q=s(); p=xy(q['p']); n=v(q['n']); g=VGroup()
            g.add(Line(*[xy(z) for z in clip_line(q['n'],q['h'])],color=ORANGE,stroke_width=3.2))
            g.add(DashedLine(p-2*n,p+.6*n,color=GREEN,stroke_width=2.6,dash_length=.12))
            for j,color in ((1,BLUE),(2,PURPLE)):
                f=xy(q[f'f{j}']); start,end=(f,p) if j==1 else (p,f)
                g.add(Line(start,end,color=color,stroke_width=3.5))
                g.add(Arrow(start+.42*(end-start),start+.62*(end-start),buff=0,color=color,stroke_width=3,max_tip_length_to_length_ratio=.32))
                ray=(f-p)/np.linalg.norm(f-p); inward=-n
                start_angle=np.arctan2(ray[1],ray[0]); finish=np.arctan2(inward[1],inward[0])
                delta=(finish-start_angle+PI)%TAU-PI
                g.add(Arc(radius=.39,start_angle=start_angle,angle=delta,arc_center=p,color=color,stroke_width=2.5))
                mid=start_angle+delta/2
                g.add(eq(r'\alpha_'+str(j),23,color).move_to(p+.66*np.array([np.cos(mid),np.sin(mid),0])))
            offset=.32*n+.24*np.array([-n[1],n[0],0.])
            g.add(Dot(p,color=ORANGE,radius=.065),eq('P',26).move_to(p+offset))
            return g
        drawing=always_redraw(optics)
        photon=always_redraw(lambda:Dot(xy(beam(phi.get_value(),progress.get_value())),color=ORANGE,radius=.09).fade(1-visibility.get_value()))
        legend=VGroup(cn('入射',23,BLUE),cn('反射',23,PURPLE),cn('法线',23,GREEN),cn('切线',23,ORANGE)).arrange(RIGHT,buff=.5).move_to([0,-3.4,0])
        law=cn('法线平分内角，切线平分外角',26).move_to([0,-4.65,0])
        formula=eq(r'\alpha_1=\alpha_2',38,GREEN).move_to([0,-5.65,0])
        foot=VGroup(eq(r'y_0\ne0',27,MUTED),cn('非退化焦点三角形',23,MUTED)).arrange(RIGHT,buff=.3).move_to([0,-6.75,0])
        self.add(title,sub,caption,base(3,2,xy),drawing,photon,legend,law,formula,foot)
        self.wait(1)
        self.play(progress.animate.set_value(1),run_time=3.5,rate_func=linear)
        self.wait(.7)
        self.play(visibility.animate.set_value(0),run_time=.25)
        self.play(phi.animate.set_value(115*DEGREES),run_time=2)
        progress.set_value(0)
        self.play(visibility.animate.set_value(1),run_time=.25)
        self.play(progress.animate.set_value(1),run_time=3.5,rate_func=linear)
        self.wait(.7)
        self.play(visibility.animate.set_value(0),Transform(caption,cn('切点改变，反射光仍通过另一焦点',24).move_to(caption)),run_time=.3)
        self.play(phi.animate.set_value(35*DEGREES),run_time=2.5)
        progress.set_value(0)
        self.play(visibility.animate.set_value(1),run_time=.25)
        self.play(progress.animate.set_value(1),run_time=3.5,rate_func=linear)
        self.wait(.7)
        self.play(visibility.animate.set_value(0),run_time=.25)
        self.play(phi.animate.set_value(55*DEGREES),run_time=1.5)
        progress.set_value(0)
        self.play(visibility.animate.set_value(1),Transform(caption,cn('沿 F₁ → P → F₂ 传播',27).move_to(caption)),run_time=.3)
        self.wait(.7)


class C014InterceptProduct(Scene):
    def construct(self):
        phi=ValueTracker(50*DEGREES); xy=mapper(1.14,(-.6,.8))
        def s(): return state(phi.get_value(),2,1)
        title=cn('切线与法线：截距积不变',31).move_to([0,6.9,0])
        sub=eq(r'a=2,\quad b=1,\quad c=\sqrt3',31).move_to([0,5.9,0])
        caption=cn('M 是法线截点，N 是切线截点',25).move_to([0,4.85,0])
        box=(-2.6,4.,-2.5,2.5)
        def drawing():
            q=s(); p=xy(q['p']); m=xy((q['xm'],0)); n=xy((q['xn'],0)); normal=v(q['n'])
            g=VGroup(Line(*[xy(z) for z in clip_line(q['n'],q['h'],box)],color=ORANGE,stroke_width=3.3),Line(m,p+.55*normal,color=GREEN,stroke_width=3.3))
            for point,name,color,offset in ((p,'P',INK,np.array([-.15,.3,0])),(m,'M',GREEN,DOWN*.36),(n,'N',ORANGE,DOWN*.36)):
                g.add(Dot(point,color=color,radius=.06),eq(name,26,color).move_to(point+offset))
            return g
        diagram=always_redraw(drawing)
        numbers=VGroup(readout('x_M',lambda:s()['xm'],[-1.9,-3.3,0],GREEN),readout('x_N',lambda:s()['xn'],[1.9,-3.3,0],ORANGE))
        result=eq(r'x_Mx_N=3=c^2',41,GREEN).move_to([0,-4.65,0])
        proof=VGroup(eq(r'x_M=\frac{c^2x_0}{a^2}',31,GREEN),eq(r'x_N=\frac{a^2}{x_0}',31,ORANGE)).arrange(RIGHT,buff=.75).move_to([0,-5.75,0])
        foot=eq(r'x_0y_0\ne0',29,MUTED).move_to([0,-6.9,0])
        self.add(title,sub,caption,base(2,1,xy,box),diagram,numbers,result,proof,foot)
        self.wait(1.5)
        self.play(phi.animate.set_value(70*DEGREES),run_time=3)
        self.wait(.8)
        self.play(phi.animate.set_value(40*DEGREES),run_time=3)
        self.wait(.8)
        self.play(Transform(caption,cn('两个坐标式相乘，消去切点横坐标',24).move_to(caption)),run_time=.3)
        self.play(phi.animate.set_value(60*DEGREES),run_time=2)
        self.wait(2)
        warning=cn('轴顶点不套用此式',25,MUTED).move_to([0,-6.9,0])
        self.play(Transform(foot,warning),run_time=.3)
        self.wait(2)
        self.play(phi.animate.set_value(50*DEGREES),run_time=1.5)
        self.play(Transform(caption,cn('M 是法线截点，N 是切线截点',25).move_to(caption)),Transform(foot,eq(r'x_0y_0\ne0',29,MUTED).move_to(foot)),run_time=.3)
        self.wait(.8)


class C014AreaMaximum(Scene):
    def construct(self):
        xy=mapper(1.35,(0,.6)); phi=ValueTracker(25*DEGREES)
        title=cn('面积上界，能否真的取到？',31).move_to([0,6.9,0])
        params=eq(r'a=2,\quad b=\sqrt3,\quad c=1',31).move_to([0,5.9,0])
        caption=cn('c<b：最大值在水平切线处',25).move_to([0,4.85,0])
        def panel(b):
            def s(): return state(phi.get_value(),2,b)
            ground=base(2,b,xy,(-2.7,2.7,-2.3,2.7))
            dynamic=always_redraw(lambda:foot_geometry(s(),xy,box=(-2.65,2.65,-2.25,2.65),fill=True))
            number=readout('S',lambda:s()['area'],[0,-3.55,0],INK,35)
            return VGroup(ground,dynamic,number)
        first=panel(math.sqrt(3))
        formula=eq(r'S=\frac12(d_1+d_2)H_1H_2',32).move_to([0,-4.6,0])
        maxtext=eq(r'S_{\max}=2bc=2\sqrt3<4',35,GREEN).move_to([0,-5.7,0])
        foot=cn('先检查取等构型能否实现',24,MUTED).move_to([0,-6.85,0])
        self.add(title,params,caption,first,formula,maxtext,foot)
        self.wait(1.5)
        self.play(phi.animate.set_value(PI/2),run_time=3)
        self.wait(1.7)
        self.play(FadeOut(first),FadeOut(params),FadeOut(maxtext),run_time=.35)
        phi.set_value(25*DEGREES)
        second=panel(1)
        params.become(eq(r'a=2,\quad b=1,\quad c=\sqrt3',31).move_to([0,5.9,0]))
        maxtext.become(eq(r'S_{\max}=a^2=4',38,GREEN).move_to([0,-5.7,0]))
        self.play(FadeIn(second),FadeIn(params),FadeIn(maxtext),Transform(caption,cn('c>b：倾斜切线能达到 a²',25).move_to(caption)),run_time=.35)
        star=area_maximum(2,1)[1]
        self.play(phi.animate.set_value(star),run_time=2)
        self.play(Transform(foot,eq(r'H_1H_2=d_1+d_2=\sqrt2\,a',29,MUTED).move_to(foot)),run_time=.3)
        self.wait(1.8)
        self.play(Transform(foot,cn('继续转到水平，面积反而减小',24,MUTED).move_to(foot)),run_time=.3)
        self.play(phi.animate.set_value(PI/2),run_time=1.8)
        self.wait(1)
        self.play(Transform(foot,cn('回到倾斜切线，面积再次达到 4',24,MUTED).move_to(foot)),run_time=.3)
        self.play(phi.animate.set_value(star),run_time=1.8)
        self.wait(1)
        rule=eq(r'S_{\max}=\begin{cases}2bc,&c\le b,\\a^2,&c\ge b.\end{cases}',34,GREEN).move_to([0,-5.75,0])
        self.play(Transform(maxtext,rule),Transform(caption,cn('先比较 c 与 b，再判断最大值',25).move_to(caption)),Transform(foot,cn('c=b 时，两种表达相同',24,MUTED).move_to(foot)),run_time=.35)
        self.wait(2.5)
        self.play(FadeOut(second),FadeOut(params),FadeOut(maxtext),run_time=.35)
        phi.set_value(25*DEGREES)
        first=panel(math.sqrt(3))
        params.become(eq(r'a=2,\quad b=\sqrt3,\quad c=1',31).move_to([0,5.9,0]))
        maxtext.become(eq(r'S_{\max}=2bc=2\sqrt3<4',35,GREEN).move_to([0,-5.7,0]))
        self.play(FadeIn(first),FadeIn(params),FadeIn(maxtext),Transform(caption,cn('c<b：最大值在水平切线处',25).move_to(caption)),Transform(foot,cn('先检查取等构型能否实现',24,MUTED).move_to(foot)),run_time=.35)
        self.wait(.8)
