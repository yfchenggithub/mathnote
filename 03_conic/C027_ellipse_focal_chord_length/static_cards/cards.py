"""Reference-led C027 portrait cards, composed deterministically with Pillow."""

from io import BytesIO
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageColor
from matplotlib.font_manager import FontProperties
from matplotlib.mathtext import math_to_image
from scripts.static_cards.canvas import chinese_font


W,H=941,1672
REG=Path(chinese_font(False).get_file())
BOLD=Path(chinese_font(True).get_file())
NAVY="#06265e"; BLUE="#168bff"; DEEP="#062e86"; RED="#a20713"
GREEN="#076d4f"; ORANGE="#ffad1e"; PURPLE="#805bd4"


def font(size,bold=False):
    return ImageFont.truetype(str(BOLD if bold else REG),size)


class Painter:
    def __init__(self,kind):
        yy,xx=np.mgrid[0:H,0:W]
        t=np.clip((xx/W*.35+yy/H*.65),0,1)
        a=np.array([237,247,255]); b=np.array([220,240,255])
        rgb=(a[None,None,:]*(1-t[:,:,None])+b[None,None,:]*t[:,:,None]).astype("uint8")
        self.im=Image.fromarray(rgb,"RGB").convert("RGBA")
        self.d=ImageDraw.Draw(self.im)
        self.boxes=[]
        self.image_boxes=[]
        self.kind=kind
        self.decor()
        self.header(kind)

    def decor(self):
        d=self.d
        d.ellipse((-70,66,63,197),fill="#c9e5ff")
        d.ellipse((28,27,68,67),fill="#a5ddff")
        d.ellipse((690,-132,1084,130),outline="#ffffff",width=3)
        d.ellipse((782,-20,961,158),outline="#f8fdff",width=2)
        d.polygon([(606,0),(941,0),(941,186),(804,122)],fill="#e3f3ff")
        d.arc((689,0,1002,233),185,348,fill="#ffffff",width=3)

    def rounded(self,xy,fill,radius=24,outline=None,width=2,shadow=False):
        if shadow:
            layer=Image.new("RGBA",(W,H)); ld=ImageDraw.Draw(layer)
            ld.rounded_rectangle((xy[0],xy[1]+7,xy[2],xy[3]+7),radius,
                                 fill=(66,123,189,35))
            self.im.alpha_composite(layer.filter(ImageFilter.GaussianBlur(12)))
        self.d.rounded_rectangle(xy,radius,fill=fill,outline=outline,width=width)

    def text(self,s,x,y,size=25,color=NAVY,bold=False,anchor=None,track=True):
        f=font(size,bold)
        self.d.text((x,y),s,font=f,fill=color,anchor=anchor)
        box=self.d.textbbox((x,y),s,font=f,anchor=anchor)
        if track:self.boxes.append((s,box))
        return box

    def math(self,s,x,y,size=32,color=NAVY,center=False,track=True):
        buf=BytesIO()
        math_to_image("$"+s+"$",buf,prop=FontProperties(size=size*.72),
                      dpi=100,format="png",color=color)
        buf.seek(0)
        # MathText writes an opaque white canvas. Recover glyph coverage from
        # the known foreground color, so formulas blend into colored panels.
        raw=np.asarray(Image.open(buf).convert("RGB"),dtype=np.float32)
        rgb=np.array(ImageColor.getrgb(color),dtype=np.float32)
        channel=int(np.argmax(255-rgb))
        coverage=np.clip((255-raw[:,:,channel])/(255-rgb[channel]),0,1)
        rgba=np.empty((*coverage.shape,4),dtype=np.uint8)
        rgba[:,:,:3]=rgb.astype(np.uint8)
        rgba[:,:,3]=(coverage*255).astype(np.uint8)
        im=Image.fromarray(rgba,"RGBA")
        if center:x-=im.width//2
        self.im.alpha_composite(im,(int(x),int(y)))
        box=(int(x),int(y),int(x+im.width),int(y+im.height))
        if track:self.boxes.append((s,box))
        return box

    def gradient_strip(self,xy,left,right,radius=18):
        x0,y0,x1,y1=map(int,xy)
        arr=np.zeros((y1-y0,x1-x0,4),dtype="uint8")
        start=np.array(Image.new("RGB",(1,1),left).getpixel((0,0)))
        end=np.array(Image.new("RGB",(1,1),right).getpixel((0,0)))
        t=np.linspace(0,1,x1-x0)
        arr[:,:,:3]=(start[None,None,:]*(1-t)[None,:,None]+end[None,None,:]*t[None,:,None]).astype("uint8")
        arr[:,:,3]=255
        mask=Image.new("L",(x1-x0,y1-y0));ImageDraw.Draw(mask).rounded_rectangle((0,0,x1-x0-1,y1-y0-1),radius,fill=255)
        self.im.paste(Image.fromarray(arr,"RGBA"),(x0,y0),mask)

    def header(self,kind):
        self.text("椭圆焦点弦长公式",79,45,68,"#072664",True)
        self.rounded((689,55,887,145),"#087af5",24,"#ffffff",3,True)
        self.d.polygon([(722,72),(703,105),(718,105),(707,137),
                        (748,92),(731,92),(742,72)],fill="#ffffff")
        self.text(kind,756,73,44,"#ffffff",True)
        subs={"快记":"过焦点的直线与椭圆相交，求所截弦长的公式",
              "快懂":"从方程出发，一步步理解焦点弦长公式",
              "快用":"看到题目，快速判断条件，直接套用公式"}
        self.text(subs[kind],86,145,27,"#33415e")
        self.d.ellipse((902,83,915,96),fill="#238bff")
        self.d.ellipse((896,107,908,120),fill="#ffb327")

    def panel(self,y0,y1,n,title,theme="blue"):
        palettes={"blue":("#eaf5ff","#ffffff","#2096ff",NAVY),
                  "orange":("#fff0d9","#ffffff","#ffae1d","#94300d"),
                  "green":("#e5f9f1","#ffffff","#31ba88","#064b38"),
                  "purple":("#f1eaff","#ffffff",PURPLE,"#30117b")}
        pale,white,accent,titlecolor=palettes[theme]
        self.rounded((22,y0,919,y1),"#ffffff",27,"#f7fbff",2,True)
        self.gradient_strip((47,y0+17,893,y0+72),pale,white,20)
        self.rounded((47,y0+17,121,y0+76),accent,20)
        self.text(str(n),84,y0+20,43,"#ffffff",True,anchor="mt")
        self.text(title,143,y0+23,37,titlecolor,True)

    def small_num(self,n,x,y,color=DEEP):
        self.d.ellipse((x,y,x+42,y+42),fill="#e9f5ff",outline="#c5e6ff",width=2)
        self.text(str(n),x+21,y+2,29,color,True,anchor="mt")

    def image(self,path,x,y,scale=1.0,within=None):
        with Image.open(path) as source:
            im=source.convert("RGBA")
            if scale!=1.0:
                im=im.resize((round(im.width*scale),round(im.height*scale)),
                             Image.Resampling.LANCZOS)
            alpha=im.getchannel("A").getbbox()
            box=(x+alpha[0],y+alpha[1],x+alpha[2],y+alpha[3])
            if within and not (within[0]<=box[0] and within[1]<=box[1]
                               and box[2]<=within[2] and box[3]<=within[3]):
                raise ValueError(f"diagram exceeds panel: {path.name}: {box}")
            self.image_boxes.append((path.name,box))
            self.im.alpha_composite(im,(x,y))

    def save(self,path):
        self.im.convert("RGB").save(path,optimize=True)
        over=[(s,b) for s,b in self.boxes if b[0]<12 or b[1]<12 or b[2]>W-12 or b[3]>H-12]
        if over:raise ValueError(f"text outside card: {over}")
        collisions=[]
        for i,(a,ab) in enumerate(self.boxes):
            for b,bb in self.boxes[i+1:]:
                if min(ab[2],bb[2])>max(ab[0],bb[0])+2 and min(ab[3],bb[3])>max(ab[1],bb[1])+2:
                    collisions.append((a,b))
        if collisions:raise ValueError(f"text/formula overlap: {collisions}")
        return {"text_and_formula_count":len(self.boxes),"edge_overflow":len(over),
                "text_formula_overlap_count":len(collisions),
                "diagram_alpha_boxes":self.image_boxes,"size":[W,H]}


