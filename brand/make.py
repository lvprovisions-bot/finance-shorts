from PIL import Image, ImageDraw, ImageFont
import os
S=os.path.dirname(os.path.abspath(__file__)); G=os.environ.get('GFONTS', os.path.join(os.path.dirname(S),'.tools','gfonts','ofl'))
BLACK=os.path.join(G,'archivoblack','ArchivoBlack-Regular.ttf'); VAR=os.path.join(G,'archivo','Archivo[wdth,wght].ttf')
NAVY=(11,16,32); DISC=(20,27,51); SLATE=(43,53,86); GREEN=(52,211,120); YEL=(255,216,77); WHITE=(255,255,255)
def archivo(size,w):
    f=ImageFont.truetype(VAR,size)
    f.set_variation_by_axes([w,100])  # axes: Weight, Width
    return f
K=4  # supersample
def mark(d=640):
    """The circular mark at diameter d (transparent outside the circle)."""
    n=800*K; im=Image.new('RGBA',(n,n),(0,0,0,0)); dr=ImageDraw.Draw(im)
    c=n//2; r=320*K
    dr.ellipse([c-r,c-r,c+r,c+r],fill=DISC)
    base=570*K; x=228*K
    for h,col in ((120,SLATE),(210,GREEN),(320,YEL)):
        dr.rounded_rectangle([x,base-h*K,x+92*K,base],radius=18*K,fill=col)
        dr.rectangle([x,base-12*K,x+92*K,base],fill=col)
        x+=(92+34)*K
    pts=[(205,520),(330,430),(420,470),(590,250)]
    dr.line([(a*K,b*K) for a,b in pts],fill=WHITE,width=26*K,joint='curve')
    for a,b in pts: dr.ellipse([a*K-13*K,b*K-13*K,a*K+13*K,b*K+13*K],fill=WHITE)
    dr.polygon([(612*K,222*K),(618*K,318*K),(528*K,282*K)],fill=WHITE)
    im=im.crop((c-r,c-r,c+r,c+r))
    return im.resize((d,d),Image.LANCZOS)
# Profile picture 800x800 (YouTube crops to a circle)
p=Image.new('RGB',(800,800),NAVY); m=mark(640); p.paste(m,(80,80),m); p.save(os.path.join(S,'profile-800.png'))
# Watermark 150x150, transparent around the disc
w=Image.new('RGBA',(150,150),(0,0,0,0)); m=mark(146); w.paste(m,(2,2),m); w.save(os.path.join(S,'watermark-150.png'))
# Banner 2560x1440, all content inside the 1546x423 safe area (x 507-2053, y 508-931)
W,H=2560,1440; b=Image.new('RGB',(W*2,H*2),NAVY); dr=ImageDraw.Draw(b)
line=[(0,1330),(520,1250),(900,1290),(1400,1130),(1800,1170),(2250,1010),(2560,960)]
dr.line([(x*2,y*2) for x,y in line],fill=(30,39,70),width=20,joint='curve')
b=b.resize((W,H),Image.LANCZOS); dr=ImageDraw.Draw(b)
size=106; fb=ImageFont.truetype(BLACK,size)
groupw=300+72+dr.textlength("FINANCE ADVISED",font=fb)
left=int(507+(1546-groupw)/2); m=mark(300); b.paste(m,(left,570),m)
tx=left+300+72
fs=archivo(46,500); fp=archivo(32,650)
y=575
dr.text((tx,y),"FINANCE ",font=fb,fill=WHITE); dr.text((tx+dr.textlength("FINANCE ",font=fb),y),"ADVISED",font=fb,fill=YEL)
y+=size+30
dr.text((tx,y),"Money maths in under a minute.",font=fs,fill=(185,193,217))
y+=46+40
def pill(x,y,text,fill,fg,outline=None):
    tw=dr.textlength(text,font=fp); w_=tw+52; h_=56
    if outline: dr.rounded_rectangle([x,y,x+w_,y+h_],radius=28,outline=outline,width=3)
    else: dr.rounded_rectangle([x,y,x+w_,y+h_],radius=28,fill=fill)
    dr.text((x+26,y+h_/2),text,font=fp,fill=fg,anchor='lm'); return x+w_
x2=pill(tx,y,"New Shorts daily",GREEN,NAVY)
x3=pill(x2+18,y,"Who wins: spender or saver?",None,WHITE,outline=SLATE)
print('wordmark size',size,'right edge',x3,'bottom',y+56,'safe right 2053 bottom 931')
b.save(os.path.join(S,'banner-2560x1440.png'),optimize=True)
for f in ('profile-800.png','watermark-150.png','banner-2560x1440.png'): print(f, os.path.getsize(os.path.join(S,f)))
