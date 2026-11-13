from manim import *
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from model import reflect, ORIGINAL, VERTICAL_ALPHA, THETA

config.background_color = '#F7F8FA'
config.frame_width = 9
config.frame_height = 16
INK='#213044'; BLUE='#2778BD'; ORANGE='#CD6031'; GREEN='#158068'; GRAY='#A7B4C2'

class P055MirrorSlope(Scene):
    def construct(self):
        def text(s,y,size=30,color=INK):
            t=Text(s,font='Microsoft YaHei',font_size=size,color=color).move_to([0,y,0])
            assert t.width < 8.1, (s,t.width)
            return t
        self.add(text('镜面转动，斜率怎样变？',6.8,34))
        # Branding stays on screen, including transitions and loop endpoints.
        self.add(text('查结论 · 看图解 · 学证明｜知树 App',-6.7,23),
                 text('公众号 ok-shuxue｜获取入口',-7.25,21))
        a=ValueTracker(0)
        center=np.array([0,1.0,0]); scale=1.05
        def pt(x,y): return center+scale*np.array([x,y,0])
        axes=VGroup(Arrow(pt(-3.3,0),pt(3.4,0),buff=0,color=GRAY,stroke_width=2),
                    Arrow(pt(0,-3.3),pt(0,3.4),buff=0,color=GRAY,stroke_width=2))
        self.add(axes,Text('x',color=INK,font_size=23).move_to(pt(3.5,-.25)),
                 Text('y',color=INK,font_size=23).move_to(pt(.25,3.5)))
        for n in [-2,-1,1,2]:
            self.add(Line(pt(n,-.06),pt(n,.06),color=GRAY,stroke_width=2),
                     Text(str(n),font_size=18,color=INK).move_to(pt(n,-.3)))
        def line_for(v,color,width=5):
            u=np.array([v[0],v[1]])/np.linalg.norm(v)
            return Line(pt(*(-3.1*u)),pt(*(3.1*u)),color=color,stroke_width=width)
        self.add(line_for(ORIGINAL,BLUE))
        mirror=always_redraw(lambda: DashedLine(pt(-3.25*np.cos(a.get_value()),-3.25*np.sin(a.get_value())),
                                               pt(3.25*np.cos(a.get_value()),3.25*np.sin(a.get_value())),
                                               color=GREEN,stroke_width=4,dash_length=.14))
        image_line=always_redraw(lambda: line_for(reflect(ORIGINAL,a.get_value()),ORANGE))
        dot=always_redraw(lambda: Dot(pt(*reflect(ORIGINAL,a.get_value())),radius=.075,color=ORANGE))
        original_dot=Dot(pt(*ORIGINAL),color=BLUE,radius=.075)
        self.add(mirror,image_line,dot,original_dot,Dot(center,radius=.055,color=INK))
        self.add(text('蓝：原线    橙：像线    虚线：镜面',-2.95,25))
        self.add(MathTex(r'k=\frac12,\quad \theta=\arctan\frac12',color=BLUE,font_size=36).move_to([0,-3.7,0]))
        status=text('水平镜面：上下反号',5.6,29)
        formula=MathTex(r"k'=-\frac12",color=ORANGE,font_size=44).move_to([0,-4.7,0])
        note=text('α：镜面方向角；横纵单位等长',-5.6,23)
        self.add(status,formula,note)
        self.wait(2)
        def turn(target,caption,result,duration=3):
            nonlocal status,formula
            moving=text('镜面转动，像线关于它保持对称',5.6,27)
            relation=MathTex(r"\theta'=2\alpha-\theta",color=ORANGE,font_size=42).move_to([0,-4.7,0])
            self.play(FadeOut(status),FadeOut(formula),run_time=.15)
            self.play(FadeIn(moving),FadeIn(relation),run_time=.15)
            self.play(a.animate.set_value(target),run_time=duration,rate_func=smooth)
            status=text(caption,5.6,29)
            formula=(text(result,-4.7,32,ORANGE) if isinstance(result,str) and not result.startswith('M:') else
                     MathTex(result[2:],color=ORANGE,font_size=44).move_to([0,-4.7,0]))
            self.play(FadeOut(moving),FadeOut(relation),run_time=.15)
            self.play(FadeIn(status),FadeIn(formula),run_time=.15)
            self.wait(2)
        turn(PI/4,'45° 镜面：横纵交换',r"M:k'=\frac{1}{k}=2")
        turn(VERTICAL_ALPHA,'临界状态：像线竖直','横增量为零，斜率不存在',2)
        turn(PI/2,'竖直镜面：左右反号',r"M:k'=-\frac12",2)
        turn(0,'水平镜面：上下反号',r"M:k'=-\frac12",3)
