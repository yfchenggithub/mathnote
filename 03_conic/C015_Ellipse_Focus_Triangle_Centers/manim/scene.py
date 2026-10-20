import math
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from manim import *
from model import state,clip_line

BG='#F7F8FA'; INK='#213044'; MUTED='#526275'; BLUE='#2778BD'
GREEN='#158068'; ORANGE='#CD6031'; PURPLE='#7959A6'; AXIS='#A7B4C2'
config.background_color=BG
config.frame_width,config.frame_height=9,16


def cn(s,size=26,color=INK): return Text(s,font='Microsoft YaHei',font_size=size,color=color)
def eq(s,size=34,color=INK): return MathTex(s,font_size=size,color=color)
def xy_map(scale=.7,centre=(0,.65)):
    return lambda p:np.array([scale*p[0]+centre[0],scale*p[1]+centre[1],0.])


def swap(scene,*pairs):
    scene.play(*[FadeOut(old) for old,new in pairs],run_time=.15)
    for old,new in pairs: old.become(new)
    scene.play(*[FadeIn(old) for old,new in pairs],run_time=.15)


def header(title,caption,b=4):
    return (cn(title,31).move_to([0,6.9,0]),
            eq(r'a=5,\ b='+str(b)+r',\ c='+('3' if b==4 else '4')+r'\quad(y_0\ne0)',29).move_to([0,5.9,0]),
            cn(caption,25).move_to([0,4.85,0]))


def base(a,b,xy,box=(-5.5,5.5,-4.8,4.8),focal_inset=0):
    xmin,xmax,ymin,ymax=box; c=math.sqrt(a*a-b*b)
    g=VGroup(Line(xy((xmin,0)),xy((xmax,0)),color=AXIS,stroke_width=1.5),Line(xy((0,ymin)),xy((0,ymax)),color=AXIS,stroke_width=1.5),ParametricFunction(lambda t:xy((a*np.cos(t),b*np.sin(t))),t_range=[0,TAU],color=MUTED,stroke_width=2,stroke_opacity=.6))
    for x,name in ((-c,'F_1'),(c,'F_2')):
        offset=np.array([focal_inset if x<0 else -focal_inset,-.3,0])
        g.add(Dot(xy((x,0)),radius=.05,color=INK),eq(name,25).move_to(xy((x,0))+offset))
    g.add(Dot(xy((0,0)),radius=.03,color=AXIS),eq('O',24).move_to(xy((0,0))+np.array([-.18,-.26,0])),eq('x',24).move_to(xy((xmax+.2,-.28))))
    return g


def triangle(s,xy):
    return VGroup(Polygon(*[xy(s[k]) for k in ('f1','p','f2')],color=INK,stroke_width=3,fill_color=BLUE,fill_opacity=.035),Dot(xy(s['p']),radius=.065,color=ORANGE),eq('P',26,ORANGE).move_to(xy(s['p'])+np.array([.13,.28,0])))


def readout(symbol,value,pos,color=GREEN,size=32):
    label=eq(symbol+r'\approx',size,color)
    number=DecimalNumber(-8.88,num_decimal_places=2,font_size=size,color=color)
    group=VGroup(label,number).arrange(RIGHT,buff=.12).move_to(pos)
    anchor=number.get_right().copy()
    def update(m):
        z=value()
        m.set_value(0 if abs(z)<.005 else z).align_to(anchor,RIGHT)
    number.add_updater(update); number.update(0)
    return group


def right_marker(origin,direction1,direction2,color=BLUE,size=.16):
    u=direction1/np.linalg.norm(direction1); v=direction2/np.linalg.norm(direction2)
    return VMobject(color=color,stroke_width=2).set_points_as_corners([origin+size*u,origin+size*(u+v),origin+size*v])