def main_formula(p,x,y,size=51):
    return p.math(r"|PQ|=\frac{2ab^2(1+k^2)}{a^2k^2+b^2}",x,y,size,RED)


def card_001(geometry,output):
    p=Painter("快记")
    p.panel(194,764,1,"条件")
    p.small_num(1,58,295);p.text("椭圆方程",118,295,28,NAVY,True)
    p.math(r"\frac{x^2}{a^2}+\frac{y^2}{b^2}=1",120,339,37)
    p.math(r"a>b>0",123,407,30)
    p.small_num(2,58,485);p.text("焦点",118,485,28,NAVY,True)
    p.math(r"F(\pm c,0),\quad c^2=a^2-b^2",118,528,27)
    p.small_num(3,58,620);p.text("过焦点直线",118,620,28,NAVY,True)
    p.text("直线经过右焦点 F(c,0)",119,665,25)
    p.text("并与椭圆相交于 P、Q。",119,706,25)
    p.image(geometry/"main.png",410,302,within=(22,194,919,764))
    p.rounded((668,285,889,330),"#fff0ed",12)
    p.text("图示 a=3, b=2, k=1",680,294,19,RED,True)
    p.panel(780,1155,2,"核心公式","orange")
    p.text("直线过焦点、斜率 k 存在时，焦点弦长为",100,880,29)
    p.rounded((74,953,867,1117),"#fff6ef",31,"#ffdb8a",5,True)
    main_formula(p,174,982,57)
    p.panel(1170,1399,3,"特例（通径）","green")
    p.text("直线垂直于 x 轴，斜率不存在。",88,1269,27)
    p.text("此时 x = ±c，焦点弦为通径。",88,1315,27)
    p.rounded((548,1242,872,1360),"#edf9f2",22,"#ccefdc",2)
    p.math(r"|PQ|=\frac{2b^2}{a}",582,1272,42,GREEN)
    p.panel(1414,1650,4,"识别信号","purple")
    for i,(s,form) in enumerate((("标准椭圆",r"\frac{x^2}{a^2}+\frac{y^2}{b^2}=1"),
                                  ("过焦点",r"F(\pm c,0)"),("求弦长",r"|PQ|"))):
        x=74+i*292
        p.rounded((x,1519,x+252,1608),"#f2ecff",22)
        p.text(s,x+38,1532,25,"#30117b",True)
        p.math(form,x+30,1569,22)
        if i<2:p.text("+",x+264,1542,28,PURPLE,True)
    return p.save(output)


