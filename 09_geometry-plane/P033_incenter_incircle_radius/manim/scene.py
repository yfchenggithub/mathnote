"""P033: three independent teaching loops, rendered by the frozen shared tools."""
from pathlib import Path
import json
import sys
import numpy as np
from manim import *

sys.path.insert(0,str(Path(__file__).resolve().parent))
from model import lesson_triangle, moving_triangle, equilateral, right_triangle

config.frame_width=9
config.frame_height=16
config.background_color='#F7F8FA'
INK='#202B3D'
MUTED='#526174'
BLUE='#356BB3'
GREEN='#27825E'
ORANGE='#A75C26'
PURPLE='#785B95'
LIGHT='#A4AEBB'
FONT='Microsoft YaHei'
FOOTER=('查结论 · 看图解 · 学证明｜知树 App','公众号 ok-shuxue｜获取入口')

def txt(value,size=26,color=INK):
    return Text(value,font=FONT,font_size=size,color=color)

def math(value,size=38,color=INK):
    return MathTex(value,font_size=size,color=color)

def fit(m,max_width=7.75):
    if m.width>max_width:m.scale_to_fit_width(max_width)
    return m

def mapper(scale=.44,shift=(-3.08,-.6)):
    return lambda p:np.array([p[0]*scale+shift[0],p[1]*scale+shift[1],0.])

def right_marker(I,H,U,project):
    h=project(H);v=project(I)-h;w=project(U)-h
    v=v/np.linalg.norm(v)*.14;w=w/np.linalg.norm(w)*.14
    return VMobject(color=MUTED,stroke_width=1.5).set_points_as_corners([h+v,h+v+w,h+w])

def label(letter,position,size=27,color=INK):
    return Text(letter,font='Times New Roman',font_size=size,color=color).move_to(position)

def shape(t,project,circle=True,radii=True,connect=False):
    result=VGroup()
    if connect:
        for V in (t.A,t.B,t.C):result.add(DashedLine(project(t.I),project(V),color=LIGHT,stroke_width=1.8,dash_length=.1))
    result.add(Polygon(*(project(p) for p in (t.A,t.B,t.C)),stroke_color=INK,stroke_width=2.6,fill_opacity=0))
    if circle:result.add(Circle(radius=t.r*np.linalg.norm(project((1,0))-project((0,0))),color=BLUE,stroke_width=2.5).move_to(project(t.I)))
    if radii:
        for H,U in zip(t.feet,(t.C,t.A,t.B)):
            result.add(Line(project(t.I),project(H),color=BLUE,stroke_width=3.5),right_marker(t.I,H,U,project))
    result.add(Dot(project(t.I),radius=.045,color=INK))
    return result

def point_labels(getter,project,feet=True,sides=False,radius=False):
    """Build glyphs once; updaters move labels without rebuilding SVGs per frame."""
    specifications=[('A',lambda t:t.A,UP*.34),('B',lambda t:t.B,DL*.30),
                    ('C',lambda t:t.C,DR*.30),('I',lambda t:t.I,RIGHT*.50+DOWN*.10)]
    if feet:
        specifications += [('D',lambda t:t.feet[0],DOWN*.34),('E',lambda t:t.feet[1],UR*.27),('F',lambda t:t.feet[2],UL*.27)]
    if sides:
        specifications += [('a',lambda t:tuple((t.B[k]+t.C[k])/2 for k in (0,1)),DOWN*.78),
                           ('b',lambda t:tuple(t.C[k]+.82*(t.A[k]-t.C[k]) for k in (0,1)),RIGHT*.34),
                           ('c',lambda t:tuple(t.A[k]+.3*(t.B[k]-t.A[k]) for k in (0,1)),LEFT*.34)]
    if radius:
        specifications += [('r',lambda t:tuple((t.I[k]+t.feet[0][k])/2 for k in (0,1)),RIGHT*.26)]
    result=VGroup()
    for name,point,offset in specifications:
        item=label(name,project(point(getter()))+offset)
        item.add_updater(lambda mob,dt,p=point,o=offset:mob.move_to(project(p(getter()))+o))
        result.add(item)
    return result

