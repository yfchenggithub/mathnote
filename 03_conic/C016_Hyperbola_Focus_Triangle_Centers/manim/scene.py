import math
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from manim import *
from model import state,clip_line

BG='#F7F8FA'; INK='#213044'; MUTED='#526275'; BLUE='#2778BD'
GREEN='#158068'; ORANGE='#CD6031'; AXIS='#A7B4C2'
config.background_color=BG
config.frame_width,config.frame_height=9,16


def cn(s,size=26,color=INK):return Text(s,font='Microsoft YaHei',font_size=size,color=color)
def eq(s,size=34,color=INK):return MathTex(s,font_size=size,color=color)
def mapping(scale=.58,centre=(0,.2)):
    return lambda p:np.array([scale*p[0]+centre[0],scale*p[1]+centre[1],0.])


def swap(scene,*pairs):
    scene.play(*[FadeOut(old) for old,new in pairs],run_time=.15)
    for old,new in pairs:old.become(new)
    scene.play(*[FadeIn(old) for old,new in pairs],run_time=.15)


def header(title,caption):
    return (cn(title,30).move_to([0,6.9,0]),eq(r'\frac{x^2}{9}-\frac{y^2}{16}=1\quad(y_0\ne0)',29).move_to([0,5.9,0]),cn(caption,25).move_to([0,4.85,0]))


def axes(xy,box):
    xmin,xmax,ymin,ymax=box
    return VGroup(Line(xy((xmin,0)),xy((xmax,0)),color=AXIS,stroke_width=1.4),Line(xy((0,ymin)),xy((0,ymax)),color=AXIS,stroke_width=1.4),eq('O',24).move_to(xy((0,0))+np.array([-.18,-.26,0])),eq('x',24).move_to(xy((xmax+.18,-.23))))


def base(xy,box=(-6.3,6.3,-4.6,6.4),focal_inset=-.2):
    g=axes(xy,box); bound=math.acosh(min(abs(box[0]),box[1])/3)
    lo=max(-bound,math.asinh(box[2]/4)); hi=min(bound,math.asinh(box[3]/4))
    for sign in (-1,1):
        g.add(ParametricFunction(lambda t,sign=sign:xy((sign*3*np.cosh(t),4*np.sinh(t))),t_range=[lo,hi],color=MUTED,stroke_width=2,stroke_opacity=.6))
    for x,name in ((-5,'F_1'),(5,'F_2')):
        g.add(Dot(xy((x,0)),radius=.05,color=INK),eq(name,25).move_to(xy((x,0))+np.array([focal_inset if x<0 else -focal_inset,-.3,0])))
    return g


def triangle(s,xy):
    return VGroup(Polygon(*[xy(s[k]) for k in ('f1','p','f2')],color=INK,stroke_width=3,fill_color=BLUE,fill_opacity=.035),Dot(xy(s['p']),color=ORANGE,radius=.065),eq('P',26,ORANGE).move_to(xy(s['p'])+np.array([s['branch']*.13,.28,0])))


def readout(symbol,value,pos,color=GREEN,size=32):
    label=eq(symbol+r'\approx',size,color)
    num=DecimalNumber(-8.88,num_decimal_places=2,font_size=size,color=color)
    g=VGroup(label,num).arrange(RIGHT,buff=.12).move_to(pos); anchor=num.get_right().copy()
    def update(m):
        z=value(); m.set_value(0 if abs(z)<.005 else z).align_to(anchor,RIGHT)
    num.add_updater(update);num.update(0)
    return g


def square(origin,u,v,color=BLUE,size=.16):
    u=u/np.linalg.norm(u);v=v/np.linalg.norm(v)
    return VMobject(color=color,stroke_width=2).set_points_as_corners([origin+size*u,origin+size*(u+v),origin+size*v])