def card_002(geometry,output):
    p=Painter("快懂")
    p.panel(194,546,0,"问题与图形")
    p.small_num(1,53,280);p.text("椭圆标准形",106,281,26,NAVY,True)
    p.math(r"\frac{x^2}{a^2}+\frac{y^2}{b^2}=1",109,324,35)
    p.math(r"a>b>0",109,383,27)
    p.small_num(2,53,438);p.text("焦点 F(c,0)",108,439,26,NAVY,True)
    p.text("求过焦点弦 PQ 的长",107,483,24)
    p.image(geometry/"main.png",470,240,scale=.85,within=(22,194,919,546))
    p.panel(560,737,1,"思路 1  设直线","orange")
    p.text("过右焦点 F(c,0)，斜率存在，设",91,642,27)
    p.rounded((207,682,737,729),"#fff6ee",17,"#ffcd6e",2)
    p.math(r"y=k(x-c),\quad k\in\mathbb{R}",271,686,35,RED)
    p.panel(751,1019,2,"思路 2  联立求交点","green")
    p.text("将直线代入椭圆方程，整理得到",78,835,26)
    p.rounded((61,881,880,977),"#eaf6ff",17)
    p.math(r"(a^2k^2+b^2)x^2-2a^2k^2cx",83,889,32)
    p.math(r"+a^2k^2c^2-a^2b^2=0",223,932,32)
    p.text("两根的横坐标记为",80,980,23)
    p.math(r"x_1,x_2",306,982,24)
    p.panel(1033,1378,3,"思路 3  由根差求弦长","orange")
    p.rounded((60,1110,522,1172),"#eef1ff",14)
    p.math(r"|PQ|=\sqrt{1+k^2}\,|x_1-x_2|",75,1125,30,DEEP)
    p.text("判别式与根差（由 c² = a² − b² 化简）：",69,1192,25)
    p.math(r"\Delta=4a^2b^4(1+k^2)",80,1232,30)
    p.math(r"|x_1-x_2|=\frac{2ab^2\sqrt{1+k^2}}{a^2k^2+b^2}",80,1278,28)
    p.rounded((556,1103,886,1353),"#fff7ee",20,"#ffd286",3)
    p.text("因此焦点弦长",590,1135,25,RED,True)
    p.math(r"|PQ|=",604,1194,34,RED)
    p.math(r"\frac{2ab^2(1+k^2)}{a^2k^2+b^2}",578,1249,33,RED)
    p.panel(1392,1650,4,"为什么有通径特例？","purple")
    p.text("直线 x = c 垂直于 x 轴；斜率不存在。",57,1474,24)
    p.text("交点为 (c, ±b²/a)，所以",57,1513,23)
    p.rounded((64,1560,468,1624),"#edfaf3",18,"#bcebd6",2)
    p.math(r"|PQ|=\frac{2b^2}{a}",116,1570,32,GREEN)
    p.image(geometry/"latus_rectum.png",600,1408,scale=.85,
            within=(22,1392,919,1650))
    return p.save(output)