class Lesson:
    def setup_lesson(self,title,status):
        self.events=[]
        self.header=fit(txt(title,30)).move_to([0,6.95,0])
        self.status=fit(txt(status,25,MUTED)).move_to([0,5.95,0])
        self.footer=VGroup(
            Line([-3.9,-6.45,0],[3.9,-6.45,0],color='#CDD3DB',stroke_width=1),
            fit(txt(FOOTER[0],22,MUTED),7.8).move_to([0,-6.95,0]),
            fit(txt(FOOTER[1],20,MUTED),7.8).move_to([0,-7.47,0]))
        self.add(self.header,self.status,self.footer)
        self.panel=VGroup()

    def state(self,status,rows=(),extra=(),duration=.35):
        status=fit(txt(status,25,MUTED)).move_to(self.status)
        target=VGroup(*(fit((math(s,size,color) if kind=='m' else txt(s,size,color))).move_to([0,y,0])
                        for kind,s,y,size,color in rows))
        animations=[ReplacementTransform(self.status,status)]
        if len(self.panel):animations.append(FadeOut(self.panel))
        if len(target):animations.append(FadeIn(target))
        self.play(*animations,*extra,run_time=duration)
        self.status=status;self.panel=target

    def mark(self,name):
        self.events.append({'time':round(float(self.time),3),'name':name})

    def finish_evidence(self):
        # Rendering evidence stays inside the renderer's own isolated output.
        p=Path(config.media_dir)/f'{type(self).__name__}-story.json'
        p.parent.mkdir(parents=True,exist_ok=True)
        p.write_text(json.dumps({'scene':type(self).__name__,'duration':float(self.time),
                                'keyframes':self.events,'footer':FOOTER},ensure_ascii=False,indent=2),encoding='utf-8')

class P033IncenterArea(Lesson,Scene):
    def construct(self):
        self.setup_lesson('内心到三边，为何同样远？','先看垂直距离，不是连向顶点')
        t=lesson_triangle();project=mapper()
        initial=VGroup(shape(t,project,False,False),point_labels(lambda:t,project,False,True))
        initial_note=fit(txt('I 是三条内角平分线的交点',25,MUTED)).move_to([0,-3.2,0])
        self.add(initial,initial_note);self.wait(1.1);self.mark('opening')
        self.play(FadeOut(initial_note),run_time=.3)
        radii=VGroup();feet=VGroup()
        for i,(H,U,name) in enumerate(zip(t.feet,(t.C,t.A,t.B),('D','E','F'))):
            item=VGroup(Line(project(t.I),project(H),color=BLUE,stroke_width=3.5),right_marker(t.I,H,U,project))
            offset=(DOWN*.34,UR*.27,UL*.27)[i]
            point=label(name,project(H)+offset)
            self.play(Create(item),FadeIn(point),run_time=.65)
            radii.add(item);feet.add(point)
        circle=Circle(radius=t.r*.44,color=BLUE,stroke_width=2.5).move_to(project(t.I))
        self.play(Create(circle),run_time=.9)
        self.state('三个垂直距离，都是内切圆半径',[
            ('m',r'ID=IE=IF=r',-2.65,41,BLUE),('t','换一个三角形，等距关系仍然成立',-4.1,25,MUTED)])
        self.wait(1.5);self.mark('three_equal_radii')
        motion=ValueTracker(0)
        dynamic=always_redraw(lambda:shape(moving_triangle(motion.get_value()),project))
        moving_labels=point_labels(lambda:moving_triangle(motion.get_value()),project,True,True,True)
        self.remove(initial,circle,*radii,*feet)
        self.add(dynamic,moving_labels)
        self.play(motion.animate.set_value(1),run_time=4,rate_func=linear)
        self.wait(.8);self.mark('shape_changes_equal_distances')
        self.remove(dynamic,moving_labels)
        graph=VGroup(shape(t,project),point_labels(lambda:t,project,True,True,True))
        self.add(graph)
        self.state('连接内心与三顶点：三块的高都为 r',[
            ('m',r'\frac{ar}{2}\quad+\quad\frac{br}{2}\quad+\quad\frac{cr}{2}',-2.65,38,INK)])
        colors=(BLUE,ORANGE,GREEN)
        pieces=VGroup()
        for (U,V),color in zip(((t.B,t.C),(t.C,t.A),(t.A,t.B)),colors):
            polygon=Polygon(project(t.I),project(U),project(V),fill_color=color,fill_opacity=.17,stroke_opacity=0)
            self.add(polygon);self.bring_to_back(polygon)
            self.play(polygon.animate.set_fill(opacity=.30),Create(Line(project(t.I),project(U),color=LIGHT,stroke_width=1.8)),run_time=.75)
            pieces.add(polygon)
        self.wait(.8);self.mark('three_area_pieces')
        self.state('把三块面积相加，提出共同的 r/2',[
            ('m',r'S=\frac12r(a+b+c)',-2.5,41,INK),
            ('m',r'S=rp,\qquad r=\frac Sp',-3.95,42,BLUE),
            ('m',r'p=\frac{a+b+c}{2}',-5.35,31,MUTED)])
        self.wait(2.4);self.mark('area_formula')
        self.state('同高，所以面积比直接等于底边比',[
            ('m',r'S_{IBC}:S_{ICA}:S_{IAB}=a:b:c',-2.65,35,INK),
            ('t','只求比值，不必先求半径',-4.2,26,BLUE)])
        self.wait(2);self.mark('area_ratio')
        extras=[mob for mob in self.mobjects if mob not in (self.header,self.status,self.footer,self.panel)]
        initial_note.set_opacity(1)
        self.state('先看垂直距离，不是连向顶点',
            extra=tuple(FadeOut(m) for m in extras)+(FadeIn(initial),FadeIn(initial_note)),duration=.6)
        self.wait(.8);self.mark('loop_return')
        self.finish_evidence()