class C016Centroid(Scene):
    def construct(self):
        u=ValueTracker(.65);branch=ValueTracker(1);xy=mapping()
        def s():return state(u.get_value(),int(branch.get_value()))
        title,params,caption=header('重心：左右两支，都取三点平均','右支：三条中线交于 G')
        ground=base(xy)
        def drawing():
            q=s();g=triangle(q,xy)
            for name,mid in (('p',(0,0)),('f1',q['mid1']),('f2',q['mid2'])):
                g.add(Line(xy(q[name]),xy(mid),color=BLUE,stroke_width=2.2),Dot(xy(mid),color=BLUE,radius=.035))
            g.add(Dot(xy(q['g']),color=GREEN,radius=.075),eq('G',27,GREEN).move_to(xy(q['g'])+np.array([.25,.18,0])))
            return g
        figure=always_redraw(drawing)
        numbers=VGroup(readout('x_G',lambda:s()['g'][0],[-1.9,-3.55,0]),readout('y_G',lambda:s()['g'][1],[1.9,-3.55,0]))
        formula=eq(r'G\left(\frac{x_0}{3},\frac{y_0}{3}\right)',41,GREEN).move_to([0,-4.85,0])
        proof=eq(r'G=\frac{P+F_1+F_2}{3}=\frac P3',33).move_to([0,-6.3,0])
        self.add(title,params,caption,ground,figure,numbers,formula,proof)
        self.wait(1.5)
        self.play(u.animate.set_value(1.15),run_time=3)
        self.wait(.7)
        swap(self,(caption,cn('两焦点坐标抵消，OG:OP=1:3',25).move_to(caption)))
        self.play(u.animate.set_value(.75),run_time=2)
        self.wait(.8)
        self.play(FadeOut(figure),FadeOut(numbers),run_time=.2)
        branch.set_value(-1);u.set_value(.65);figure.update(0);numbers.update(0)
        swap(self,(caption,cn('换到左支：同样取坐标的三分之一',24).move_to(caption)))
        self.play(FadeIn(figure),FadeIn(numbers),run_time=.2)
        self.play(u.animate.set_value(1.1),run_time=2.5)
        self.wait(1)
        self.play(u.animate.set_value(.75),run_time=2)
        self.wait(.7)
        self.play(FadeOut(figure),FadeOut(numbers),run_time=.2)
        branch.set_value(1);u.set_value(.65);figure.update(0);numbers.update(0)
        swap(self,(caption,cn('右支：三条中线交于 G',25).move_to(caption)))
        self.play(FadeIn(figure),FadeIn(numbers),run_time=.2)
        self.wait(.8)


class C016Incentre(Scene):
    def construct(self):
        u=ValueTracker(.65);branch=ValueTracker(1);xy=mapping(.58,(0,.35))
        def s():return state(u.get_value(),int(branch.get_value()))
        title,params,caption=header('内心：横坐标被距离差锁定','右支：底边切点 T 固定在 (a,0)')
        ground=base(xy)
        def geometry():
            q=s();centre=xy(q['i']);g=triangle(q,xy)
            g.add(Line(xy((3,-4.6)),xy((3,6.4)),color=GREEN,stroke_width=1.6,stroke_opacity=.65),Circle(radius=.58*q['radius'],color=GREEN,stroke_width=3).move_to(centre))
            for name in ('t','contact1','contact2'):
                g.add(Line(centre,xy(q[name]),color=BLUE,stroke_width=1.8),Dot(xy(q[name]),color=BLUE,radius=.045))
            g.add(Dot(centre,color=GREEN,radius=.07),eq('I',27,GREEN).move_to(centre+np.array([.23,.16,0])),eq('T',25,BLUE).move_to(xy(q['t'])+np.array([.18,-.28,0])))
            return g
        figure=always_redraw(geometry)
        numbers=VGroup(readout('x_I',lambda:s()['i'][0],[-1.9,-3.6,0]),readout('y_I',lambda:s()['i'][1],[1.9,-3.6,0]))
        formula=eq(r'I\left(a\operatorname{sgn}(x_0),\frac{ay_0}{a+|x_0|}\right)',35,GREEN).move_to([0,-4.95,0])
        foot=eq(r'x_I=x_T=\frac{PF_1-PF_2}{2}',32).move_to([0,-6.45,0])
        self.add(title,params,caption,ground,figure,numbers,formula,foot)
        self.wait(1.5)
        self.play(u.animate.set_value(1.15),run_time=2.5)
        self.wait(.7)
        self.play(u.animate.set_value(.75),run_time=1.8)
        self.wait(.5)
        self.play(FadeOut(ground),FadeOut(figure),run_time=.25)
        locxy=mapping(.7,(0,.35));locus=axes(locxy,(-4.5,4.5,-4.6,4.6))
        for x in (-3,3):
            for low,high in ((-4,0),(0,4)):
                locus.add(Line(locxy((x,low)),locxy((x,high)),color=GREEN,stroke_width=3.2))
            for y in (-4,0,4):
                locus.add(Circle(radius=.065,color=GREEN,stroke_width=2,fill_color=BG,fill_opacity=1).move_to(locxy((x,y))))
            locus.add(eq('x='+str(x),27,GREEN).move_to(locxy((x,4.5))))
        for y in (-4,4):locus.add(eq(str(y),25,MUTED).move_to(locxy((-.28,y))))
        point=always_redraw(lambda:VGroup(Dot(locxy(s()['i']),radius=.08,color=GREEN),eq('I',27,GREEN).move_to(locxy(s()['i'])+np.array([.25,.14,0]))))
        swap(self,(caption,cn('只看内心轨迹：端点全部取不到',25).move_to(caption)),(foot,eq(r'x_I=\pm a,\qquad0<|y_I|<b',33).move_to(foot)))
        self.play(FadeIn(locus),FadeIn(point),run_time=.3)
        self.play(u.animate.set_value(3.2),run_time=3)
        self.wait(1)
        for newbranch,newu,message in ((-1,1.5,'左支：内心在 x=-a 上'),(-1,-1.5,'P 在下方，内心纵坐标也为负'),(1,-1.5,'两支、上下半部：共四条开线段')):
            self.play(FadeOut(point),FadeOut(numbers),run_time=.15)
            branch.set_value(newbranch);u.set_value(newu);point.update(0);numbers.update(0)
            swap(self,(caption,cn(message,25).move_to(caption)))
            self.play(FadeIn(point),FadeIn(numbers),run_time=.15)
            self.wait(.8)
        self.wait(1)
        self.play(FadeOut(locus),FadeOut(point),FadeOut(numbers),run_time=.25)
        branch.set_value(1);u.set_value(.65);figure.update(0);numbers.update(0)
        swap(self,(caption,cn('右支：底边切点 T 固定在 (a,0)',25).move_to(caption)),(foot,eq(r'x_I=x_T=\frac{PF_1-PF_2}{2}',32).move_to(foot)))
        self.play(FadeIn(ground),FadeIn(figure),FadeIn(numbers),run_time=.25)
        self.wait(.8)