class C015Centroid(Scene):
    def construct(self):
        theta=ValueTracker(45*DEGREES); xy=xy_map()
        def s(): return state(theta.get_value())
        title,params,caption=header('重心：把 P 的坐标缩为三分之一','三条中线相交于 G')
        def medians():
            q=s(); g=VGroup()
            for vname,midpoint in (('p',(0,0)),('f1',q['midpoint1']),('f2',q['midpoint2'])):
                g.add(Line(xy(q[vname]),xy(midpoint),color=BLUE,stroke_width=2.3,stroke_opacity=.8),Dot(xy(midpoint),radius=.035,color=BLUE))
            g.add(Dot(xy(q['g']),radius=.075,color=GREEN),eq('G',27,GREEN).move_to(xy(q['g'])+np.array([.25,.16,0])))
            return g
        lines=always_redraw(medians); tri=always_redraw(lambda:triangle(s(),xy))
        numbers=VGroup(readout('x_G',lambda:s()['g'][0],[-1.9,-3.45,0]),readout('y_G',lambda:s()['g'][1],[1.9,-3.45,0]))
        formula=eq(r'G\left(\frac{x_0}{3},\frac{y_0}{3}\right)',42,GREEN).move_to([0,-4.8,0])
        proof=eq(r'G=\frac{P+F_1+F_2}{3}=\frac P3',33).move_to([0,-6.25,0])
        self.add(title,params,caption,base(5,4,xy),tri,lines,numbers,formula,proof)
        self.wait(1.5)
        self.play(theta.animate.set_value(135*DEGREES),run_time=4)
        self.wait(.8)
        swap(self,(caption,cn('底边中点是 O，PG:GO=2:1',25).move_to(caption)))
        self.play(theta.animate.set_value(75*DEGREES),run_time=2.5)
        self.wait(1)
        locus=VGroup(ParametricFunction(lambda t:xy((5*np.cos(t)/3,4*np.sin(t)/3)),t_range=[0,TAU],color=GREEN,stroke_width=2.2))
        for x in (-5/3,5/3):
            locus.add(Circle(radius=.065,color=GREEN,stroke_width=2,fill_color=BG,fill_opacity=1).move_to(xy((x,0))))
        swap(self,(caption,cn('重心轨迹：原椭圆缩小为三分之一',24).move_to(caption)),(proof,eq(r'\frac{X^2}{25/9}+\frac{Y^2}{16/9}=1,\quad Y\ne0',30).move_to(proof)))
        self.play(FadeIn(locus),run_time=.3)
        self.play(theta.animate.set_value(125*DEGREES),run_time=3)
        self.wait(1.5)
        self.play(FadeOut(locus),run_time=.3)
        swap(self,(caption,cn('三条中线相交于 G',25).move_to(caption)),(proof,eq(r'G=\frac{P+F_1+F_2}{3}=\frac P3',33).move_to(proof)))
        self.play(theta.animate.set_value(45*DEGREES),run_time=3)
        self.wait(.8)


class C015Incentre(Scene):
    def construct(self):
        theta=ValueTracker(50*DEGREES); xy=xy_map()
        def s(): return state(theta.get_value())
        title,params,caption=header('内心：切线长定横坐标，面积定半径','内切圆同时与三条边相切')
        title.become(cn('内心：切线长与面积，确定坐标',29).move_to(title))
        tri=always_redraw(lambda:triangle(s(),xy))
        def incircle():
            q=s(); centre=xy(q['i']); g=VGroup(Circle(radius=.7*q['radius'],color=GREEN,stroke_width=3).move_to(centre))
            for name in ('t','u','v'):
                foot=xy(q[name])
                g.add(Line(centre,foot,color=BLUE,stroke_width=1.8),Dot(foot,radius=.045,color=BLUE))
            g.add(Dot(centre,radius=.065,color=GREEN),eq('I',27,GREEN).move_to(centre+np.array([.2,.18,0])),eq('T',25,BLUE).move_to(xy(q['t'])+np.array([.18,-.27,0])),eq('r',25,BLUE).move_to((centre+xy(q['t']))/2+LEFT*.2))
            return g
        circle=always_redraw(incircle)
        numbers=VGroup(readout('x_I',lambda:s()['i'][0],[-1.9,-3.4,0]),readout('r',lambda:s()['radius'],[1.9,-3.4,0],BLUE))
        formula=eq(r'I\left(ex_0,\frac{cy_0}{a+c}\right)',40,GREEN).move_to([0,-4.8,0])
        explanation=eq(r'x_I=x_T=\frac{PF_1-PF_2}{2}=ex_0',31).move_to([0,-6.1,0])
        foot=cn('内心与 P 位于底边同侧',22,MUTED).move_to([0,-7,0])
        self.add(title,params,caption,base(5,4,xy),tri,circle,numbers,formula,explanation,foot)
        self.wait(1.5)
        self.play(theta.animate.set_value(130*DEGREES),run_time=4)
        self.wait(.8)
        swap(self,(caption,cn('底边切点 T 与内心 I 同横坐标',25).move_to(caption)))
        self.play(theta.animate.set_value(65*DEGREES),run_time=3)
        self.wait(1.2)
        swap(self,(caption,cn('面积 S=sr，求出内切圆半径',25).move_to(caption)),(explanation,eq(r'r=\frac{S}{s}=\frac{c|y_0|}{a+c}=|y_I|',33).move_to(explanation)))
        self.play(theta.animate.set_value(115*DEGREES),run_time=2.5)
        self.wait(1.5)
        swap(self,(caption,cn('内切圆同时与三条边相切',25).move_to(caption)),(explanation,eq(r'x_I=x_T=\frac{PF_1-PF_2}{2}=ex_0',31).move_to(explanation)))
        self.play(theta.animate.set_value(50*DEGREES),run_time=3)
        self.wait(.8)


