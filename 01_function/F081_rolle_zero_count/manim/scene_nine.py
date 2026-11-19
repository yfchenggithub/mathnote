from manim import *
from pathlib import Path
import json,sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import model_nine as math_model

config.frame_width=9
config.frame_height=16
BG='#F7F8FA';INK='#213044';MUTED='#526275';LEFT_BLUE='#2778BD';RIGHT_GREEN='#158068';ORANGE='#CD6031';PURPLE='#8055B2';AXIS='#A7B4C2'
BUILD=Path(__file__).resolve().parents[3]/'build/manim/F081-nine-paths-20261119'

def cn(text,y,size=28,color=INK):
    m=Text(text,font='Microsoft YaHei',font_size=size,color=color)
    if m.width>7.95:m.scale_to_fit_width(7.95)
    return m.move_to([0,y,0])
def eq(text,y,size=36,color=INK):
    m=MathTex(text,font_size=size,color=color)
    if m.width>7.85:m.scale_to_fit_width(7.85)
    return m.move_to([0,y,0])
def axes(w,h,center,tips=True):
    return Axes(x_range=[-1.35,1.35,1],y_range=[-1.5,1.5,1],x_length=w,y_length=h,tips=tips,axis_config={'color':AXIS,'stroke_width':1.5,'include_ticks':False,'tip_width':.08,'tip_height':.11}).move_to(center)
def graph(ax,a,b,width=3.4):
    return VGroup(ax.plot(lambda x:a*x*x*x,x_range=[-1.06,0,.006],color=LEFT_BLUE,stroke_width=width,use_smoothing=False),ax.plot(lambda x:b*x*x*x,x_range=[0,1.06,.006],color=RIGHT_GREEN,stroke_width=width,use_smoothing=False))
def horizontal(ax,half=.26,width=4):
    return VGroup(Line(ax.c2p(-half,0),ax.c2p(half,0),color=ORANGE,stroke_width=width),Dot(ax.c2p(0,0),radius=.065 if width>3 else .035,color=ORANGE))
def mark(scene,records,name,**values):
    visible=[m for m in scene.mobjects if m.width>.001 and m.height>.001]
    bounds=[float(min(m.get_left()[0] for m in visible)),float(max(m.get_right()[0] for m in visible)),float(min(m.get_bottom()[1] for m in visible)),float(max(m.get_top()[1] for m in visible))]
    assert bounds[0]>-4.42 and bounds[1]<4.42 and bounds[2]>-7.85 and bounds[3]<7.85,(name,bounds)
    records.append({'name':name,'time':float(scene.time),'values':values,'bounds':bounds})