def card_003(geometry,output):
    p=Painter("快用")
    p.panel(194,915,1,"解题步骤")
    steps=[("判型：是否标准椭圆",r"\frac{x^2}{a^2}+\frac{y^2}{b^2}=1,\ a>b>0"),
           ("判线：直线是否过焦点",r"F(c,0)\ \mathrm{or}\ F(-c,0)"),
           ("看方向：是否垂直 x 轴",None),
           ("套公式：根据情况选择",None)]
    ys=[283,406,530,659]
    for i,((title,formula),y) in enumerate(zip(steps,ys),1):
        p.small_num(i,48,y);p.text(title,110,y,28,DEEP,True)
        if formula and i==2:p.text("直线经过 F(±c,0)。",113,y+47,25)
        elif formula:p.math(formula,113,y+45,26)
        elif i==3:p.text("垂直时用通径；否则读取斜率 k。",112,y+46,25)
    p.image(geometry/"example.png",425,268,within=(22,194,919,915))
    p.rounded((47,737,537,889),"#fff8ed",20,"#ffcf75",2)
    p.text("斜率存在",73,750,29,RED,True)
    p.math(r"|PQ|=\frac{2ab^2(1+k^2)}{a^2k^2+b^2}",75,806,31,RED)
    p.rounded((553,737,899,889),"#edfaf5",20,"#b9ead9",2)
    p.text("垂直 x 轴",581,750,29,GREEN,True)
    p.math(r"|PQ|=\frac{2b^2}{a}",612,809,34,GREEN)
    p.panel(929,1478,2,"例题","orange")
    p.text("已知椭圆",74,1013,27)
    p.math(r"\frac{x^2}{9}+\frac{y^2}{4}=1",206,1005,25)
    p.text("过右焦点的直线斜率为 1，求弦长。",74,1064,27)
    p.small_num(1,55,1124);p.math(r"a=3,\ b=2,\ c=\sqrt{5}",109,1133,30)
    p.small_num(2,55,1193);p.math(r"y=x-\sqrt{5},\quad k=1",108,1203,30)
    p.small_num(3,55,1265);p.text("代入焦点弦长公式",110,1264,27)
    p.math(r"|PQ|=\frac{2\cdot3\cdot2^2(1+1)}{3^2+2^2}",110,1313,29)
    p.rounded((161,1383,361,1457),"#fff0f1",19)
    p.math(r"\frac{48}{13}",210,1394,37,RED)
    p.rounded((588,1094,893,1457),"#effaf4",23,"#c1ebd5",2)
    p.text("小特例 · 通径",614,1108,25,GREEN,True)
    p.text("x = √5，过右焦点",614,1148,22)
    p.math(r"|PQ|=\frac{2\cdot2^2}{3}=\frac{8}{3}",610,1200,27,GREEN)
    p.image(geometry/"latus_rectum.png",610,1232,scale=.80,
            within=(588,1094,893,1457))
    p.panel(1492,1650,3,"易错提醒","purple")
    for i,(a,b) in enumerate((("a、b 是半轴", "不能把 c 代入主公式"),
                              ("垂直无斜率", "直接使用通径公式"),
                              ("先判过焦点", "否则不能套公式"))):
        x=44+i*296
        p.rounded((x,1569,x+279,1633),"#f6f0ff",15,"#e6dafa",2)
        p.text(a,x+11,1575,23,"#42278a",True)
        p.text(b,x+11,1604,21,NAVY)
    return p.save(output)


CARDS={"001":card_001,"002":card_002,"003":card_003}