class C016Orthocentre(Scene):
    def construct(self):
        u=ValueTracker(.95);xy=mapping(.55,(0,.1));box=(-6.4,6.4,-4.6,6.6)
        def s():return state(u.get_value())
        title,params,caption=header('垂心：与 P 同横坐标，位置会改变','竖直高线与另一条高线交于 H')
        def geometry():
            q=s();x,y=q['p'];g=triangle(q,xy);p=xy(q['p']);f1=xy(q['f1']);f2=xy(q['f2']);h=xy(q['h']);d=xy(q['altfoot']);d0=xy(q['verticalfoot'])
            g.add(DashedLine(xy((x,box[2])),xy((x,box[3])),color=GREEN,stroke_width=2.2,dash_length=.13),DashedLine(*[xy(z) for z in clip_line(x-5,y,-5*(x-5),box)],color=BLUE,stroke_width=2.2,dash_length=.13),Line(f1,d,color=BLUE,stroke_width=2.5))
            side=p-f2;ratio=np.dot(d-f2,side)/np.dot(side,side)
            if ratio<-1e-8:g.add(DashedLine(f2,d,color=INK,stroke_width=1.8,dash_length=.1))
            elif ratio>1+1e-8:g.add(DashedLine(p,d,color=INK,stroke_width=1.8,dash_length=.1))
            g.add(square(d,side,f1-d))
            if np.linalg.norm(d-d0)>.15:g.add(square(d0,UP,LEFT,GREEN))
            if x>5+1e-8:g.add(DashedLine(f2,d0,color=INK,stroke_width=1.8,dash_length=.1))
            if np.linalg.norm(h-p)<.4:offset=np.array([.3,-.22,0])
            else:offset=np.array([.28,.4 if q['h'][1]>y else(.25 if q['h'][1]>=0 else -.3),0])
            g.add(Dot(h,color=GREEN,radius=.075),eq('H',27,GREEN).move_to(h+offset))
            return g
        drawing=always_redraw(geometry)
        numbers=VGroup(readout('x_H',lambda:s()['h'][0],[-1.9,-3.55,0]),readout('y_H',lambda:s()['h'][1],[1.9,-3.55,0]))
        formula=eq(r'H\left(x_0,\frac{c^2-x_0^2}{y_0}\right)',39,GREEN).move_to([0,-4.9,0])
        proof=eq(r'x_H=x_0,\quad(x_0-c)(x_H+c)+y_0y_H=0',29).move_to([0,-6.35,0])
        ground=base(xy,box)
        ground[-1].move_to(xy((5,0))+np.array([-.32,.24,0]))
        self.add(title,params,caption,ground,drawing,numbers,formula,proof)
        self.wait(1.5)
        self.play(u.animate.set_value(math.log(3)),run_time=2.5)
        swap(self,(caption,cn('x₀=c：三角形在 F₂ 处为直角',25).move_to(caption)))
        self.wait(1.5)
        swap(self,(caption,cn('越过这个位置，垂心走到下方',25).move_to(caption)))
        self.play(u.animate.set_value(1.22),run_time=2)
        self.wait(1)
        swap(self,(caption,cn('靠近顶点，垂心还可走到 P 上方',24).move_to(caption)))
        self.play(u.animate.set_value(.6),run_time=3.5)
        self.wait(1.5)
        swap(self,(caption,cn('始终与 P 同横坐标；顶点不取',25).move_to(caption)))
        self.play(u.animate.set_value(.95),run_time=2.5)
        swap(self,(caption,cn('竖直高线与另一条高线交于 H',25).move_to(caption)))
        self.wait(.8)