class P033TangentLengths(Lesson,Scene):
    def construct(self):
        self.setup_lesson('三边已知，切点分段不用猜','同一顶点引出的两条切线段等长')
        t=lesson_triangle();project=mapper()
        graph=VGroup(shape(t,project,True,False),point_labels(lambda:t,project,True))
        self.add(graph);self.wait(1);self.mark('opening')
        D,E,F=t.feet
        pairs=VGroup();symbols=VGroup()
        for V,Hs,name,color in ((t.A,(E,F),'x',BLUE),(t.B,(F,D),'y',GREEN),(t.C,(D,E),'z',PURPLE)):
            lines=VGroup();names=VGroup()
            for H in Hs:
                lines.add(Line(project(V),project(H),color=color,stroke_width=5))
                mid=(project(V)+project(H))/2
                edge=project(H)-project(V);normal=np.array([-edge[1],edge[0],0]);normal/=np.linalg.norm(normal)
                if np.dot(normal,mid-project(t.I))<0:normal=-normal
                names.add(label(name,mid+normal*.36,29,color))
            self.play(Create(lines),FadeIn(names),run_time=1)
            pairs.add(lines);symbols.add(names)
            self.state(f'从顶点 {"ABC"[len(pairs)-1]} 出发：两段一样长',[
                ('m',{'x':r'AE=AF=x','y':r'BF=BD=y','z':r'CD=CE=z'}[name],-2.8,41,color)])
            self.wait(.8)
        self.mark('three_pairs')
        self.state('沿着三条边，把相邻的两段相加',[
            ('m',r'y+z=a\quad(BC)',-2.25,37,INK),
            ('m',r'x+z=b\quad(CA)',-3.35,37,INK),
            ('m',r'x+y=c\quad(AB)',-4.45,37,INK)])
        self.wait(2.3);self.mark('sides_are_sums')
        self.state('三式相加：每段都数了两次',[
            ('m',r'2(x+y+z)=a+b+c',-2.6,37,INK),
            ('m',r'x+y+z=p',-3.85,41,BLUE),
            ('m',r'p=\frac{a+b+c}{2}',-5.2,31,MUTED)])
        self.wait(2.3);self.mark('semiperimeter')
        self.state('半周长，减去出发顶点的对边',[
            ('m',r'x=p-a',-2.3,41,BLUE),('m',r'y=p-b',-3.4,41,GREEN),
            ('m',r'z=p-c',-4.5,41,PURPLE),('t','不用先求面积或半径',-5.65,25,MUTED)])
        self.wait(2.3);self.mark('tangent_formulas')
        values=VGroup()
        for group,value,color in zip(symbols,(7,8,6),(BLUE,GREEN,PURPLE)):
            values.add(VGroup(*(label(str(value),m.get_center(),29,color) for m in group)))
        self.play(ReplacementTransform(symbols,values),run_time=.5)
        self.state('a=14，b=13，c=15；半周长 p=21',[
            ('m',r'x=21-14=7',-2.3,39,BLUE),('m',r'y=21-13=8',-3.4,39,GREEN),
            ('m',r'z=21-15=6',-4.5,39,PURPLE),('t','回验：7+8=15，8+6=14，7+6=13',-5.65,23,MUTED)])
        self.wait(2.7);self.mark('numeric_example')
        self.play(FadeOut(pairs),FadeOut(values),FadeOut(self.panel),run_time=.6)
        self.panel=VGroup();self.state('同一顶点引出的两条切线段等长')
        self.wait(.8);self.mark('loop_return');self.finish_evidence()

