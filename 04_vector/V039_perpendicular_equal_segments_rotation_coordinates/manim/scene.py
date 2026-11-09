"""V039: rigid quarter turns about an explicitly non-origin center."""
from pathlib import Path
import json
import sys
import numpy as np
from manim import *

sys.path.insert(0,str(Path(__file__).resolve().parent))
from model import CENTER, SOURCE, rotate, triangle, audit_state, quarter_turn

BG='#F7F8FA'
INK='#213044'
MUTED='#526275'
BLUE='#2778BD'
GREEN='#158068'
ORANGE='#CD6031'
AXIS='#A7B4C2'
FONT='Microsoft YaHei'

config.frame_width=8
config.frame_height=128/9
config.background_color=BG

def txt(value,size=25,color=INK):
    return Text(value,font=FONT,font_size=size,color=color)

def math(value,size=32,color=INK):
    return MathTex(value,font_size=size,color=color)

class V039QuarterTurn(Scene):
    def construct(self):
        self.camera.background_color=BG
        footer=VGroup(
            txt('查结论 · 看图解 · 学证明｜知树 App',19,MUTED).move_to([0,-6.12,0]),
            txt('公众号 ok-shuxue｜获取入口',18,MUTED).move_to([0,-6.57,0]),
        )
        title=txt('垂直又等长，坐标怎么变？',31).move_to([0,6.30,0])
        phase=txt('先减中心，读出两个变化量',27,BLUE).move_to([0,5.50,0])
        note=txt('中心 B(2,-1) 始终不动',23,MUTED).move_to([0,4.91,0])
        axes=Axes(x_range=[-4,8,2],y_range=[-6,6,2],x_length=7,y_length=7,
                  tips=True,axis_config={'color':AXIS,'stroke_width':1.3,'include_ticks':False,
                                         'tip_width':.10,'tip_height':.12}).move_to([0,.8,0])
        # Axes center at the midpoint of the displayed numeric rectangle.
        cp=lambda p: axes.c2p(*p)
        b,p=cp(CENTER),cp(SOURCE)
        static_bp=Line(b,p,color=BLUE,stroke_width=4.2)
        bdot=Dot(b,radius=.065,color=INK)
        pdot=Dot(p,radius=.065,color=BLUE)
        blabel=math('B',29).next_to(b,DL,buff=.14)
        plabel=math('P(5,3)',29,BLUE).next_to(p,UR,buff=.12)
        origin=math('O',21,MUTED).next_to(cp((0,0)),DL,buff=.10)
        axis_names=VGroup(math('x',22,MUTED).next_to(axes.x_axis.get_end(),RIGHT,buff=.08),
                          math('y',22,MUTED).next_to(axes.y_axis.get_end(),UP,buff=.07))
        start_triangle=self.make_triangle(cp,0,BLUE)
        initial_legs=VGroup(math('+3',29,BLUE).move_to(cp((3.5,-1))+DOWN*.25),
                            math('+4',29,BLUE).move_to(cp((5,1))+RIGHT*.31))
        formula=math(r'P-B=(5-2,\ 3+1)=(3,4)',36).move_to([0,-3.50,0])
        explanation=txt('相对中心的横、纵变化量：3 和 4',23,MUTED).move_to([0,-4.30,0])
        condition=math(r'BP=5',29,BLUE).move_to([0,-5.05,0])
        self.add(footer,title,phase,note,axes,axis_names,origin,static_bp,bdot,pdot,
                 blabel,plabel,start_triangle,initial_legs,formula,explanation,condition)
        self.wait(1.8)

        records=[]
        theta=ValueTracker(0)
        def audit(_mob,dt):
            state=audit_state(theta.get_value())
            if abs(state['length_squared']-25)>1e-9 or abs(state['triangle_dot'])>1e-9:
                raise ValueError('V039 rigid-motion model failed during rendering')
            records.append(state)
        audit_mob=VMobject().add_updater(audit)
        self.add(audit_mob)

        endpoint_objects=[]
        for direction,color,name,target_y in [(1,GREEN,'逆时针',None),(-1,ORANGE,'顺时针',None)]:
            theta.set_value(0)
            self.remove(start_triangle,initial_legs)
            new_phase=txt(name+'旋转 90°',29,color).move_to(phase)
            new_note=txt('转动中等长；到 90° 时才垂直',23,MUTED).move_to(note)
            new_formula=math(r'BR=BP=5',34,color).move_to(formula)
            new_explanation=txt('观察整个小三角形怎样转过去',23,MUTED).move_to(explanation)
            self.play(Transform(phase,new_phase),Transform(note,new_note),
                      Transform(formula,new_formula),Transform(explanation,new_explanation),
                      FadeOut(condition),run_time=.35)
            rotating=always_redraw(lambda: self.make_triangle(cp,theta.get_value(),color))
            moving=always_redraw(lambda: Dot(cp(rotate(CENTER,SOURCE,theta.get_value())),
                                             radius=.072,color=color))
            moving_label=always_redraw(lambda: math('R',24,color).next_to(moving,RIGHT,buff=.12))
            initial_angle=np.arctan2(4,3)
            arc=always_redraw(lambda: Arc(radius=.65,start_angle=initial_angle,
                                angle=theta.get_value() or 1e-5,color=color,stroke_width=2,
                                arc_center=b))
            angle_label=txt('转角',22,MUTED).move_to([-1,-4.98,0])
            angle_value=DecimalNumber(0,num_decimal_places=0,font_size=29,color=color).move_to([.0,-4.98,0])
            angle_value.add_updater(lambda m: m.set_value(abs(theta.get_value())*180/PI))
            deg=math(r'^\circ',25,color).move_to([.50,-4.93,0])
            self.add(rotating,moving,moving_label,arc,angle_label,angle_value,deg)
            self.play(theta.animate.set_value(direction*PI/2),run_time=2.6,rate_func=smooth)
            moving_label.clear_updaters()
            self.remove(moving_label)
            q=quarter_turn(CENTER,SOURCE,direction)
            sub='1' if direction==1 else '2'
            qlabel=math(r'Q_'+sub+f'({int(q[0])},{int(q[1])})',29,color)
            qlabel.next_to(cp(q),UP if direction==1 else DOWN,buff=.15)
            marker=self.right_angle(cp,direction,color)
            if direction==1:
                legs=VGroup(math('+3',29,color).move_to(cp((2,.5))+RIGHT*.32),
                             math('-4',29,color).move_to(cp((.8,2))+UP*.29))
                rel=r'(3,4)\longmapsto(-4,3)'
                absolute=r'Q_1=(2-4,-1+3)=(-2,2)'
            else:
                legs=VGroup(math('-3',29,color).move_to(cp((2,-2.5))+LEFT*.32),
                             math('+4',29,color).move_to(cp((4,-4))+DOWN*.27))
                rel=r'(3,4)\longmapsto(4,-3)'
                absolute=r'Q_2=(2+4,-1-3)=(6,-4)'
            endpoint_note=txt('到达直角：垂直，而且等长',23,color).move_to(note)
            self.play(Transform(note,endpoint_note),Transform(formula,math(rel,40,color).move_to(formula)),
                      Transform(explanation,math(absolute,34).move_to(explanation)),
                      FadeIn(qlabel),FadeIn(marker),FadeIn(legs),run_time=.35)
            self.wait(2.2)
            angle_value.clear_updaters()
            for item in [rotating,moving,arc]: item.clear_updaters()
            group=VGroup(rotating,moving,arc,angle_label,angle_value,deg,qlabel,marker,legs)
            endpoint_objects.append((q,color))
            self.play(FadeOut(group),run_time=.35)

        final_objects=VGroup()
        for i,(q,color) in enumerate(endpoint_objects,1):
            qdot=Dot(cp(q),radius=.07,color=color)
            ray=Line(b,cp(q),stroke_width=3.6,color=color)
            lab=math(f'Q_{i}({int(q[0])},{int(q[1])})',29,color).next_to(qdot,UP if i==1 else DOWN,buff=.15)
            final_objects.add(ray,qdot,lab)
        self.play(FadeIn(final_objects),Transform(phase,txt('同一中心，保留两种位置',28).move_to(phase)),
                  Transform(note,math(r'BP\perp BQ,\quad BP=BQ>0',27).move_to(note)),
                  Transform(formula,math(r'Q=(a-v,\ b+u)',39,GREEN).move_to(formula)),
                  Transform(explanation,math(r'Q=(a+v,\ b-u)',39,ORANGE).move_to(explanation)),run_time=.45)
        self.remove(angle_label,angle_value,deg)
        final_hint=txt('先减中心 → 交换并变号 → 加回中心',23).move_to([0,-5.05,0])
        directions=VGroup(txt('逆时针',21,GREEN).move_to([-2.90,-3.5,0]),
                          txt('顺时针',21,ORANGE).move_to([-2.90,-4.3,0]))
        definitions=math(r'B(a,b),\quad P-B=(u,v)',27).move_to([0,-2.86,0])
        self.add(final_hint,directions,definitions)
        self.wait(2.8)
        self.play(FadeOut(final_objects),FadeOut(final_hint),FadeOut(directions),FadeOut(definitions),
                  Transform(phase,txt('先减中心，读出两个变化量',27,BLUE).move_to(phase)),
                  Transform(note,txt('中心 B(2,-1) 始终不动',23,MUTED).move_to(note)),
                  Transform(formula,math(r'P-B=(5-2,\ 3+1)=(3,4)',36).move_to(formula)),
                  Transform(explanation,txt('相对中心的横、纵变化量：3 和 4',23,MUTED).move_to(explanation)),
                  FadeIn(start_triangle),FadeIn(initial_legs),FadeIn(condition),run_time=.5)
        self.wait(.5)
        audit_mob.clear_updaters()
        destination=Path(config.media_dir)/'v039_motion_audit.json'
        destination.write_text(json.dumps({'samples':len(records),'states':records},indent=2),encoding='utf-8')

    def make_triangle(self,cp,angle,color):
        b,h,r=(cp(point) for point in triangle(angle=angle))
        shape=Polygon(b,h,r,stroke_width=0,fill_color=color,fill_opacity=.10)
        legs=VGroup(DashedLine(b,h,color=color,stroke_width=2.1,dash_length=.075),
                    DashedLine(h,r,color=color,stroke_width=2.1,dash_length=.075))
        hypotenuse=Line(b,r,color=color,stroke_width=4)
        # The right angle at H travels with the rigid triangle.
        e1=(b-h)/np.linalg.norm(b-h)*.15
        e2=(r-h)/np.linalg.norm(r-h)*.15
        mark=VMobject(color=color,stroke_width=1.4).set_points_as_corners([h+e1,h+e1+e2,h+e2])
        return VGroup(shape,legs,hypotenuse,mark)

    def right_angle(self,cp,direction,color):
        b=cp(CENTER)
        u=np.array([3,4,0])/5*.29
        v=np.array([-4,3,0])/5*.29*direction
        return VMobject(color=color,stroke_width=2).set_points_as_corners([b+u,b+u+v,b+v])