class C016Circumcentre(Scene):
    def construct(self):
        u=ValueTracker(.6);xy=mapping(.51,(0,.15))
        def s():return state(u.get_value())
        title,params,caption=header('外心：沿 y 轴移动，三顶点等距','外心在底边中垂线上')
        def geometry():
            q=s();centre=xy(q['circum']);g=VGroup(Circle(radius=.51*q['circumradius'],color=GREEN,stroke_width=2.7).move_to(centre),Line(xy((0,-6.5)),xy((0,7.6)),color=BLUE,stroke_width=2.1,stroke_opacity=.7))
            for name in ('f1','f2','p'):g.add(Line(centre,xy(q[name]),color=BLUE,stroke_width=1.7))
            g.add(triangle(q,xy),Dot(centre,color=GREEN,radius=.075),eq("O'",27,GREEN).move_to(centre+np.array([.3,-.25,0])))
            if abs(q['circum'][1])<1e-9:
                p=xy(q['p']);g.add(square(p,xy(q['f1'])-p,xy(q['f2'])-p,GREEN,.2))
            return g
        drawing=always_redraw(geometry)
        number=readout(r"y_{O'}",lambda:s()['circum'][1],[0,-3.75,0],GREEN,35)
        equality=eq(r"O'P=O'F_1=O'F_2",33,BLUE).move_to([0,-4.75,0])
        formula=eq(r"O'\left(0,\frac{x_0^2+y_0^2-c^2}{2y_0}\right)",36,GREEN).move_to([0,-5.85,0])
        foot=cn('外心不一定与 P 位于底边同侧',23,MUTED).move_to([0,-7,0])
        self.add(title,params,caption,base(xy,(-6.5,6.5,-6.4,7.5),focal_inset=.35),drawing,number,equality,formula,foot)
        self.wait(1.5)
        swap(self,(caption,cn('顶角为钝角：P 在上方，外心在下方',23).move_to(caption)))
        self.wait(1.2)
        self.play(u.animate.set_value(math.asinh(.8)),run_time=2.5)
        swap(self,(caption,cn('OP=c：顶角为直角，外心就是 O',25).move_to(caption)),(foot,eq(r"OP=c\quad\Longleftrightarrow\quad O'=O",29,MUTED).move_to(foot)))
        self.wait(1.7)
        swap(self,(caption,cn('继续移动，外心越过 x 轴',25).move_to(caption)),(foot,cn('三条半径始终相等',24,MUTED).move_to(foot)))
        self.play(u.animate.set_value(1),run_time=3)
        self.wait(1.5)
        swap(self,(caption,cn('外心始终在 y 轴上，不随 P 左右移',24).move_to(caption)))
        self.play(u.animate.set_value(.6),run_time=3.5)
        swap(self,(caption,cn('外心在底边中垂线上',25).move_to(caption)),(foot,cn('外心不一定与 P 位于底边同侧',23,MUTED).move_to(foot)))
        self.wait(.8)
