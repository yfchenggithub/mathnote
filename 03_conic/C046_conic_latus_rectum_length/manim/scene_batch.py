from pathlib import Path
import sys
import numpy as np
from manim import *
sys.path.insert(0,str(Path(__file__).resolve().parent))
from model import *
config.background_color='#F7F8FA'
config.frame_width,config.frame_height=9,16
INK,MUTED,BLUE,ORANGE,GREEN,PURPLE,AXIS='#213044','#526275','#2778BD','#CD6031','#158068','#8055B2','#A7B4C2'
def cn(s,size=26,color=INK): return Text(s,font='Microsoft YaHei',font_size=size,color=color)
def eq(s,size=32,color=INK): return MathTex(s,font_size=size,color=color)
def swap(scene,*pairs):
    scene.play(*[FadeOut(a) for a,b in pairs],run_time=.15)
    for a,b in pairs: a.become(b)
    scene.play(*[FadeIn(a) for a,b in pairs],run_time=.15)
def number(symbol,value,pos,color=INK,places=2):
    d=DecimalNumber(-88.888,num_decimal_places=places,font_size=31,color=color)
    g=VGroup(eq(symbol+r"\approx",31,color),d).arrange(RIGHT,buff=.12).move_to(pos)
    anchor=d.get_right().copy()
    def update(m):
        v=value(); m.set_value(0 if abs(v)<.00001 else v).align_to(anchor,RIGHT)
    d.add_updater(update); d.update(0); return g
def axes(xy,xlim,ylim):
    return VGroup(Line(xy((xlim[0],0)),xy((xlim[1],0)),color=AXIS,stroke_width=1.3),Line(xy((0,ylim[0])),xy((0,ylim[1])),color=AXIS,stroke_width=1.3),eq('O',21,MUTED).move_to(xy((0,0))+LEFT*.2+DOWN*.23))


class C046Animation(Scene):
    def construct(self):
        xy=lambda p:np.array([1.05*p[0]-.3,1.05*p[1]+.4,0])
        title=cn('通径：过焦点、垂直于轴',31).move_to([0,6.9,0]);self.add(title)
        for kind,label,lo,hi in [('ellipse','椭圆',1.,2.),('hyperbola','双曲线',.8,1.5),('parabola','抛物线',1.,1.8)]:
            t=ValueTracker(lo)
            def geometry():
                q=t.get_value();a,b,c=params(kind,q);A,B=endpoints(kind,q)
                if kind=='ellipse':plot=ParametricFunction(lambda u:xy(curve(kind,q,u)),t_range=[0,TAU],color=BLUE)
                elif kind=='hyperbola':plot=VGroup(*[ParametricFunction(lambda u,s=s:xy(curve(kind,q,u,s)),t_range=[-1,1],color=BLUE) for s in (-1,1)])
                else:plot=ParametricFunction(lambda u:xy(curve(kind,q,u)),t_range=[-2.3,2.3],color=BLUE)
                return VGroup(plot,Line(xy(A),xy(B),color=ORANGE,stroke_width=4),Dot(xy(A),color=GREEN,radius=.07),Dot(xy(B),color=GREEN,radius=.07),
                    Dot(xy((c,0)),color=INK,radius=.055),eq('F',25,MUTED).move_to(xy((c,0))+LEFT*.3))
            geo=always_redraw(geometry)
            caption=cn(label+'：焦点处的垂直截弦',26).move_to([0,5.6,0])
            form=eq(r'L=2p' if kind=='parabola' else r'L=\frac{2b^2}{a}',40,GREEN).move_to([0,-4.9,0])
            read=number('L',lambda:2*endpoints(kind,t.get_value())[0][1],[0,-3.5,0],ORANGE)
            note=cn('橙色弦与对称轴垂直',25,MUTED).move_to([0,-6.3,0])
            self.add(geo,caption,form,read,note);self.wait(.6)
            self.play(t.animate.set_value(hi),run_time=2.5);self.wait(.7)
            self.play(t.animate.set_value(lo),run_time=2.5);self.wait(.4)
            self.play(*[FadeOut(m) for m in (geo,caption,form,read,note)],run_time=.2)