def special_graph(kind):
    if kind==0:t=equilateral(6);project=mapper(.9,(-2.7,-.65))
    elif kind==1:t=right_triangle(3,4);project=mapper(1.2,(-1.8,-.65))
    else:t=right_triangle(4,4);project=mapper(1.2,(-2.4,-.65))
    u=t.C[0];v=t.A[1]
    axes=VGroup(Line(project((-.45,0)),project((u+.65,0)),color=LIGHT,stroke_width=1.5),
                Line(project((0,-.4)),project((0,v+.65)),color=LIGHT,stroke_width=1.5),
                label('X',project((u+.88,0)),24,MUTED),label('Y',project((0,v+.88)),24,MUTED))
    geometry=VGroup(axes,shape(t,project,True,False))
    labels=point_labels(lambda:t,project,False)
    # Place the right-triangle incenter label away from the symmetry line.
    if kind:labels[3].clear_updaters().move_to(project(t.I)+UL*.30)
    labels[1].clear_updaters().become(label('B=O',project(t.B)+np.array([-.40,-.38,0]),25))
    geometry.add(labels)
    radius=VGroup(Line(project(t.I),project(t.feet[0]),color=BLUE,stroke_width=3.5))
    if kind:
        radius.add(Line(project(t.I),project((0,t.r)),color=BLUE,stroke_width=3.5))
        geometry.add(RightAngle(Line(project(t.B),project(t.C)),Line(project(t.B),project(t.A)),length=.23,color=MUTED,stroke_width=1.5))
        if kind==2:
            geometry.add(DashedLine(project(t.B),project((2,2)),color=PURPLE,stroke_width=1.8,dash_length=.11))
        geometry.add(label('r',project((t.r,0))+DOWN*.38,27,BLUE),label('r',project((0,t.r))+LEFT*.32,27,BLUE))
        geometry.add(label('u' if kind==1 else 't',project(t.C)+DOWN*.4,27),
                     label('v' if kind==1 else 't',project(t.A)+LEFT*.33,27))
        diagonal=math(r'w' if kind==1 else r'\sqrt2\,t',28,MUTED)
        diagonal.move_to(project(tuple(t.A[k]+.35*(t.C[k]-t.A[k]) for k in (0,1)))+RIGHT*.50)
        geometry.add(diagonal)
    else:
        geometry.add(DashedLine(project(t.A),project((3,0)),color=PURPLE,stroke_width=1.8,dash_length=.11),
                     label('ℓ/2',project((3,0))+DOWN*.4,26),label('ℓ',project(t.C)+DOWN*.4,26))
    return geometry,radius

class P033SpecialTriangles(Lesson,Scene):
    def construct(self):
        self.setup_lesson('特殊三角形：内心在哪里？','先约定位置，再写内心坐标')
        graph,radius=special_graph(0)
        self.add(graph);self.wait(.8)
        self.state('等边三角形：边长为 ℓ',[
            ('t','底边 B(0,0)、C(ℓ,0)，顶点 A 在上方',-1.8,23,MUTED),
            ('m',r'r=\frac{\sqrt3}{6}\ell=\frac h3',-2.95,40,BLUE),
            ('m',r'I=\left(\frac \ell2,\frac{\sqrt3 \ell}{6}\right)',-4.25,39,INK),
            ('t','h 为高；四心重合，切点是各边中点',-5.55,24,MUTED)])
        self.play(Create(radius),run_time=.9);self.wait(3.5);self.mark('equilateral')
        old_graph,old_radius=graph,radius
        graph,radius=special_graph(1)
        self.state('直角三角形：直角顶点 B 在原点',[
            ('t','两条直角边沿 X、Y 正半轴',-1.8,25,MUTED),
            ('m',r'r=\frac{u+v-w}{2}',-2.95,40,BLUE),
            ('m',r'I=(r,r)',-4.2,45,INK),
            ('t','u、v 是直角边，w 是斜边',-5.55,24,MUTED)],
            extra=(FadeOut(old_graph),FadeOut(old_radius),FadeIn(graph)),duration=.6)
        self.play(Create(radius),run_time=.9);self.wait(3.8);self.mark('right_triangle')
        old_graph,old_radius=graph,radius
        graph,radius=special_graph(2)
        self.state('等腰直角三角形：两直角边都是 t',[
            ('t','同样建系；对称轴为 Y=X',-1.8,25,MUTED),
            ('m',r'r=\frac{2-\sqrt2}{2}t',-2.95,40,BLUE),
            ('m',r'I=(r,r)',-4.2,45,INK),
            ('m',r'x=z=\frac{t}{\sqrt2},\quad y=r',-5.55,32,MUTED)],
            extra=(FadeOut(old_graph),FadeOut(old_radius),FadeIn(graph)),duration=.6)
        self.play(Create(radius),run_time=.9);self.wait(4);self.mark('isosceles_right')
        old_graph,old_radius=graph,radius
        graph,_=special_graph(0)
        self.state('先约定位置，再写内心坐标',
            extra=(FadeOut(old_graph),FadeOut(old_radius),FadeIn(graph)),duration=.6)
        self.wait(.8);self.mark('loop_return')
        self.finish_evidence()