class C015Orthocentre(Scene):
    def construct(self):
        theta=ValueTracker(70*DEGREES); xy=xy_map(.65,(0,.6))
        def s(): return state(theta.get_value())
        title,params,caption=header('垂心：先锁定同一条竖线','两条高线的交点就是 H')
        tri=always_redraw(lambda:triangle(s(),xy))
        def altitudes():
            q=s(); x,y=q['p']; c=q['c']
            g=VGroup(DashedLine(xy((x,-4.8)),xy((x,4.8)),color=GREEN,stroke_width=2.2,dash_length=.13),DashedLine(*[xy(p) for p in clip_line(x-c,y,-c*(x-c))],color=BLUE,stroke_width=2.2,dash_length=.13))
            d=xy(q['altfoot']); f1=xy(q['f1']); f2=xy(q['f2']); p=xy(q['p']); d0=xy(q['verticalfoot'])
            side=p-f2
            parameter=np.dot(d-f2,side)/np.dot(side,side)
            if parameter<-1e-8:
                g.add(DashedLine(f2,d,color=INK,stroke_width=1.8,dash_length=.1))
            elif parameter>1+1e-8:
                g.add(DashedLine(p,d,color=INK,stroke_width=1.8,dash_length=.1))
            if np.linalg.norm(f1-d)>1e-8:
                g.add(Line(f1,d,color=BLUE,stroke_width=2.6),right_marker(d,p-f2,f1-d))
            if np.linalg.norm(d-d0)>.15:
                g.add(right_marker(d0,UP,LEFT,GREEN))
            if x>c+1e-8:
                g.add(DashedLine(f2,d0,color=INK,stroke_width=2,dash_length=.1))
            elif x<-c-1e-8:
                g.add(DashedLine(f1,d0,color=INK,stroke_width=2,dash_length=.1))
            far_from_foci=min(np.linalg.norm(xy(q['h'])-f1),np.linalg.norm(xy(q['h'])-f2))>.65
            offset=np.array([.28,-.35 if q['h'][1]<-.05 and far_from_foci else .22,0])
            g.add(Dot(xy(q['h']),color=GREEN,radius=.075),eq('H',27,GREEN).move_to(xy(q['h'])+offset))
            return g
        lines=always_redraw(altitudes)
        numbers=VGroup(readout('x_H',lambda:s()['h'][0],[-1.9,-3.45,0]),readout('y_H',lambda:s()['h'][1],[1.9,-3.45,0]))
        formula=eq(r'H\left(x_0,\frac{c^2-x_0^2}{y_0}\right)',39,GREEN).move_to([0,-4.85,0])
        proof=eq(r'x_H=x_0,\quad (x_0+c)(x_0-c)+y_0y_H=0',29).move_to([0,-6.3,0])
        self.add(title,params,caption,base(5,4,xy,focal_inset=-.2),tri,lines,numbers,formula,proof)
        self.wait(1.5)
        swap(self,(caption,cn('P 移动，高线始终是 x=x₀',25).move_to(caption)))
        self.play(theta.animate.set_value(math.acos(3/5)),run_time=2.5)
        swap(self,(caption,cn('焦点处为直角：H 与 F₂ 重合',25).move_to(caption)))
        self.wait(1.7)
        swap(self,(caption,cn('继续移动，垂心走到三角形外',25).move_to(caption)))
        self.play(theta.animate.set_value(math.acos(4/5)),run_time=2.3)
        self.wait(1.7)
        swap(self,(caption,cn('垂心可在外部，仍与 P 同横坐标',24).move_to(caption)))
        self.play(theta.animate.set_value(110*DEGREES),run_time=4)
        self.wait(1)
        swap(self,(caption,cn('两条高线的交点就是 H',25).move_to(caption)))
        self.play(theta.animate.set_value(70*DEGREES),run_time=2.5)
        self.wait(.8)


