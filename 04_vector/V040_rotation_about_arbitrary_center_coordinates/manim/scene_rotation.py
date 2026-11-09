"""V040: fixed arbitrary center, signed rotation, then rotating components."""
from pathlib import Path
import json
import sys
import numpy as np
from manim import *

sys.path.insert(0,str(Path(__file__).resolve().parent))
from model import LESSON, MOTIONS

config.frame_width=9
config.frame_height=16
config.background_color='#F7F8FA'

INK='#213044'
MUTED='#526275'
AXIS='#A7B4C2'
BLUE='#2778BD'
GREEN='#158068'
ORANGE='#CD6031'
PURPLE='#8055B2'
FONT='Microsoft YaHei'


class V040ArbitraryCenterRotation(Scene):
    def construct(self):
        fixed_text=[]
        def text(s,size=27,color=INK):
            m=Text(s,font=FONT,font_size=size,color=color)
            return m
        def keep(m):
            fixed_text.append(m)
            self.add(m)
            return m
        title=keep(text('绕任意点旋转，坐标怎么变？',36).move_to([0,7.05,0]))
        subtitle=keep(text('B(1,1)，P(4,2)；中心 B 始终不动',25,MUTED).move_to([0,6.35,0]))
        # Branding is never part of any fading teaching group.
        footer1=keep(text('查结论 · 看图解 · 学证明｜知树 App',23,MUTED).move_to([0,-6.95,0]))
        footer2=keep(text('公众号 ok-shuxue｜获取入口',21,MUTED).move_to([0,-7.45,0]))
        self.add(Line([-3.8,-6.45,0],[3.8,-6.45,0],color=AXIS,stroke_width=1))

        axes=Axes(x_range=[-3,5,1],y_range=[-3,5,1],x_length=7,y_length=7,
                  axis_config={'color':AXIS,'stroke_width':1.4,'include_ticks':False,
                               'tip_width':0.11,'tip_height':0.13}).move_to([0,1.85,0])
        cp=lambda p:axes.c2p(*p)
        self.add(axes)
        keep(MathTex('x',font_size=25,color=MUTED).next_to(axes.x_axis.get_end(),RIGHT,buff=0.13))
        keep(MathTex('y',font_size=25,color=MUTED).next_to(axes.y_axis.get_end(),UP,buff=0.13))
        keep(MathTex('O',font_size=25,color=MUTED).move_to(cp((0,0))+np.array([-.22,-.25,0])))
        # Sparse equal-scale ticks are sufficient; circle and vectors carry the lesson.
        for direction,values in [('x',[-2,2,4]),('y',[-2,2,4])]:
            for n in values:
                p=cp((n,0) if direction=='x' else (0,n))
                self.add(Line(p+(.055*UP if direction=='x' else .055*LEFT),
                              p+(.055*DOWN if direction=='x' else .055*RIGHT),color=AXIS,stroke_width=1))
                keep(MathTex(str(n),font_size=20,color=MUTED).move_to(p+(.23*DOWN if direction=='x' else .23*LEFT)))
        b=cp(LESSON.center); p=cp(LESSON.point)
        theta=ValueTracker(0)
        phase=ValueTracker(0)
        self.add(Circle(radius=LESSON.radius*7/8,color=AXIS,stroke_width=1.4,
                        stroke_opacity=.55).move_to(b))
        original=Arrow(b,p,buff=0,color=BLUE,stroke_width=5,max_tip_length_to_length_ratio=.075)
        self.add(original,Dot(b,radius=.065,color=INK),Dot(p,radius=.055,color=BLUE))
        b_label=keep(text('B(1,1)',23).move_to(b+np.array([-.62,-.38,0])))
        p_label=keep(MathTex('P',font_size=28,color=BLUE).move_to([3.85,2.9,0]))
        self.add(Line(p+np.array([.12,.03,0]),p_label.get_left()+LEFT*.10,color=BLUE,stroke_width=1))
        qpt=lambda:cp(LESSON.image(theta.get_value()))
        moving=always_redraw(lambda:Arrow(b,qpt(),buff=0,color=GREEN,stroke_width=5,
                                          max_tip_length_to_length_ratio=.075))
        qdot=always_redraw(lambda:Dot(qpt(),radius=.075,color=GREEN))
        qlabel=text('Q',25,GREEN)
        def label_position(m):
            radial=qpt()-b
            m.move_to(qpt()+radial/np.linalg.norm(radial)*.38)
        qlabel.add_updater(label_position)
        self.add(moving,qdot,qlabel)
        # Angle is measured from BP, never from the x axis.
        initial=np.arctan2(1,3)
        def angle_arc():
            degrees=theta.get_value()
            if abs(degrees)<.3:
                return VMobject()
            arc=Arc(radius=.72,start_angle=initial,angle=degrees*DEGREES,
                    arc_center=b,color=ORANGE,stroke_width=2.5)
            arc.add_tip(tip_length=.12,tip_width=.10)
            return arc
        sweep=always_redraw(angle_arc)
        self.add(sweep)
        # Decomposition appears only for the explanation stage.
        three=MathTex('3',font_size=30,color=BLUE)
        one=MathTex('1',font_size=30,color=ORANGE)
        h_name=MathTex('H',font_size=25,color=INK)
        def component_path():
            if phase.get_value()<.5: return VGroup()
            h=cp(LESSON.corner(theta.get_value())); q=qpt()
            angle=theta.get_value()*DEGREES
            off_h=np.array([np.sin(angle),-np.cos(angle),0])*.28
            off_k=np.array([np.cos(angle),np.sin(angle),0])*.28
            return VGroup(Arrow(b,h,buff=0,color=BLUE,stroke_width=4),
                          Arrow(h,q,buff=0,color=ORANGE,stroke_width=4),
                          Dot(h,radius=.05,color=INK),
                          three.copy().move_to((b+h)/2+off_h),
                          one.copy().move_to((h+q)/2+off_k),
                          h_name.copy().move_to(h+np.array([.27,-.25,0])))
        components=always_redraw(component_path)
        self.add(components)
        stage=text('从 P 出发，绕 B 转动',30).move_to([0,-2.0,0])
        self.add(stage)
        angle_caption=MathTex(r'\theta=',font_size=32,color=ORANGE).move_to([-1.0,-2.7,0])
        angle_number=DecimalNumber(0,num_decimal_places=0,include_sign=True,font_size=32,color=ORANGE)
        angle_number.add_updater(lambda m:m.set_value(theta.get_value()).move_to([.1,-2.7,0]))
        degree=MathTex(r'^\circ',font_size=30,color=ORANGE).move_to([.9,-2.63,0])
        invariant=MathTex(r'BP=BQ=\sqrt{10}',font_size=29,color=MUTED).move_to([2,-2.7,0])
        # Angle occupies the left half; the invariant sits on its right.
        angle_caption.shift(LEFT*1.15); angle_number.add_updater(lambda m:m.shift(LEFT*1.15))
        degree.shift(LEFT*1.15)
        self.add(angle_caption,angle_number,degree,invariant)
        fixed_text.extend([angle_caption,degree,invariant])

        relative=keep(MathTex(r'(u,v)=P-B=(3,1)',font_size=35,color=BLUE).move_to([0,-3.4,0]))
        formula=VGroup(MathTex(r's=',r'3\cos\theta',r'-\sin\theta',font_size=40,color=INK),
                       MathTex(r't=',r'3\sin\theta',r'+\cos\theta',font_size=40,color=INK)).arrange(DOWN,buff=.18).move_to([0,-4.4,0])
        for row in formula:
            row[1].set_color(BLUE); row[2].set_color(ORANGE)
        self.add(formula)
        restore=keep(MathTex(r'Q=(1+s,\ 1+t)',font_size=36,color=GREEN).move_to([0,-5.4,0]))
        exact=text('先减中心 → 转相对坐标 → 加回中心',24,MUTED).move_to([0,-6.0,0])
        self.add(exact)
        fixed_text.extend(list(formula))

        events=[]
        def stamp(label):
            events.append({'time':round(self.time,4),'label':label,'angle':theta.get_value(),
                           'point':LESSON.image(theta.get_value()),
                           'screen_point':qpt().tolist()})
        def caption(message):
            stage.become(text(message,30).move_to([0,-2.0,0]))
        # Collect actual rendered-frame layout evidence. Rebuilding Mobjects does
        # not move formulas or branding, and every point is computed by the model.
        audit={'samples':0,'violations':[]}
        def inspect(_m,dt):
            audit['samples']+=1
            for i,m in enumerate(fixed_text+[stage,exact,qlabel,angle_number]):
                if m.width and (m.get_left()[0]<-4.25 or m.get_right()[0]>4.25 or
                                m.get_bottom()[1]<-7.8 or m.get_top()[1]>7.8):
                    if len(audit['violations'])<20: audit['violations'].append([self.time,i])
        sentinel=VMobject().add_updater(inspect)
        self.add(sentinel)
        self.wait(1.2); stamp('initial')
        for target,duration,hold,message in MOTIONS:
            caption(message)
            self.play(theta.animate.set_value(target),run_time=duration,rate_func=smooth)
            stamp(message); self.wait(hold)
        caption('拆成两段路，一起转 45°')
        phase.set_value(1)
        exact.become(text('蓝段转完，再接上橙段',25,MUTED).move_to([0,-6.0,0]))
        self.wait(.5)
        self.play(theta.animate.set_value(45),run_time=2.4,rate_func=smooth)
        stamp('component_45')
        exact.become(MathTex(r'Q=(1+\sqrt2,\ 1+2\sqrt2)',font_size=31,color=GREEN).move_to([0,-6.0,0]))
        self.wait(2.2)
        caption('回到起点，再看一次')
        exact.become(text('蓝段转完，再接上橙段',25,MUTED).move_to([0,-6.0,0]))
        self.play(theta.animate.set_value(0),run_time=1.5,rate_func=smooth)
        phase.set_value(0)
        caption('从 P 出发，绕 B 转动')
        exact.become(text('先减中心 → 转相对坐标 → 加回中心',24,MUTED).move_to([0,-6.0,0]))
        self.wait(.8); stamp('loop_end')
        dest=Path(config.media_dir).resolve().parent
        dest.mkdir(parents=True,exist_ok=True)
        (dest/'scene_audit.json').write_text(json.dumps({'events':events,'layout':audit},ensure_ascii=False,indent=2),encoding='utf-8')
        if audit['violations']: raise ValueError('text exceeds safe frame; see scene_audit.json')
