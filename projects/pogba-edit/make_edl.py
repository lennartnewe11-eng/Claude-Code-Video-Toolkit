import json
S="src/"; S2="src2/"
C=[]
def c(src,inn,beats,speed=1.0,**kw):
    d=dict(src=src,**{"in":inn},beats=beats,speed=speed); d.update(kw); C.append(d)
# ---------- INTRO (instrumental) ----------
c(S+"BV1dwad6cE5G.mp4",3.55,8,0.565,cx=[[0,0.72],[1.77,0.56],[2.95,0.44],[3.54,0.39],[4.26,0.33]],cy=0.55,h=0.9,fx=["fadein","zoomin"],fadein_s=1.2)          # anthem, eyes closed (WC semi)
c(S2+"BV1gbgCzUEiS.mp4",18.95,8,0.56,ylim=[0.08,0.84],cx=[[0,0.56],[1.96,0.74],[4,0.76]],fx=["zoomin"])  # anthem profile (WC final)
# ---------- VERSE 1a: "J'ai retrouve le sourire quand j'ai vu le bout du tunnel" ----------
c(S+"BV1ZP4y1H7BF.mp4",37.55,4,0.4,ylim=[0,0.9],cx=[[0,0.6],[0.9,0.55],[2,0.5]])                       # smile (Juve)
c(S+"BV1TyNv6oEHR.mp4",31.3,8,1.0,cx=[[0,0.6],[2.2,0.58],[4,0.53]])                                     # tunnel walk
c(S+"BV1JsGT6pESA.mp4",0.5,4,0.75,cx=[[0,0.47],[1.2,0.55],[2,0.56]])                                   # Etihad walkout
c(S+"BV1JsGT6pESA.mp4",10.0,4,1.0,cx=[[0,0.52],[1,0.47],[2,0.47]])                                     # back view POGBA 6
c(S+"BV1JsGT6pESA.mp4",20.9,4,1.0,cx=0.66)                                                              # blond profile
# ---------- VERSE 1b: skills ----------
c(S+"BV1SzM2zDE17.mp4",30.3,4,1.0,cx=[[0,0.66],[0.45,0.6],[1.0,0.5],[1.55,0.58],[2,0.7]],fx=["punch"])  # vs Bayern
c(S+"BV1SzM2zDE17.mp4",0.0,4,0.8,cx=[[0,0.45],[0.66,0.55],[1.34,0.66],[2,0.6]])                        # vs USA
c(S2+"BV1c5411t7KD.mp4",95.2,4,1.0,cx=[[0,0.44],[0.5,0.42],[1.2,0.58],[1.8,0.6],[2,0.58]])            # dribble vs Inter (Juve)
c(S2+"BV1c5411t7KD.mp4",116.1,4,1.0,cx=[[0,0.52],[0.9,0.58],[1.7,0.42],[2,0.42]])                     # flick vs Verona (Juve)
c(S2+"BV1c5411t7KD.mp4",74.8,4,1.0,cx=[[0,0.38],[1,0.48],[2,0.6]])                                    # chest control + volley (Juve)
c(S+"BV1VP4y1k7eP.mp4",8.6,4,1.0,cx=0.36,ylim=[0,0.9])                                                  # mohawk stare
# ---------- PRE-CHORUS: "graver ton image a l'encre noire sous mes paupieres" ----------
c(S+"BV1R54y1B7CN.mp4",8.1,8,0.5,ylim=[0,0.9],cx=[[0,0.47],[1.9,0.58],[4,0.6]],fx=["zoomin"])           # eyes close-up
c(S2+"BV1gbgCzUEiS.mp4",24.6,4,0.5,ylim=[0.08,0.84],cx=0.74)                                            # anthem w/ Griezmann
c(S+"BV1Ja41197y4.mp4",225.7,4,0.45,ylim=[0.08,1],cx=[[0,0.62],[2,0.52]])                               # blond close-up Etihad
c(S2+"BV1gbgCzUEiS.mp4",53.6,4,0.35,ylim=[0.08,0.84],cx=[[0,0.33],[2,0.4]])                              # looks back POGBA 6
c(S+"BV1JsGT6pESA.mp4",86.6,4,1.0,cx=0.36,ylim=[0.07,1])                                                              # at the net POGBA 6
c(S+"BV1eB4y197w8.mp4",74.9,8,0.5625,ylim=[0.1,1],cx=[[0,0.55],[2.2,0.58],[4,0.55]],fx=["zoomin"])     # WC final goal replay, ball hits net on the drop
# ---------- CHORUS ----------
c(S+"BV1eB4y197w8.mp4",22.3,4,1.0,ylim=[0.1,1],cx=[[0,0.47],[0.5,0.55],[1.2,0.52],[1.9,0.47]],fx=["punch","flash","shake"])  # celebration run
c(S2+"BV1gbgCzUEiS.mp4",153.3,4,0.75,ylim=[0.08,0.84],cx=[[0,0.35],[1,0.43],[2,0.46]],fx=["punch"])     # arms out w/ Matuidi
c(S+"BV1VP4y1k7eP.mp4",12.0,4,1.0,ylim=[0,0.84],cx=[[0,0.36],[0.7,0.3],[1.3,0.42],[2,0.62]],fx=["punch"])  # Udinese volley
c(S+"BV1ZP4y1H7BF.mp4",45.95,4,1.0,ylim=[0,0.9],cx=[[0,0.4],[1,0.42],[2,0.46]],fx=["punch","shake"])  # dance w/ Evra (Juve)
c(S+"BV1ZP4y1H7BF.mp4",64.9,4,1.0,ylim=[0,0.9],cx=[[0,0.4],[0.6,0.43],[1.4,0.39],[2,0.45]])            # Napoli volley strike
c(S+"BV1ZP4y1H7BF.mp4",68.1,4,0.9,ylim=[0,0.9],cx=[[0,0.38],[1,0.55],[2,0.6]])                          # ...into the net
c(S2+"BV1hs411j7J5.mp4",161.5,4,1.0,cx=[[0,0.37],[0.4,0.34],[0.8,0.32],[1.2,0.35],[1.6,0.4],[2,0.44]],fx=["punch"])  # both arms to the sky (official MUFC)
c(S+"BV1JsGT6pESA.mp4",73.0,4,1.0,cx=0.5,fx=["punch","shake"])                                         # celebration
c(S+"BV1JsGT6pESA.mp4",89.9,4,1.0,cx=[[0,0.62],[0.9,0.68],[2,0.58]],fx=["punch"])                       # City header
c(S+"BV1JsGT6pESA.mp4",95.8,8,1.0,cx=[[0,0.65],[1.6,0.63],[2.4,0.56],[3.2,0.52],[4,0.58]])                           # slow-mo look up
c(S2+"BV1Cg41117HH.mp4",101.9,4,1.0,ylim=[0.07,0.92],cx=[[0,0.84],[0.8,0.84],[1.4,0.8],[2,0.72]],fx=["punch"])  # Europa League final goal
c(S2+"BV1hs411j7J5.mp4",367.6,4,1.0,cx=[[0,0.3],[0.8,0.38],[1.4,0.47],[2,0.5]],fx=["punch","shake"])     # arms-crossed celebration (official MUFC)
c(S2+"BV1hs411j7J5.mp4",656.5,4,1.0,cx=[[0,0.36],[1,0.38],[2,0.42]],fx=["punch","flash"])              # hand to ear, arms wide
c(S+"BV1TyNv6oEHR.mp4",38.9,8,1.0,cx=0.5,cy=0.55,h=0.85)                                                              # trophy dance, fireworks
# ---------- BREAKDOWN: "j'sais pas si je t'aime" ----------
c(S+"BV1R54y1B7CN.mp4",45.9,8,1.0,ylim=[0,0.9],cx=0.5)                                                  # finger to the sky
c(S2+"BV1hs411j7J5.mp4",643.45,8,0.575,cx=[[0,0.36],[0.9,0.45],[1.8,0.48],[2.7,0.41],[4,0.47]])         # arms out, calm (official MUFC)
c(S+"BV1JsGT6pESA.mp4",101.0,8,0.55,cx=0.35)                                                           # back view slow-mo
c(S2+"BV1gbgCzUEiS.mp4",27.4,8,0.3,ylim=[0.08,0.84],cx=[[0,0.62],[2.5,0.48],[4,0.42]],fx=["fadeout"],fadeout_s=2.8,
  title=dict(font="fonts/BebasNeue-Regular.ttf",text="PAUL POGBA",sub="LA PIOCHE",start=0.9,fade=1.0,fade_out=0.6,y=0.70))              # eyes closed, fade out + title
beats=sum(x["beats"] for x in C)
print(len(C),"clips",beats,"beats",0.2555+beats*0.5,"s")
json.dump({"bpm":120,"grid0":0.2555,"clips":C},open("edl.json","w"),indent=1)