class C015Circumcentre(Scene):
    def construct(self):
        theta=ValueTracker(35*DEGREES); xy=xy_map(.58,(0,.35))
        def s(): return state(theta.get_value(),5,3)
        title,params,caption=header('外心：始终在 y 轴上', '底边中垂线就是 y 轴',3)
        tri=always_redraw(lambda:triangle(s(),xy))
        def circumcircle():
            q=s(); centre=xy(q['circum'])
            g=VGroup(Circle(radius=.58*q['circumradius'],color=GREEN,stroke_width=2.7).move_to(centre),Line(xy((0,-5.4)),xy((0,5.5)),color=BLUE,stroke_width=2.2,stroke_opacity=.65))
            for name in ('f1','f2','p'):
                g.add(Line(centre,xy(q[name]),color=BLUE,stroke_width=1.7,stroke_opacity=.8))
            g.add(Dot(centre,radius=.075,color=GREEN),eq("O'",27,GREEN).move_to(centre+np.array([.3,-.25,0])))
            if abs(q['circum'][1])<1e-9:
                p=xy(q['p'])
                g.add(right_marker(p,xy(q['f1'])-p,xy(q['f2'])-p,GREEN,size=.2))
            return g
        circle=always_redraw(circumcircle)
        number=readout(r"y_{O'}",lambda:s()['circum'][1],[0,-3.6,0],GREEN,35)
        equality=eq(r"O'P=O'F_1=O'F_2",33,BLUE).move_to([0,-4.6,0])
        formula=eq(r"O'\left(0,\frac{x_0^2+y_0^2-c^2}{2y_0}\right)",36,GREEN).move_to([0,-5.75,0])
        foot=cn('外心位置不要求三角形等腰',23,MUTED).move_to([0,-6.9,0])
        self.add(title,params,caption,base(5,3,xy,(-5.5,5.5,-5.4,5.5),focal_inset=.34),circle,tri,number,equality,formula,foot)
        self.wait(1.5)
        swap(self,(caption,cn('三个顶点到外心的距离始终相等',24).move_to(caption)))
        self.play(theta.animate.set_value(math.acos(math.sqrt(7)/4)),run_time=2.5)
        swap(self,(caption,cn('顶角为直角：外心恰为 O',25).move_to(caption)),(foot,eq(r"OP=c\quad\Longleftrightarrow\quad O'=O",29,MUTED).move_to(foot)))
        self.wait(1.7)
        swap(self,(caption,cn('继续移动，外心可以跨过底边',25).move_to(caption)),(foot,cn('外心不一定与 P 在底边同侧',23,MUTED).move_to(foot)))
        self.play(theta.animate.set_value(PI/2),run_time=2.5)
        swap(self,(caption,cn('顶角为钝角，外心在 x 轴下方',25).move_to(caption)))
        self.wait(2)
        swap(self,(caption,cn('外心沿 y 轴移动，三段半径仍相等',24).move_to(caption)))
        self.play(theta.animate.set_value(130*DEGREES),run_time=2.5)
        self.wait(.8)
        self.play(theta.animate.set_value(35*DEGREES),run_time=4)
        swap(self,(caption,cn('底边中垂线就是 y 轴',25).move_to(caption)),(foot,cn('外心位置不要求三角形等腰',23,MUTED).move_to(foot)))
        self.wait(.8)
