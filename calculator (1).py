import tkinter as tk
from tkinter import ttk
import math

# ── PALETTE ────────────────────────────────────────────────────────────────
BG          = "#0F1117"
BG2         = "#171B26"
BG3         = "#1E2433"
BG4         = "#252B3B"
CARD        = "#1A1F2E"
CARD_BORDER = "#2A3045"
ACCENT      = "#E8300B"
ACCENT2     = "#FF5533"
BLUE        = "#3B7DE8"
BLUE2       = "#5B9BFF"
GREEN       = "#22C55E"
GREEN2      = "#4ADE80"
AMBER       = "#F59E0B"
TEXT1       = "#F1F5F9"
TEXT2       = "#94A3B8"
TEXT3       = "#475569"
WHITE       = "#FFFFFF"
FONT        = "Segoe UI"

RAID_DATA = {
    "RAID 0":  ("Striping sem redundancia",       "Todo espaco disponivel. Se 1 HD falhar, perde tudo.",         1, lambda d,t: d*t),
    "RAID 1":  ("Mirroring - espelho total",       "Tolera falha de metade dos discos. Min. 2 HDs.",             2, lambda d,t: math.floor(d/2)*t),
    "RAID 5":  ("Paridade simples distribuida",    "Tolera falha de 1 disco. 1 HD para paridade. Min. 3 HDs.",   3, lambda d,t: (d-1)*t),
    "RAID 6":  ("Dupla paridade distribuida",      "Tolera falha de 2 discos. 2 HDs para paridade. Min. 4 HDs.",4, lambda d,t: (d-2)*t),
    "RAID 10": ("Mirror + Stripe combinados",      "Alta performance e redundancia. Min. 4 HDs (par).",           4, lambda d,t: (d//2)*t),
    "JBOD":    ("Discos independentes, sem RAID",  "Sem redundancia. Capacidade total de todos os HDs.",          1, lambda d,t: d*t),
}
TB_SIZES = [0.5,1,2,3,4,6,8,10,12,14,16,18,20]
RES_MAP  = {
    "D1 / CIF - 0.5 MP":0.5,"720p HD - 1 MP":1,"1080p Full HD - 2 MP":2,
    "4 MP":4,"3K / 5 MP":5,"4K Ultra HD - 8 MP":8,"12 MP":12
}
COMP_MAP = {"H.265 / H.265+":0.5,"H.264":1.0,"MJPEG":1.5}
BR_BASE  = {0.5:512,1:1024,2:2048,4:4096,5:5120,8:8192,12:12288}

def fmt(v, unit="TB"):
    if unit=="TB":
        if v>=1000: return f"{v/1000:.1f} PB"
        if v>=1:    return f"{v:.2f} TB"
        return f"{v*1024:.0f} GB"
    if unit=="GB":
        if v>=1024: return f"{v/1024:.2f} TB"
        return f"{v:.1f} GB"
    return str(v)

class Divider(tk.Frame):
    def __init__(self,p,**kw): super().__init__(p,bg=CARD_BORDER,height=1,**kw)

class Card(tk.Frame):
    def __init__(self,p,**kw):
        super().__init__(p,bg=CARD,highlightbackground=CARD_BORDER,highlightthickness=1,**kw)

class MetricCard(tk.Frame):
    def __init__(self,p,label,icon="",**kw):
        super().__init__(p,bg=BG3,highlightbackground=CARD_BORDER,highlightthickness=1,**kw)
        top=tk.Frame(self,bg=BG3); top.pack(fill="x",padx=14,pady=14)
        tk.Label(top,text=icon,font=(FONT,10),fg=TEXT3,bg=BG3).pack(side="left")
        tk.Label(top,text=label,font=(FONT,9),fg=TEXT2,bg=BG3).pack(side="left",padx=6)
        self.val=tk.Label(self,text="--",font=(FONT,20,"bold"),fg=TEXT1,bg=BG3)
        self.val.pack(anchor="w",padx=14)
        self.sub=tk.Label(self,text="",font=(FONT,8),fg=TEXT3,bg=BG3)
        self.sub.pack(anchor="w",padx=14,pady=14)
    def set(self,v,s="",c=TEXT1):
        self.val.config(text=v,fg=c); self.sub.config(text=s)

class ProgressBar(tk.Frame):
    def __init__(self,p,**kw):
        super().__init__(p,bg=BG4,height=8,**kw)
        self.fill=tk.Frame(self,bg=GREEN,height=8)
        self.fill.place(x=0,y=0,relheight=1,relwidth=0)
    def set(self,pct):
        pct=max(0,min(pct,100))
        self.fill.place(relwidth=pct/100)
        self.fill.config(bg=GREEN if pct<70 else AMBER if pct<90 else ACCENT)

def make_combo(p,var,vals,cmd=None,**kw):
    cb=ttk.Combobox(p,textvariable=var,values=vals,state="readonly",font=(FONT,10),**kw)
    if cmd: cb.bind("<<ComboboxSelected>>",lambda e:cmd())
    return cb

def make_spin(p,var,mn,mx,step=1,**kw):
    return ttk.Spinbox(p,from_=mn,to=mx,increment=step,textvariable=var,font=(FONT,10),**kw)

def field(p,label):
    f=tk.Frame(p,bg=CARD); f.pack(fill="x",pady=5)
    tk.Label(f,text=label,font=(FONT,8,"bold"),fg=TEXT3,bg=CARD).pack(anchor="w",pady=5)
    return f

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Intelbras Storage Calculator")
        self.configure(bg=BG)
        self.minsize(960,680)
        try: self.state("zoomed")
        except: self.geometry("960x700")
        self._style()
        self._header()
        self._sidebar()
        self._content()
        self._footer()
        self._show("raid")
        self.after(150,lambda:(self._calc_raid(),self._calc_cam()))

    def _style(self):
        s=ttk.Style(self); s.theme_use("clam")
        for w in ("TCombobox","TSpinbox"):
            s.configure(w,fieldbackground=BG4,background=BG4,foreground=TEXT1,
                        arrowcolor=TEXT2,bordercolor=CARD_BORDER,lightcolor=CARD_BORDER,
                        darkcolor=CARD_BORDER,selectbackground=BLUE,selectforeground=WHITE,
                        font=(FONT,10),padding=8,relief="flat")
            s.map(w,fieldbackground=[("readonly",BG4),("disabled",BG3)],
                  foreground=[("disabled",TEXT3)],
                  selectbackground=[("readonly",BG4)],
                  selectforeground=[("readonly",TEXT1)])

    def _header(self):
        h=tk.Frame(self,bg=BG2,height=64); h.pack(fill="x"); h.pack_propagate(False)
        left=tk.Frame(h,bg=BG2); left.pack(side="left",padx=20,pady=12)
        logo=tk.Frame(left,bg=ACCENT,width=38,height=38); logo.pack(side="left"); logo.pack_propagate(False)
        tk.Frame(logo,bg=WHITE,width=14,height=14).place(relx=0.5,rely=0.5,anchor="center")
        info=tk.Frame(left,bg=BG2); info.pack(side="left",padx=12)
        tk.Label(info,text="INTELBRAS",font=(FONT,13,"bold"),fg=WHITE,bg=BG2).pack(anchor="w")
        tk.Label(info,text="Storage & CFTV Calculator",font=(FONT,9),fg=TEXT2,bg=BG2).pack(anchor="w")
        right=tk.Frame(h,bg=BG2); right.pack(side="right",padx=20)
        badge=tk.Frame(right,bg=BG4,highlightbackground=CARD_BORDER,highlightthickness=1); badge.pack()
        tk.Label(badge,text="v2.0  PRO",font=(FONT,9,"bold"),fg=BLUE2,bg=BG4,padx=10,pady=4).pack()
        Divider(self).pack(fill="x")

    def _sidebar(self):
        self.sb=tk.Frame(self,bg=BG2,width=210); self.sb.pack(side="left",fill="y"); self.sb.pack_propagate(False)
        Divider(self.sb).pack(fill="x")
        nav_hdr=tk.Frame(self.sb,bg=BG2); nav_hdr.pack(fill="x",padx=16,pady=20)
        tk.Label(nav_hdr,text="FERRAMENTAS",font=(FONT,8,"bold"),fg=TEXT3,bg=BG2).pack(anchor="w")
        self._nav_ws={}
        for key,icon,label in [("raid","💾","Calculadora RAID"),("cameras","📹","Cameras & Gravacao"),("combinado","📊","Analise Combinada")]:
            self._nav_ws[key]=self._nav_btn(key,icon,label)
        Divider(self.sb).pack(fill="x",pady=16)
        inf=tk.Frame(self.sb,bg=BG3,highlightbackground=CARD_BORDER,highlightthickness=1)
        inf.pack(fill="x",padx=12,pady=4)
        tk.Label(inf,text="Dica rapida",font=(FONT,9,"bold"),fg=BLUE2,bg=BG3,padx=12,pady=10).pack(anchor="w")
        self.tip=tk.Label(inf,text="Configure o RAID\ne depois as cameras\npara ver a analise\ncombinada.",
                          font=(FONT,8),fg=TEXT2,bg=BG3,justify="left",wraplength=170,padx=12,pady=12)
        self.tip.pack(anchor="w")
        Divider(self.sb).pack(fill="x",side="bottom")

    def _nav_btn(self,key,icon,label):
        fr=tk.Frame(self.sb,bg=BG2,cursor="hand2"); fr.pack(fill="x")
        ind=tk.Frame(fr,bg=BG2,width=3); ind.pack(side="left",fill="y")
        inn=tk.Frame(fr,bg=BG2); inn.pack(side="left",fill="both",expand=True,padx=12,pady=10)
        ic=tk.Label(inn,text=icon,font=(FONT,14),bg=BG2,fg=TEXT2); ic.pack(side="left")
        tx=tk.Label(inn,text=label,font=(FONT,10),bg=BG2,fg=TEXT2); tx.pack(side="left",padx=10)
        def enter(_):
            if self._active!=key:
                for w in (fr,inn): w.config(bg=BG3)
                ind.config(bg=BG3); ic.config(bg=BG3); tx.config(bg=BG3)
        def leave(_):
            if self._active!=key:
                for w in (fr,inn): w.config(bg=BG2)
                ind.config(bg=BG2); ic.config(bg=BG2); tx.config(bg=BG2)
        def click(_): self._show(key)
        for w in (fr,inn,ic,tx,ind):
            w.bind("<Enter>",enter); w.bind("<Leave>",leave); w.bind("<Button-1>",click)
        return {"fr":fr,"inn":inn,"ind":ind,"ic":ic,"tx":tx}

    def _show(self,key):
        self._active=key
        for k,w in self._nav_ws.items():
            on=k==key
            bg=BG3 if on else BG2
            for ww in (w["fr"],w["inn"]): ww.config(bg=bg)
            w["ind"].config(bg=ACCENT if on else BG2)
            w["ic"].config(bg=bg,fg=WHITE if on else TEXT2)
            w["tx"].config(bg=bg,fg=TEXT1 if on else TEXT2,font=(FONT,10,"bold" if on else "normal"))
        for k,p in self._panels.items():
            if k==key: p.pack(fill="both",expand=True)
            else: p.pack_forget()

    def _content(self):
        self._active=""
        self._panels={}
        self.main=tk.Frame(self,bg=BG); self.main.pack(side="left",fill="both",expand=True)
        self._raid_panel()
        self._cam_panel()
        self._combined_panel()

    def _sec_hdr(self,p,title,sub=""):
        h=tk.Frame(p,bg=BG); h.pack(fill="x",padx=24,pady=20)
        tk.Label(h,text=title,font=(FONT,15,"bold"),fg=TEXT1,bg=BG).pack(anchor="w")
        if sub: tk.Label(h,text=sub,font=(FONT,9),fg=TEXT2,bg=BG).pack(anchor="w",pady=2)
        Divider(p).pack(fill="x",padx=24)

    # ──────────────────────────────────────────────────────── RAID ──────────
    def _raid_panel(self):
        p=tk.Frame(self.main,bg=BG); self._panels["raid"]=p
        self._sec_hdr(p,"Calculadora RAID","Configure os discos e o tipo de array para calcular o volume disponivel")
        body=tk.Frame(p,bg=BG); body.pack(fill="both",expand=True,padx=24,pady=16)
        body.columnconfigure(0,weight=2); body.columnconfigure(1,weight=3); body.rowconfigure(0,weight=1)

        # LEFT
        left=Card(body); left.grid(row=0,column=0,sticky="nsew",padx=12)
        tk.Label(left,text="Configuracao dos Discos",font=(FONT,11,"bold"),fg=TEXT1,bg=CARD,padx=20,pady=16).pack(anchor="w")
        Divider(left).pack(fill="x")
        frm=tk.Frame(left,bg=CARD,padx=20,pady=14); frm.pack(fill="x")

        # num HDs quick select
        ff=field(frm,"NUMERO DE HDs")
        self.v_nhd=tk.IntVar(value=4)
        self.v_nhd.trace_add("write",lambda *_:self._calc_raid())
        qrow=tk.Frame(ff,bg=CARD); qrow.pack(fill="x"); self._nhd_qrow=qrow
        for v in [2,4,8,12,16,24]:
            b=tk.Label(qrow,text=str(v),font=(FONT,10),bg=BG4,fg=TEXT2,width=4,pady=6,
                       cursor="hand2",highlightbackground=CARD_BORDER,highlightthickness=1)
            b.pack(side="left",padx=4)
            b.bind("<Button-1>",lambda e,x=v:(self.v_nhd.set(x),self._upd_nhd()))
            b.bind("<Enter>",lambda e,w=b:w.config(bg=BG3,fg=TEXT1))
            b.bind("<Leave>",lambda e,w=b:self._upd_nhd())
        cust=tk.Frame(ff,bg=CARD); cust.pack(fill="x",pady=6)
        tk.Label(cust,text="Personalizado:",font=(FONT,9),fg=TEXT3,bg=CARD).pack(side="left")
        make_spin(cust,self.v_nhd,1,64,width=8).pack(side="left",padx=8)

        # capacidade
        ff2=field(frm,"CAPACIDADE POR HD")
        self.v_thd=tk.StringVar(value="4 TB")
        self.v_thd.trace_add("write",lambda *_:self._calc_raid())
        make_combo(ff2,self.v_thd,[f"{v} TB" for v in TB_SIZES],cmd=self._calc_raid,width=30).pack(fill="x")

        # RAID type buttons
        ff3=field(frm,"TIPO DE RAID")
        rgrid=tk.Frame(ff3,bg=CARD); rgrid.pack(fill="x"); self._rbw={}
        raids=["RAID 0","RAID 1","RAID 5","RAID 6","RAID 10","JBOD"]
        for i,r in enumerate(raids):
            c=i%3; ro=i//3
            btn=tk.Frame(rgrid,bg=BG4,highlightbackground=CARD_BORDER,highlightthickness=1,cursor="hand2")
            btn.grid(row=ro,column=c,padx=6,pady=6,sticky="ew"); rgrid.columnconfigure(c,weight=1)
            lbl=tk.Label(btn,text=r,font=(FONT,10,"bold"),bg=BG4,fg=TEXT2,pady=9,cursor="hand2")
            lbl.pack()
            def on_click(e,rv=r): self.v_raid.set(rv); self._upd_rbw(); self._calc_raid()
            def on_ent(e,bw=btn,lw=lbl,rv=r):
                if self.v_raid.get()!=rv: bw.config(highlightbackground=BLUE); lw.config(fg=TEXT1)
            def on_lv(e,rv=r): self._upd_rbw()
            for w in (btn,lbl):
                w.bind("<Button-1>",on_click); w.bind("<Enter>",on_ent); w.bind("<Leave>",on_lv)
            self._rbw[r]=(btn,lbl)
        self.v_raid=tk.StringVar(value="RAID 5")
        self.lbl_rdesc=tk.Label(frm,text="",font=(FONT,9),fg=TEXT2,bg=CARD,wraplength=300,justify="left")
        self.lbl_rdesc.pack(anchor="w",pady=4)

        # Hot Spare — quantidade configuravel
        ff4=field(frm,"HOT SPARE")
        hs_row=tk.Frame(ff4,bg=CARD); hs_row.pack(fill="x")
        self.v_hs=tk.IntVar(value=0)
        self.v_hs.trace_add("write",lambda *_:self._calc_raid())

        # botoes rapidos 0-3
        self._hs_qrow=tk.Frame(hs_row,bg=CARD); self._hs_qrow.pack(side="left")
        for v in [0,1,2,3]:
            lbl="Nenhum" if v==0 else f"{v} HD{'s' if v>1 else ''}"
            b=tk.Label(self._hs_qrow,text=lbl,font=(FONT,9,"bold"),bg=BG4,fg=TEXT2,
                       padx=10,pady=7,cursor="hand2",
                       highlightbackground=CARD_BORDER,highlightthickness=1)
            b.pack(side="left",padx=4)
            b.bind("<Button-1>",lambda e,x=v:(self.v_hs.set(x),self._upd_hs_btns()))
            b.bind("<Enter>",lambda e,w=b:w.config(bg=BG3,fg=TEXT1))
            b.bind("<Leave>",lambda e,w=b:self._upd_hs_btns())

        # spinbox para valores maiores
        cust_hs=tk.Frame(ff4,bg=CARD); cust_hs.pack(fill="x",pady=6)
        tk.Label(cust_hs,text="Personalizado:",font=(FONT,9),fg=TEXT3,bg=CARD).pack(side="left")
        make_spin(cust_hs,self.v_hs,0,16,width=6).pack(side="left",padx=8)

        self.hs_lbl=tk.Label(ff4,text="",font=(FONT,9),fg=TEXT3,bg=CARD)
        self.hs_lbl.pack(anchor="w",pady=4)
        self._upd_hs_btns()

        self._upd_nhd(); self._upd_rbw()

        # RIGHT
        right=tk.Frame(body,bg=BG); right.grid(row=0,column=1,sticky="nsew")
        tk.Label(right,text="Resultado do Array",font=(FONT,11,"bold"),fg=TEXT1,bg=BG).pack(anchor="w",pady=12)
        g=tk.Frame(right,bg=BG); g.pack(fill="x",pady=12)
        g.columnconfigure(0,weight=1); g.columnconfigure(1,weight=1)
        self.mc_rd=MetricCard(g,"HDs no Array",""); self.mc_rd.grid(row=0,column=0,sticky="ew",padx=8,pady=8)
        self.mc_rb=MetricCard(g,"Capacidade Bruta",""); self.mc_rb.grid(row=0,column=1,sticky="ew",pady=8)
        self.mc_ru=MetricCard(g,"Volume Disponivel",""); self.mc_ru.grid(row=1,column=0,sticky="ew",padx=8)
        self.mc_re=MetricCard(g,"Eficiencia de Uso",""); self.mc_re.grid(row=1,column=1,sticky="ew")

        bc=Card(right); bc.pack(fill="x",pady=12)
        bt=tk.Frame(bc,bg=CARD); bt.pack(fill="x",padx=16,pady=14)
        tk.Label(bt,text="Aproveitamento do storage",font=(FONT,9,"bold"),fg=TEXT2,bg=CARD).pack(side="left")
        self.lbl_pct_r=tk.Label(bt,text="",font=(FONT,9,"bold"),fg=BLUE2,bg=CARD); self.lbl_pct_r.pack(side="right")
        self.pb_raid=ProgressBar(bc); self.pb_raid.pack(fill="x",padx=16,pady=6)
        self.lbl_bar_s=tk.Label(bc,text="",font=(FONT,8),fg=TEXT3,bg=CARD,padx=16,pady=10); self.lbl_bar_s.pack(anchor="w")
        self.info_r=tk.Label(right,text="",font=(FONT,9),fg=TEXT2,bg=BG3,wraplength=420,
                             justify="left",padx=14,pady=10,highlightbackground=CARD_BORDER,highlightthickness=1)
        self.info_r.pack(fill="x",pady=10)

    def _upd_hs_btns(self):
        try: cur=int(self.v_hs.get())
        except: cur=0
        for ch in self._hs_qrow.winfo_children():
            txt=ch.cget("text")
            val=0 if txt=="Nenhum" else int(txt.split()[0])
            if val==cur:
                ch.config(bg=GREEN if cur>0 else BG4,
                          fg="#052E16" if cur>0 else TEXT2,
                          highlightbackground=GREEN if cur>0 else CARD_BORDER,
                          highlightthickness=2 if cur>0 else 1)
            else:
                ch.config(bg=BG4,fg=TEXT2,highlightbackground=CARD_BORDER,highlightthickness=1)
        if cur==0:
            self.hs_lbl.config(text="Sem disco de reserva configurado.",fg=TEXT3)
        elif cur==1:
            self.hs_lbl.config(text="1 HD reservado em standby para substituicao automatica.",fg=GREEN)
        else:
            self.hs_lbl.config(text=f"{cur} HDs reservados em standby para substituicao automatica.",fg=GREEN)

    def _upd_nhd(self):
        try: cur=int(self.v_nhd.get())
        except: return
        for ch in self._nhd_qrow.winfo_children():
            try:
                v=int(ch.cget("text"))
                if v==cur: ch.config(bg=ACCENT,fg=WHITE,highlightbackground=ACCENT,highlightthickness=2)
                else: ch.config(bg=BG4,fg=TEXT2,highlightbackground=CARD_BORDER,highlightthickness=1)
            except: pass

    def _upd_rbw(self):
        cur=self.v_raid.get()
        for r,(btn,lbl) in self._rbw.items():
            if r==cur: btn.config(bg=ACCENT,highlightbackground=ACCENT,highlightthickness=2); lbl.config(bg=ACCENT,fg=WHITE)
            else: btn.config(bg=BG4,highlightbackground=CARD_BORDER,highlightthickness=1); lbl.config(bg=BG4,fg=TEXT2)

    def _calc_raid(self,*_):
        try: n=int(self.v_nhd.get()); tam=float(self.v_thd.get().replace(" TB",""))
        except: return
        self._upd_nhd()
        raid=self.v_raid.get()
        try: hs=int(self.v_hs.get())
        except: hs=0
        if raid not in RAID_DATA: return
        sub,desc,min_d,calc=RAID_DATA[raid]
        self.lbl_rdesc.config(text=f"  {desc}")
        self._upd_hs_btns()
        dr=max(n-hs,1) if hs>0 else n
        bruto=dr*tam
        # valida minimo de discos ativos
        if dr<min_d and raid not in ("JBOD","RAID 0"):
            err=f"  {raid} requer minimo {min_d} HDs ativos. Reduza os Hot Spares ou adicione HDs."
            self.mc_rd.set(str(dr),"discos ativos"); self.mc_rb.set(fmt(n*tam),f"{n*tam:.1f} TB bruto total")
            self.mc_ru.set("--",err,ACCENT); self.mc_re.set("--","",TEXT3)
            self.pb_raid.set(0); self.lbl_pct_r.config(text="0%")
            self.lbl_bar_s.config(text=err); self.info_r.config(text=err,fg=AMBER)
            self._upd_combined(); return
        try: util=calc(dr,tam)
        except: util=0
        efic=round((util/bruto)*100) if bruto>0 else 0
        col=GREEN if efic>=75 else AMBER if efic>=50 else ACCENT
        self.mc_rd.set(str(dr),"discos ativos no array")
        self.mc_rb.set(fmt(n*tam),f"{n*tam:.1f} TB bruto total ({n} HDs)")
        self.mc_ru.set(fmt(util),f"{util:.2f} TB disponiveis para uso",BLUE2)
        self.mc_re.set(f"{efic}%","do espaco bruto aproveitado",col)
        self.pb_raid.set(efic); self.lbl_pct_r.config(text=f"{efic}% aproveitado")
        hs_t=f"  |  {hs} Hot Spare{'s' if hs>1 else ''} ({hs*tam:.1f} TB reservados)" if hs>0 else ""
        self.lbl_bar_s.config(text=f"{dr} HDs ativos x {tam} TB  |  {raid}  |  {sub}{hs_t}")
        self.info_r.config(text=f"Util: {fmt(util)}   |   Overhead RAID: {fmt(bruto-util)}   |   Hot Spare: {hs} HD(s) = {hs*tam:.1f} TB   |   Eficiencia: {efic}%",fg=TEXT2)
        self._upd_combined()

    # ──────────────────────────────────────────────────────── CAMERAS ───────
    def _cam_panel(self):
        p=tk.Frame(self.main,bg=BG); self._panels["cameras"]=p
        self._sec_hdr(p,"Cameras & Gravacao","Calcule o armazenamento necessario para o seu sistema de CFTV")
        body=tk.Frame(p,bg=BG); body.pack(fill="both",expand=True,padx=24,pady=16)
        body.columnconfigure(0,weight=2); body.columnconfigure(1,weight=3); body.rowconfigure(0,weight=1)

        # LEFT
        left=Card(body); left.grid(row=0,column=0,sticky="nsew",padx=12)
        tk.Label(left,text="Parametros de Gravacao",font=(FONT,11,"bold"),fg=TEXT1,bg=CARD,padx=20,pady=16).pack(anchor="w")
        Divider(left).pack(fill="x")
        frm=tk.Frame(left,bg=CARD,padx=20,pady=14); frm.pack(fill="x")

        # cameras quick
        ff=field(frm,"NUMERO DE CAMERAS")
        self.v_ncam=tk.IntVar(value=8)
        self.v_ncam.trace_add("write",lambda *_:self._calc_cam())
        cqrow=tk.Frame(ff,bg=CARD); cqrow.pack(fill="x"); self._cqrow=cqrow
        for v in [4,8,16,32,64]:
            b=tk.Label(cqrow,text=str(v),font=(FONT,10),bg=BG4,fg=TEXT2,width=4,pady=6,
                       cursor="hand2",highlightbackground=CARD_BORDER,highlightthickness=1)
            b.pack(side="left",padx=4)
            b.bind("<Button-1>",lambda e,x=v:(self.v_ncam.set(x),self._upd_cqrow()))
            b.bind("<Enter>",lambda e,w=b:w.config(bg=BG3,fg=TEXT1))
            b.bind("<Leave>",lambda e,w=b:self._upd_cqrow())
        cust=tk.Frame(ff,bg=CARD); cust.pack(fill="x",pady=6)
        tk.Label(cust,text="Personalizado:",font=(FONT,9),fg=TEXT3,bg=CARD).pack(side="left")
        make_spin(cust,self.v_ncam,1,512,width=8).pack(side="left",padx=8)

        ff2=field(frm,"RESOLUCAO")
        self.v_res=tk.StringVar(value="1080p Full HD - 2 MP")
        make_combo(ff2,self.v_res,list(RES_MAP.keys()),cmd=self._calc_cam,width=30).pack(fill="x")

        r2=tk.Frame(frm,bg=CARD); r2.pack(fill="x")
        c1=tk.Frame(r2,bg=CARD); c1.pack(side="left",expand=True,fill="x",padx=8)
        tk.Label(c1,text="COMPRESSAO",font=(FONT,8,"bold"),fg=TEXT3,bg=CARD).pack(anchor="w",pady=5)
        self.v_comp=tk.StringVar(value="H.265 / H.265+")
        make_combo(c1,self.v_comp,list(COMP_MAP.keys()),cmd=self._calc_cam,width=14).pack(fill="x")
        c2=tk.Frame(r2,bg=CARD); c2.pack(side="left",expand=True,fill="x")
        tk.Label(c2,text="FPS",font=(FONT,8,"bold"),fg=TEXT3,bg=CARD).pack(anchor="w",pady=5)
        self.v_fps=tk.StringVar(value="15 fps")
        make_combo(c2,self.v_fps,["1 fps","5 fps","10 fps","15 fps","20 fps","25 fps","30 fps"],cmd=self._calc_cam,width=12).pack(fill="x")

        ff3=field(frm,"MODO DE BITRATE")
        self.v_bitmode=tk.StringVar(value="Automatico")
        make_combo(ff3,self.v_bitmode,["Automatico","Manual (Kbps)"],cmd=self._calc_cam,width=30).pack(fill="x")
        self.ff_manual=tk.Frame(frm,bg=CARD); self.ff_manual.pack(fill="x",pady=4)
        tk.Label(self.ff_manual,text="BITRATE POR CAMERA (KBPS)",font=(FONT,8,"bold"),fg=TEXT3,bg=CARD).pack(anchor="w",pady=5)
        self.v_bitrate=tk.IntVar(value=2048)
        self.v_bitrate.trace_add("write",lambda *_:self._calc_cam())
        self.spin_bit=make_spin(self.ff_manual,self.v_bitrate,64,32000,step=64,width=30); self.spin_bit.pack(fill="x")

        r3=tk.Frame(frm,bg=CARD); r3.pack(fill="x",pady=10)
        d1=tk.Frame(r3,bg=CARD); d1.pack(side="left",expand=True,fill="x",padx=8)
        tk.Label(d1,text="DIAS DE RETENCAO",font=(FONT,8,"bold"),fg=TEXT3,bg=CARD).pack(anchor="w",pady=5)
        self.v_dias=tk.IntVar(value=30); self.v_dias.trace_add("write",lambda *_:self._calc_cam())
        make_spin(d1,self.v_dias,1,365,width=14).pack(fill="x")
        d2=tk.Frame(r3,bg=CARD); d2.pack(side="left",expand=True,fill="x")
        tk.Label(d2,text="HORAS/DIA GRAVANDO",font=(FONT,8,"bold"),fg=TEXT3,bg=CARD).pack(anchor="w",pady=5)
        self.v_horas=tk.IntVar(value=24); self.v_horas.trace_add("write",lambda *_:self._calc_cam())
        make_spin(d2,self.v_horas,1,24,width=14).pack(fill="x")

        self._upd_cqrow()

        # RIGHT
        right=tk.Frame(body,bg=BG); right.grid(row=0,column=1,sticky="nsew")
        tk.Label(right,text="Resultado",font=(FONT,11,"bold"),fg=TEXT1,bg=BG).pack(anchor="w",pady=12)
        g=tk.Frame(right,bg=BG); g.pack(fill="x",pady=12)
        g.columnconfigure(0,weight=1); g.columnconfigure(1,weight=1)
        self.mc_cbt=MetricCard(g,"Bitrate Total",""); self.mc_cbt.grid(row=0,column=0,sticky="ew",padx=8,pady=8)
        self.mc_cpd=MetricCard(g,"Por camera / dia",""); self.mc_cpd.grid(row=0,column=1,sticky="ew",pady=8)
        self.mc_cst=MetricCard(g,"Total Necessario",""); self.mc_cst.grid(row=1,column=0,sticky="ew",padx=8)
        self.mc_cd1=MetricCard(g,"Dias com 1 TB",""); self.mc_cd1.grid(row=1,column=1,sticky="ew")
        self.cam_sum=Card(right); self.cam_sum.pack(fill="x",pady=12)
        self.lbl_csum=tk.Label(self.cam_sum,text="",font=(FONT,9),fg=TEXT2,bg=CARD,
                               justify="left",padx=16,pady=14,wraplength=440); self.lbl_csum.pack(anchor="w")

    def _upd_cqrow(self):
        try: cur=int(self.v_ncam.get())
        except: return
        for ch in self._cqrow.winfo_children():
            try:
                v=int(ch.cget("text"))
                if v==cur: ch.config(bg=BLUE,fg=WHITE,highlightbackground=BLUE,highlightthickness=2)
                else: ch.config(bg=BG4,fg=TEXT2,highlightbackground=CARD_BORDER,highlightthickness=1)
            except: pass

    def _calc_cam(self,*_):
        try:
            ncam=int(self.v_ncam.get()); res=RES_MAP.get(self.v_res.get(),2)
            comp=COMP_MAP.get(self.v_comp.get(),0.5); fps=int(self.v_fps.get().replace(" fps",""))
            dias=int(self.v_dias.get()); horas=int(self.v_horas.get())
            auto=self.v_bitmode.get()=="Automatico"
        except: return
        self._upd_cqrow()
        if auto: br=BR_BASE.get(res,2048)*comp*(fps/15); self.spin_bit.config(state="disabled")
        else: br=float(self.v_bitrate.get()); self.spin_bit.config(state="normal")
        mbps=(br*ncam)/1000; gb_cam=(br*3600*horas)/(8*1024*1024)
        total_tb=(gb_cam*ncam*dias)/1024; d1tb=(1024/(gb_cam*ncam)) if gb_cam*ncam>0 else 0
        self.mc_cbt.set(f"{mbps:.1f} Mbps",f"{br:.0f} Kbps por camera",BLUE2)
        self.mc_cpd.set(fmt(gb_cam,"GB"),"por camera por dia",TEXT1)
        self.mc_cst.set(fmt(total_tb),f"{ncam} cam. x {dias} dias x {horas}h",ACCENT)
        self.mc_cd1.set(f"{d1tb:.1f} dias","de gravacao por 1 TB",GREEN)
        self.lbl_csum.config(
            text=f"  {ncam} camera{'s' if ncam>1 else ''}  |  {self.v_res.get()}  |  {self.v_comp.get()}  |  {fps} fps\n"
                 f"  Retencao: {dias} dias x {horas}h/dia  |  Bitrate: {br:.0f} Kbps/camera\n"
                 f"  Armazenamento total necessario: {fmt(total_tb)}")
        self._upd_combined()

    # ──────────────────────────────────────────────────── COMBINED ──────────
    def _combined_panel(self):
        p=tk.Frame(self.main,bg=BG); self._panels["combinado"]=p
        self._sec_hdr(p,"Analise Combinada","Comparacao entre volume disponivel no RAID e o necessario pelas cameras")
        body=tk.Frame(p,bg=BG); body.pack(fill="both",expand=True,padx=24,pady=16)

        top=tk.Frame(body,bg=BG); top.pack(fill="x",pady=16)
        top.columnconfigure(0,weight=1); top.columnconfigure(1,weight=1); top.columnconfigure(2,weight=1)
        self.mc_xr=MetricCard(top,"Disponivel no RAID",""); self.mc_xr.grid(row=0,column=0,sticky="ew",padx=8)
        self.mc_xc=MetricCard(top,"Necessario pelas Cameras",""); self.mc_xc.grid(row=0,column=1,sticky="ew",padx=8)
        self.mc_xl=MetricCard(top,"Saldo / Deficit",""); self.mc_xl.grid(row=0,column=2,sticky="ew")

        vc=Card(body); vc.pack(fill="x",pady=16)
        vr=tk.Frame(vc,bg=CARD); vr.pack(fill="x",padx=20,pady=16)
        self.lbl_vi=tk.Label(vr,text="",font=(FONT,26),bg=CARD); self.lbl_vi.pack(side="left")
        vt=tk.Frame(vr,bg=CARD); vt.pack(side="left",padx=12)
        self.lbl_vt=tk.Label(vt,text="",font=(FONT,12,"bold"),fg=GREEN,bg=CARD); self.lbl_vt.pack(anchor="w")
        self.lbl_vs=tk.Label(vt,text="",font=(FONT,9),fg=TEXT2,bg=CARD,wraplength=600,justify="left"); self.lbl_vs.pack(anchor="w",pady=4)

        gc=Card(body); gc.pack(fill="x",pady=16)
        gt=tk.Frame(gc,bg=CARD); gt.pack(fill="x",padx=16,pady=14)
        tk.Label(gt,text="Utilizacao do storage RAID",font=(FONT,9,"bold"),fg=TEXT2,bg=CARD).pack(side="left")
        self.lbl_gpct=tk.Label(gt,text="",font=(FONT,11,"bold"),fg=BLUE2,bg=CARD); self.lbl_gpct.pack(side="right")
        self.pb_comb=ProgressBar(gc); self.pb_comb.pack(fill="x",padx=16,pady=14)

        # tabela resumo
        tc=Card(body); tc.pack(fill="x")
        tk.Label(tc,text="Resumo Tecnico",font=(FONT,10,"bold"),fg=TEXT1,bg=CARD,padx=20,pady=14).pack(anchor="w")
        Divider(tc).pack(fill="x")
        tf=tk.Frame(tc,bg=CARD,padx=20,pady=12); tf.pack(fill="x")
        self._tbl=[]
        rows_def=[("RAID configurado",""),("Volume RAID disponivel",""),("Numero de cameras",""),
                  ("Armazenamento necessario",""),("Saldo de espaco",""),("Taxa de utilizacao","")]
        for i,(lbl,_) in enumerate(rows_def):
            row=tk.Frame(tf,bg=CARD if i%2==0 else BG3); row.pack(fill="x")
            tk.Label(row,text=lbl,font=(FONT,9),fg=TEXT3,bg=row.cget("bg"),padx=10,pady=7,width=28,anchor="w").pack(side="left")
            v=tk.Label(row,text="--",font=(FONT,9,"bold"),fg=TEXT1,bg=row.cget("bg"),padx=10); v.pack(side="right")
            self._tbl.append(v)

    def _upd_combined(self):
        try: n=int(self.v_nhd.get()); tam=float(self.v_thd.get().replace(" TB",""))
        except: return
        raid=self.v_raid.get()
        try: hs=int(self.v_hs.get())
        except: hs=0
        if raid not in RAID_DATA: return
        _,_,min_d,calc=RAID_DATA[raid]
        dr=max(n-hs,1) if hs>0 else n
        util_tb=calc(dr,tam) if dr>=min_d else 0
        try:
            ncam=int(self.v_ncam.get()); res=RES_MAP.get(self.v_res.get(),2)
            comp=COMP_MAP.get(self.v_comp.get(),0.5); fps=int(self.v_fps.get().replace(" fps",""))
            dias=int(self.v_dias.get()); horas=int(self.v_horas.get())
            auto=self.v_bitmode.get()=="Automatico"
            br=BR_BASE.get(res,2048)*comp*(fps/15) if auto else float(self.v_bitrate.get())
            cam_tb=(br*3600*horas*ncam*dias)/(8*1024*1024*1024)
        except: return
        livre=util_tb-cam_tb; pct=min((cam_tb/util_tb)*100,100) if util_tb>0 else 0
        self.mc_xr.set(fmt(util_tb),"volume RAID disponivel",BLUE2)
        self.mc_xc.set(fmt(cam_tb),"necessario para cameras",AMBER)
        if livre>=0:
            self.mc_xl.set(f"+{fmt(livre)}","espaco livre restante",GREEN)
            self.lbl_vi.config(text="")
            self.lbl_vt.config(text=f"Storage suficiente - {fmt(livre)} de margem disponivel",fg=GREEN)
            self.lbl_vs.config(text=f"O array RAID fornece {fmt(util_tb)} e as cameras precisam de {fmt(cam_tb)}. Utilizacao de {pct:.1f}% do armazenamento disponivel.")
        else:
            self.mc_xl.set(f"-{fmt(abs(livre))}","deficit de armazenamento",ACCENT)
            self.lbl_vi.config(text="")
            self.lbl_vt.config(text=f"Storage insuficiente - deficit de {fmt(abs(livre))}",fg=ACCENT)
            self.lbl_vs.config(text=f"O RAID tem apenas {fmt(util_tb)}, mas as cameras exigem {fmt(cam_tb)}. Considere mais HDs, maior capacidade ou reducao de cameras/retencao.")
        self.pb_comb.set(pct)
        col=GREEN if pct<70 else AMBER if pct<90 else ACCENT
        self.lbl_gpct.config(text=f"{pct:.1f}%",fg=col)
        vals=[raid,fmt(util_tb),f"{ncam} cameras",fmt(cam_tb),
              f"+{fmt(livre)}" if livre>=0 else f"-{fmt(abs(livre))}",f"{pct:.1f}%"]
        cols=[TEXT1,BLUE2,TEXT1,AMBER,GREEN if livre>=0 else ACCENT,col]
        for lb,v,c in zip(self._tbl,vals,cols): lb.config(text=v,fg=c)

    def _footer(self):
        Divider(self).pack(fill="x",side="bottom")
        ft=tk.Frame(self,bg=BG2,height=32); ft.pack(fill="x",side="bottom"); ft.pack_propagate(False)
        tk.Label(ft,text="Intelbras Storage Calculator  |  Valores estimados para dimensionamento tecnico",
                 font=(FONT,8),fg=TEXT3,bg=BG2).pack(side="left",padx=20,pady=8)
        tk.Label(ft,text="2025 Intelbras  |  v2.0",font=(FONT,8),fg=TEXT3,bg=BG2).pack(side="right",padx=20)

if __name__=="__main__":
    app=App(); app.mainloop()