class F081NineStationaryDirections(Scene):
    def construct(self):
        self.camera.background_color=BG;records=[]
        title=cn('导数为零的九种走向',7.15,33)
        subtitle=cn('水平切线不等于曲线掉头',6.43,29)
        formula=eq(r'f(x)=\begin{cases}ax^3,&x\leq0,\\bx^3,&x>0\end{cases}',5.32,35)
        domain=eq(r'a,b\in\{-1,0,1\}',4.30,29,MUTED)
        self.add(title,subtitle,formula,domain,cn('查结论 · 看图解 · 学证明｜知树 App',-6.85,22,MUTED),cn('公众号 ok-shuxue｜获取入口',-7.42,20,MUTED))
        ax=axes(7.1,5.2,[0,.8,0])
        axis_names=VGroup(MathTex('x',font_size=25,color=MUTED).next_to(ax.x_axis.get_end(),RIGHT,buff=.1),MathTex('y',font_size=25,color=MUTED).next_to(ax.y_axis.get_end(),UP,buff=.09),MathTex('O',font_size=25,color=MUTED).next_to(ax.c2p(0,0),DL,buff=.13))
        invariant=eq(r'f\,^{\prime}(0)=0',-4.1,42,ORANGE)
        origin_tangent=horizontal(ax)
        legend=cn('蓝：左侧 x ≤ 0　绿：右侧 x > 0',-5.85,23,MUTED)
        self.add(ax,axis_names,origin_tangent,invariant,legend)
        curve=scan=coefficients=direction=insight=None
        for index,(a,b) in enumerate(math_model.CASES,1):
            if curve is not None:
                self.play(*[FadeOut(m) for m in [curve,scan,coefficients,direction,insight]],run_time=.2)
                self.remove(curve,scan,coefficients,direction,insight)
            x=ValueTracker(-.95)
            curve=graph(ax,a,b)
            def trace(a=a,b=b,x=x):
                z=x.get_value();p,q=math_model.tangent_endpoints(z,a,b)
                color=ORANGE if abs(z)<1e-8 else PURPLE
                return VGroup(Line(ax.c2p(*p),ax.c2p(*q),color=color,stroke_width=3.7),Dot(ax.c2p(z,math_model.f(z,a,b)),radius=.065,color=color))
            scan=always_redraw(trace)
            coefficients=VGroup(MathTex('a='+str(a),font_size=36,color=LEFT_BLUE),MathTex('b='+str(b),font_size=36,color=RIGHT_GREEN)).arrange(RIGHT,buff=.75).move_to([0,-2.35,0])
            direction=cn(f'{index}/9　左{math_model.trend(a)} → 右{math_model.trend(b)}',-3.13,30)
            insight=cn(math_model.note(a,b),-5.15,26)
            if index==1:
                self.add(curve,scan,coefficients,direction,insight)
                self.wait(.65);mark(self,records,'opening',a=a,b=b)
            else:
                self.play(*[FadeIn(m) for m in [curve,scan,coefficients,direction,insight]],run_time=.25)
            self.play(x.animate.set_value(0),run_time=.75,rate_func=linear)
            self.wait(.8 if a*b<0 else .6 if a==b==0 else .5)
            mark(self,records,f'case_{index}_origin',case=index,a=a,b=b,left=math_model.trend(a),right=math_model.trend(b),x=0,y=0,slope=0)
            self.play(x.animate.set_value(.95),run_time=.75,rate_func=linear)
            self.wait(.3)
            mark(self,records,f'case_{index}_exit',case=index,a=a,b=b,x=.95,y=math_model.f(.95,a,b),slope=math_model.df(.95,a,b))
        self.play(*[FadeOut(m) for m in [scan,coefficients,direction,insight,legend]],invariant.animate.move_to([0,-5,0]),run_time=.3)
        self.remove(scan,coefficients,direction,insight,legend)
        why=cn('为什么九种情况都有水平切线？',-2.3,29)
        limit=eq(r'\frac{f(h)-f(0)}{h}=\begin{cases}ah^2,&h<0,\\bh^2,&h>0\end{cases}\xrightarrow{h\to0}0',-3.55,29)
        self.play(FadeIn(why),FadeIn(limit),run_time=.3);self.wait(2.6)
        mark(self,records,'difference_quotient',all_cases=True)
        self.play(*[FadeOut(m) for m in [curve,ax,axis_names,origin_tangent,domain,why,limit]],invariant.animate.move_to([0,-4.3,0]),run_time=.35)
        self.remove(curve,ax,axis_names,origin_tangent,domain,why,limit)
        atlas=VGroup()
        for i,(a,b) in enumerate(math_model.CASES):
            col=i%3;row=i//3;cx=[-2.65,0,2.65][col];cy=[2.65,0,-2.65][row]
            small=axes(2.12,1.65,[cx,cy,0],tips=False)
            label=MathTex(str(i+1)+r'\quad('+str(a)+','+str(b)+')',font_size=30,color=INK).move_to([cx,cy+1.25,0])
            atlas.add(VGroup(small,graph(small,a,b,2.5),horizontal(small,.22,2.7),label))
        summary=cn('同为水平切线，左右走向却不同',-5.22,28)
        caption=cn('每格标注 (a,b)；九种典型组合，同一坐标尺度',-5.95,22,MUTED)
        self.play(FadeIn(atlas),FadeIn(summary),FadeIn(caption),run_time=.55)
        self.wait(3.5);mark(self,records,'nine_panel_summary',cases=[list(p) for p in math_model.CASES])
        BUILD.mkdir(parents=True,exist_ok=True)
        (BUILD/'key_states.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
