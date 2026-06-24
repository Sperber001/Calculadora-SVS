import customtkinter as ctk
import math
import tkinter as tk

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

# Cores oficiais Intelbras adaptadas para tema escuro
GREEN_PRIMARY = "#00A335"
GREEN_DARK    = "#00863F"
GREEN_DARKER  = "#005C2B"
GREEN_SUBTLE  = "#003D1D"
BG_DARK       = "#0D1410"
BG_PANEL      = "#111A14"
BG_CARD       = "#172014"
BG_FIELD      = "#1E2B1A"
BG_HOVER      = "#243320"
BORDER        = "#2A4030"
TEXT1         = "#EDF5EE"
TEXT2         = "#8FB898"
TEXT3         = "#4A6B52"
WHITE         = "#FFFFFF"
AMBER         = "#F59E0B"
RED           = "#E53935"
FONT          = "Segoe UI"

RAID_DATA = {
    "RAID 0":  ("Striping sem redundancia",     "Sem protecao. Se 1 HD falhar, perde tudo.",                   1, lambda d,t: d*t),
    "RAID 1":  ("Mirroring espelho total",       "Tolera falha de metade dos discos. Min. 2 HDs.",              2, lambda d,t: math.floor(d/2)*t),
    "RAID 5":  ("Paridade simples distribuida",  "Tolera falha de 1 disco. 1 HD para paridade. Min. 3 HDs.",   3, lambda d,t: (d-1)*t),
    "RAID 6":  ("Dupla paridade distribuida",    "Tolera falha de 2 discos. 2 HDs para paridade. Min. 4 HDs.",4, lambda d,t: (d-2)*t),
    "RAID 10": ("Mirror + Stripe combinados",    "Alta performance e redundancia. Min. 4 HDs par.",             4, lambda d,t: (d//2)*t),
    "JBOD":    ("Discos independentes sem RAID", "Sem redundancia. Capacidade total de todos os HDs.",          1, lambda d,t: d*t),
}
TB_SIZES = [0.5,1,2,3,4,6,8,10,12,14,16,18,20]
RES_MAP  = {"D1/CIF-0.5MP":0.5,"720p HD-1MP":1,"1080p FullHD-2MP":2,"4MP":4,"3K/5MP":5,"4K UHD-8MP":8,"12MP":12}
COMP_MAP = {"H.265/H.265+":0.5,"H.264":1.0,"MJPEG":1.5}
BR_BASE  = {0.5:512,1:1024,2:2048,4:4096,5:5120,8:8192,12:12288}

def fmt(v, unit="TB"):
    if unit=="TB":
        if v>=1000: return f"{v/1000:.1f} PB"
        if v>=1:    return f"{v:.2f} TB"
        return f"{v*1024:.0f} GB"
    if v>=1024: return f"{v/1024:.2f} TB"
    return f"{v:.1f} GB"

class MetricCard(ctk.CTkFrame):
    def __init__(self, p, label, **kw):
        super().__init__(p, fg_color=BG_FIELD, corner_radius=10, border_width=1, border_color=BORDER, **kw)
        ctk.CTkLabel(self, text=label, font=(FONT,11), text_color=TEXT2).pack(anchor="w", padx=14, pady=(12,2))
        self.val = ctk.CTkLabel(self, text="--", font=(FONT,22,"bold"), text_color=TEXT1)
        self.val.pack(anchor="w", padx=14)
        self.sub = ctk.CTkLabel(self, text="", font=(FONT,10), text_color=TEXT3)
        self.sub.pack(anchor="w", padx=14, pady=(0,12))
    def set(self, v, s="", c=TEXT1):
        self.val.configure(text=v, text_color=c)
        self.sub.configure(text=s)

class InfoBox(ctk.CTkFrame):
    def __init__(self, p, **kw):
        super().__init__(p, fg_color=BG_FIELD, corner_radius=8, border_width=1, border_color=BORDER, **kw)
        self.lbl = ctk.CTkLabel(self, text="", font=(FONT,10), text_color=TEXT2, wraplength=420, justify="left")
        self.lbl.pack(anchor="w", padx=12, pady=10)
    def set(self, t, c=TEXT2): self.lbl.configure(text=t, text_color=c)

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Intelbras Storage Calculator")
        self.configure(fg_color=BG_DARK)
        self.minsize(1000, 680)
        try: self.state("zoomed")
        except: self.geometry("1000x700")
        self._active = ""
        self._panels = {}
        self._header()
        self._layout()
        self._sidebar()
        self._raid_panel()
        self._cam_panel()
        self._combined_panel()
        self._footer()
        self._show("raid")
        self.after(150, lambda: (self._calc_raid(), self._calc_cam()))

    def _header(self):
        h = ctk.CTkFrame(self, fg_color=BG_PANEL, corner_radius=0, height=64)
        h.pack(fill="x"); h.pack_propagate(False)
        left = ctk.CTkFrame(h, fg_color="transparent"); left.pack(side="left", padx=20, pady=12)
        logo = ctk.CTkFrame(left, fg_color=GREEN_PRIMARY, width=40, height=40, corner_radius=8)
        logo.pack(side="left"); logo.pack_propagate(False)
        ctk.CTkLabel(logo, text="I", font=(FONT,20,"bold"), text_color=WHITE).place(relx=.5, rely=.5, anchor="center")
        info = ctk.CTkFrame(left, fg_color="transparent"); info.pack(side="left", padx=12)
        ctk.CTkLabel(info, text="INTELBRAS", font=(FONT,14,"bold"), text_color=WHITE).pack(anchor="w")
        ctk.CTkLabel(info, text="Storage & CFTV Calculator", font=(FONT,10), text_color=TEXT2).pack(anchor="w")
        right = ctk.CTkFrame(h, fg_color="transparent"); right.pack(side="right", padx=20)
        badge = ctk.CTkFrame(right, fg_color=GREEN_DARKER, corner_radius=20, border_width=1, border_color=GREEN_DARK)
        badge.pack()
        ctk.CTkLabel(badge, text="  v3.0  PRO  ", font=(FONT,10,"bold"), text_color=GREEN_PRIMARY).pack(padx=4, pady=4)
        ctk.CTkFrame(self, fg_color=GREEN_DARKER, height=2, corner_radius=0).pack(fill="x")

    def _layout(self):
        self.body = ctk.CTkFrame(self, fg_color="transparent"); self.body.pack(fill="both", expand=True)

    def _sidebar(self):
        self.sb = ctk.CTkFrame(self.body, fg_color=BG_PANEL, width=220, corner_radius=0)
        self.sb.pack(side="left", fill="y"); self.sb.pack_propagate(False)
        ctk.CTkFrame(self.sb, fg_color=BORDER, height=1, corner_radius=0).pack(fill="x")
        ctk.CTkLabel(self.sb, text="FERRAMENTAS", font=(FONT,9,"bold"), text_color=TEXT3).pack(anchor="w", padx=16, pady=(20,8))
        self._nav_ws = {}
        for key,icon,label in [("raid","💾","Calculadora RAID"),("cameras","📹","Cameras & Gravacao"),("combinado","📊","Analise Combinada")]:
            self._nav_ws[key] = self._nav_btn(key, icon, label)
        ctk.CTkFrame(self.sb, fg_color=BORDER, height=1, corner_radius=0).pack(fill="x", pady=16)
        tip = ctk.CTkFrame(self.sb, fg_color=BG_CARD, corner_radius=8, border_width=1, border_color=BORDER)
        tip.pack(fill="x", padx=12)
        ctk.CTkLabel(tip, text="Dica rapida", font=(FONT,10,"bold"), text_color=GREEN_PRIMARY).pack(anchor="w", padx=12, pady=(10,2))
        ctk.CTkLabel(tip, text="Configure o RAID\ne depois as cameras\npara ver a analise\ncombinada.",
                     font=(FONT,9), text_color=TEXT2, justify="left").pack(anchor="w", padx=12, pady=(0,10))
        ctk.CTkFrame(self.sb, fg_color=BORDER, height=1, corner_radius=0).pack(fill="x", side="bottom")
        self.content = ctk.CTkFrame(self.body, fg_color=BG_DARK, corner_radius=0)
        self.content.pack(side="left", fill="both", expand=True)

    def _nav_btn(self, key, icon, label):
        fr = ctk.CTkFrame(self.sb, fg_color="transparent", cursor="hand2", corner_radius=0); fr.pack(fill="x")
        ind = ctk.CTkFrame(fr, fg_color="transparent", width=3, corner_radius=0); ind.pack(side="left", fill="y")
        inn = ctk.CTkFrame(fr, fg_color="transparent"); inn.pack(side="left", fill="both", expand=True, padx=12, pady=10)
        ic = ctk.CTkLabel(inn, text=icon, font=(FONT,15), text_color=TEXT2); ic.pack(side="left")
        tx = ctk.CTkLabel(inn, text=label, font=(FONT,11), text_color=TEXT2); tx.pack(side="left", padx=10)
        def enter(_):
            if self._active!=key: fr.configure(fg_color=BG_HOVER); inn.configure(fg_color=BG_HOVER)
        def leave(_):
            if self._active!=key: fr.configure(fg_color="transparent"); inn.configure(fg_color="transparent")
        def click(_): self._show(key)
        for w in (fr,inn,ic,tx,ind): w.bind("<Enter>",enter); w.bind("<Leave>",leave); w.bind("<Button-1>",click)
        return {"fr":fr,"inn":inn,"ind":ind,"ic":ic,"tx":tx}

    def _show(self, key):
        self._active = key
        for k,w in self._nav_ws.items():
            on=k==key; bg=BG_HOVER if on else "transparent"
            w["fr"].configure(fg_color=bg); w["inn"].configure(fg_color=bg)
            w["ind"].configure(fg_color=GREEN_PRIMARY if on else "transparent")
            w["ic"].configure(text_color=WHITE if on else TEXT2)
            w["tx"].configure(text_color=TEXT1 if on else TEXT2, font=(FONT,11,"bold" if on else "normal"))
        for k,p in self._panels.items():
            if k==key: p.pack(fill="both", expand=True, padx=24, pady=16)
            else: p.pack_forget()

    def _card(self, p, title=None):
        c = ctk.CTkFrame(p, fg_color=BG_CARD, corner_radius=12, border_width=1, border_color=BORDER)
        if title:
            ctk.CTkLabel(c, text=title, font=(FONT,12,"bold"), text_color=TEXT1).pack(anchor="w", padx=18, pady=(14,10))
            ctk.CTkFrame(c, fg_color=BORDER, height=1, corner_radius=0).pack(fill="x")
        return c

    def _fl(self, p, label):
        f = ctk.CTkFrame(p, fg_color="transparent"); f.pack(fill="x", pady=5)
        ctk.CTkLabel(f, text=label, font=(FONT,9,"bold"), text_color=TEXT3).pack(anchor="w", pady=(0,5))
        return f

    def _combo(self, p, var, values, cmd=None, **kw):
        cb = ctk.CTkComboBox(p, variable=var, values=values,
                             command=lambda _: cmd() if cmd else None,
                             fg_color=BG_FIELD, border_color=BORDER,
                             button_color=GREEN_DARKER, button_hover_color=GREEN_DARK,
                             dropdown_fg_color=BG_CARD, dropdown_hover_color=GREEN_DARKER,
                             text_color=TEXT1, font=(FONT,11), **kw)
        return cb

    def _entry(self, p, var, **kw):
        return ctk.CTkEntry(p, textvariable=var, fg_color=BG_FIELD, border_color=BORDER,
                            text_color=TEXT1, font=(FONT,11), height=32, **kw)

    def _qbtns(self, p, values, var, cmd):
        row = ctk.CTkFrame(p, fg_color="transparent"); row.pack(fill="x", pady=(0,4))
        btns = []
        def make(v):
            def c():
                var.set(v)
                for b2,v2 in btns:
                    sel=v2==var.get()
                    b2.configure(fg_color=GREEN_PRIMARY if sel else BG_FIELD,
                                text_color=WHITE if sel else TEXT2,
                                border_width=0 if sel else 1)
                cmd()
            return c
        for v in values:
            lbl = "Nenhum" if v=="Nenhum" else str(v)
            b = ctk.CTkButton(row, text=lbl, command=make(v),
                             fg_color=BG_FIELD, hover_color=BG_HOVER, text_color=TEXT2,
                             corner_radius=6, height=30, font=(FONT,11),
                             border_width=1, border_color=BORDER)
            b.pack(side="left", padx=(0,4))
            btns.append((b,v))
        return row, btns

    def _upd_q(self, btns, cur):
        for b,v in btns:
            sel=v==cur
            b.configure(fg_color=GREEN_PRIMARY if sel else BG_FIELD,
                       text_color=WHITE if sel else TEXT2, border_width=0 if sel else 1)

    # ──────────────────────────────────────────── RAID ──────────────────────
    def _raid_panel(self):
        p = ctk.CTkScrollableFrame(self.content, fg_color="transparent", scrollbar_button_color=BORDER)
        self._panels["raid"] = p
        ctk.CTkLabel(p, text="Calculadora RAID", font=(FONT,16,"bold"), text_color=TEXT1).pack(anchor="w")
        ctk.CTkLabel(p, text="Configure os discos e o tipo de array para calcular o volume disponivel",
                     font=(FONT,10), text_color=TEXT2).pack(anchor="w", pady=(2,16))

        body = ctk.CTkFrame(p, fg_color="transparent"); body.pack(fill="both", expand=True)
        body.columnconfigure(0,weight=2); body.columnconfigure(1,weight=3); body.rowconfigure(0,weight=1)

        left = self._card(body,"Configuracao dos Discos"); left.grid(row=0,column=0,sticky="nsew",padx=(0,12))
        frm = ctk.CTkFrame(left,fg_color="transparent"); frm.pack(fill="x",padx=18,pady=12)

        ff=self._fl(frm,"NUMERO DE HDs")
        self.v_nhd=tk.IntVar(value=4); self.v_nhd.trace_add("write",lambda *_:self._calc_raid())
        _,self._nhd_q=self._qbtns(ff,[2,4,8,12,16,24],self.v_nhd,self._calc_raid)
        cust=ctk.CTkFrame(ff,fg_color="transparent"); cust.pack(fill="x",pady=(4,0))
        ctk.CTkLabel(cust,text="Personalizado:",font=(FONT,10),text_color=TEXT3).pack(side="left")
        self._entry(cust,self.v_nhd,width=70).pack(side="left",padx=8)

        ff2=self._fl(frm,"CAPACIDADE POR HD")
        self.v_thd=tk.StringVar(value="4 TB"); self.v_thd.trace_add("write",lambda *_:self._calc_raid())
        self._combo(ff2,self.v_thd,[f"{v} TB" for v in TB_SIZES],cmd=self._calc_raid,width=260).pack(fill="x")

        ff3=self._fl(frm,"TIPO DE RAID")
        self.v_raid=tk.StringVar(value="RAID 5"); self._rbw={}
        rg=ctk.CTkFrame(ff3,fg_color="transparent"); rg.pack(fill="x")
        for i,r in enumerate(["RAID 0","RAID 1","RAID 5","RAID 6","RAID 10","JBOD"]):
            def mc(rv=r):
                def c(): self.v_raid.set(rv); self._upd_rbw(); self._calc_raid()
                return c
            sel=r=="RAID 5"
            b=ctk.CTkButton(rg,text=r,command=mc(),
                           fg_color=GREEN_PRIMARY if sel else BG_FIELD,
                           hover_color=GREEN_DARK,text_color=WHITE if sel else TEXT2,
                           corner_radius=6,height=34,font=(FONT,11,"bold"),
                           border_width=0 if sel else 1,border_color=BORDER)
            b.grid(row=i//3,column=i%3,padx=(0,6),pady=(0,6),sticky="ew"); rg.columnconfigure(i%3,weight=1)
            self._rbw[r]=b
        self.lbl_rdesc=ctk.CTkLabel(frm,text="Tolera falha de 1 disco. Min. 3 HDs.",
                                    font=(FONT,10),text_color=TEXT2,wraplength=300,justify="left")
        self.lbl_rdesc.pack(anchor="w",pady=(4,0))

        ff4=self._fl(frm,"HOT SPARE")
        self.v_hs=tk.IntVar(value=0); self.v_hs.trace_add("write",lambda *_:self._calc_raid())
        self._hs_btns=[]
        hs_row=ctk.CTkFrame(ff4,fg_color="transparent"); hs_row.pack(fill="x")
        for v in [0,1,2,3]:
            lbl="Nenhum" if v==0 else f"{v} HD{'s' if v>1 else ''}"
            def mhs(x=v):
                def c(): self.v_hs.set(x); self._upd_hs(); self._calc_raid()
                return c
            sel=v==0
            b=ctk.CTkButton(hs_row,text=lbl,command=mhs(),
                           fg_color=GREEN_DARKER if sel else BG_FIELD,
                           hover_color=GREEN_DARK,text_color=TEXT1 if sel else TEXT2,
                           corner_radius=6,height=30,font=(FONT,10),
                           border_width=1,border_color=GREEN_DARK if sel else BORDER)
            b.pack(side="left",padx=(0,4)); self._hs_btns.append((b,v))
        ch=ctk.CTkFrame(ff4,fg_color="transparent"); ch.pack(fill="x",pady=(6,0))
        ctk.CTkLabel(ch,text="Personalizado:",font=(FONT,10),text_color=TEXT3).pack(side="left")
        self._entry(ch,self.v_hs,width=60).pack(side="left",padx=8)
        self.lbl_hs=ctk.CTkLabel(ff4,text="Sem disco de reserva configurado.",font=(FONT,9),text_color=TEXT3)
        self.lbl_hs.pack(anchor="w",pady=(4,0))

        self._upd_nhd(); self._upd_rbw(); self._upd_hs()

        right=ctk.CTkFrame(body,fg_color="transparent"); right.grid(row=0,column=1,sticky="nsew")
        ctk.CTkLabel(right,text="Resultado do Array",font=(FONT,12,"bold"),text_color=TEXT1).pack(anchor="w",pady=(0,10))
        g=ctk.CTkFrame(right,fg_color="transparent"); g.pack(fill="x",pady=(0,10))
        g.columnconfigure(0,weight=1); g.columnconfigure(1,weight=1)
        self.mc_rd=MetricCard(g,"HDs no Array"); self.mc_rd.grid(row=0,column=0,sticky="ew",padx=(0,8),pady=(0,8))
        self.mc_rb=MetricCard(g,"Capacidade Bruta"); self.mc_rb.grid(row=0,column=1,sticky="ew",pady=(0,8))
        self.mc_ru=MetricCard(g,"Volume Disponivel"); self.mc_ru.grid(row=1,column=0,sticky="ew",padx=(0,8))
        self.mc_re=MetricCard(g,"Eficiencia de Uso"); self.mc_re.grid(row=1,column=1,sticky="ew")

        pc=self._card(right); pc.pack(fill="x",pady=(10,0))
        pt=ctk.CTkFrame(pc,fg_color="transparent"); pt.pack(fill="x",padx=16,pady=(14,6))
        ctk.CTkLabel(pt,text="Aproveitamento do storage",font=(FONT,10,"bold"),text_color=TEXT2).pack(side="left")
        self.lbl_pct_r=ctk.CTkLabel(pt,text="",font=(FONT,10,"bold"),text_color=GREEN_PRIMARY); self.lbl_pct_r.pack(side="right")
        self.pb_raid=ctk.CTkProgressBar(pc,fg_color=BG_FIELD,progress_color=GREEN_PRIMARY,height=10,corner_radius=5)
        self.pb_raid.pack(fill="x",padx=16,pady=(0,6)); self.pb_raid.set(0)
        self.lbl_bar_r=ctk.CTkLabel(pc,text="",font=(FONT,9),text_color=TEXT3); self.lbl_bar_r.pack(anchor="w",padx=16,pady=(0,12))
        self.info_r=InfoBox(right); self.info_r.pack(fill="x",pady=(10,0))

    def _upd_nhd(self):
        try: cur=int(self.v_nhd.get())
        except: return
        self._upd_q(self._nhd_q, cur)

    def _upd_rbw(self):
        cur=self.v_raid.get()
        for r,b in self._rbw.items():
            sel=r==cur
            b.configure(fg_color=GREEN_PRIMARY if sel else BG_FIELD,
                       text_color=WHITE if sel else TEXT2,border_width=0 if sel else 1)

    def _upd_hs(self):
        try: cur=int(self.v_hs.get())
        except: cur=0
        for b,v in self._hs_btns:
            sel=v==cur
            b.configure(fg_color=GREEN_PRIMARY if sel else BG_FIELD,
                       text_color=WHITE if sel else TEXT2,
                       border_color=GREEN_DARK if sel else BORDER)
        if cur==0: self.lbl_hs.configure(text="Sem disco de reserva configurado.",text_color=TEXT3)
        elif cur==1: self.lbl_hs.configure(text="1 HD reservado em standby para substituicao automatica.",text_color=GREEN_PRIMARY)
        else: self.lbl_hs.configure(text=f"{cur} HDs reservados em standby para substituicao automatica.",text_color=GREEN_PRIMARY)

    def _calc_raid(self, *_):
        try: n=int(self.v_nhd.get()); tam=float(self.v_thd.get().replace(" TB","")); hs=int(self.v_hs.get())
        except: return
        self._upd_nhd(); self._upd_hs()
        raid=self.v_raid.get()
        if raid not in RAID_DATA: return
        sub,desc,min_d,calc=RAID_DATA[raid]
        self.lbl_rdesc.configure(text=f"  {desc}")
        dr=max(n-hs,1) if hs>0 else n; bruto=dr*tam
        if dr<min_d and raid not in ("JBOD","RAID 0"):
            err=f"  {raid} requer minimo {min_d} HDs ativos. Reduza hot spares ou adicione HDs."
            self.mc_rd.set(str(dr),"discos ativos"); self.mc_rb.set(fmt(n*tam),f"{n*tam:.1f} TB total")
            self.mc_ru.set("--",err,RED); self.mc_re.set("--","",TEXT3)
            self.pb_raid.set(0); self.lbl_pct_r.configure(text="0%",text_color=RED)
            self.lbl_bar_r.configure(text=err); self.info_r.set(err,RED)
            self._upd_combined(); return
        try: util=calc(dr,tam)
        except: util=0
        efic=round((util/bruto)*100) if bruto>0 else 0
        col=GREEN_PRIMARY if efic>=75 else AMBER if efic>=50 else RED
        self.mc_rd.set(str(dr),"discos ativos no array")
        self.mc_rb.set(fmt(n*tam),f"{n*tam:.1f} TB ({n} HDs)")
        self.mc_ru.set(fmt(util),f"{util:.2f} TB disponiveis",GREEN_PRIMARY)
        self.mc_re.set(f"{efic}%","do espaco aproveitado",col)
        self.pb_raid.set(efic/100); self.pb_raid.configure(progress_color=col)
        self.lbl_pct_r.configure(text=f"{efic}%",text_color=col)
        hs_t=f"  |  {hs} HS={hs*tam:.1f}TB reservados" if hs>0 else ""
        self.lbl_bar_r.configure(text=f"{dr} HDs x {tam} TB  |  {raid}{hs_t}")
        self.info_r.set(f"Util: {fmt(util)}   |   Overhead: {fmt(bruto-util)}   |   Hot Spare: {hs} HD(s)   |   Eficiencia: {efic}%",TEXT2)
        self._upd_combined()

    # ──────────────────────────────────────────── CAMERAS ───────────────────
    def _cam_panel(self):
        p=ctk.CTkScrollableFrame(self.content,fg_color="transparent",scrollbar_button_color=BORDER)
        self._panels["cameras"]=p
        ctk.CTkLabel(p,text="Cameras & Gravacao",font=(FONT,16,"bold"),text_color=TEXT1).pack(anchor="w")
        ctk.CTkLabel(p,text="Calcule o armazenamento necessario para o seu sistema de CFTV",
                     font=(FONT,10),text_color=TEXT2).pack(anchor="w",pady=(2,16))

        body=ctk.CTkFrame(p,fg_color="transparent"); body.pack(fill="both",expand=True)
        body.columnconfigure(0,weight=2); body.columnconfigure(1,weight=3); body.rowconfigure(0,weight=1)

        left=self._card(body,"Parametros de Gravacao"); left.grid(row=0,column=0,sticky="nsew",padx=(0,12))
        frm=ctk.CTkFrame(left,fg_color="transparent"); frm.pack(fill="x",padx=18,pady=12)

        ff=self._fl(frm,"NUMERO DE CAMERAS")
        self.v_ncam=tk.IntVar(value=8); self.v_ncam.trace_add("write",lambda *_:self._calc_cam())
        _,self._cam_q=self._qbtns(ff,[4,8,16,32,64],self.v_ncam,self._calc_cam)
        cust=ctk.CTkFrame(ff,fg_color="transparent"); cust.pack(fill="x",pady=(4,0))
        ctk.CTkLabel(cust,text="Personalizado:",font=(FONT,10),text_color=TEXT3).pack(side="left")
        self._entry(cust,self.v_ncam,width=70).pack(side="left",padx=8)

        ff2=self._fl(frm,"RESOLUCAO")
        self.v_res=tk.StringVar(value="1080p FullHD-2MP")
        self._combo(ff2,self.v_res,list(RES_MAP.keys()),cmd=self._calc_cam,width=260).pack(fill="x")

        r2=ctk.CTkFrame(frm,fg_color="transparent"); r2.pack(fill="x")
        c1=ctk.CTkFrame(r2,fg_color="transparent"); c1.pack(side="left",expand=True,fill="x",padx=(0,8))
        ctk.CTkLabel(c1,text="COMPRESSAO",font=(FONT,9,"bold"),text_color=TEXT3).pack(anchor="w",pady=(5,5))
        self.v_comp=tk.StringVar(value="H.265/H.265+")
        self._combo(c1,self.v_comp,list(COMP_MAP.keys()),cmd=self._calc_cam,width=120).pack(fill="x")
        c2=ctk.CTkFrame(r2,fg_color="transparent"); c2.pack(side="left",expand=True,fill="x")
        ctk.CTkLabel(c2,text="FPS",font=(FONT,9,"bold"),text_color=TEXT3).pack(anchor="w",pady=(5,5))
        self.v_fps=tk.StringVar(value="15 fps")
        self._combo(c2,self.v_fps,["1 fps","5 fps","10 fps","15 fps","20 fps","25 fps","30 fps"],cmd=self._calc_cam,width=100).pack(fill="x")

        ff3=self._fl(frm,"MODO DE BITRATE")
        self.v_bitmode=tk.StringVar(value="Automatico")
        self._combo(ff3,self.v_bitmode,["Automatico","Manual (Kbps)"],cmd=self._calc_cam,width=260).pack(fill="x")

        self.ff_m=ctk.CTkFrame(frm,fg_color="transparent"); self.ff_m.pack(fill="x",pady=(4,0))
        ctk.CTkLabel(self.ff_m,text="BITRATE POR CAMERA (KBPS)",font=(FONT,9,"bold"),text_color=TEXT3).pack(anchor="w",pady=(5,5))
        self.v_bitrate=tk.IntVar(value=2048); self.v_bitrate.trace_add("write",lambda *_:self._calc_cam())
        self.entry_bit=self._entry(self.ff_m,self.v_bitrate,width=260); self.entry_bit.pack(fill="x")

        r3=ctk.CTkFrame(frm,fg_color="transparent"); r3.pack(fill="x",pady=(10,0))
        d1=ctk.CTkFrame(r3,fg_color="transparent"); d1.pack(side="left",expand=True,fill="x",padx=(0,8))
        ctk.CTkLabel(d1,text="DIAS DE RETENCAO",font=(FONT,9,"bold"),text_color=TEXT3).pack(anchor="w",pady=(5,5))
        self.v_dias=tk.IntVar(value=30); self.v_dias.trace_add("write",lambda *_:self._calc_cam())
        self._entry(d1,self.v_dias).pack(fill="x")
        d2=ctk.CTkFrame(r3,fg_color="transparent"); d2.pack(side="left",expand=True,fill="x")
        ctk.CTkLabel(d2,text="HORAS/DIA",font=(FONT,9,"bold"),text_color=TEXT3).pack(anchor="w",pady=(5,5))
        self.v_horas=tk.IntVar(value=24); self.v_horas.trace_add("write",lambda *_:self._calc_cam())
        self._entry(d2,self.v_horas).pack(fill="x")

        self._upd_cam()

        right=ctk.CTkFrame(body,fg_color="transparent"); right.grid(row=0,column=1,sticky="nsew")
        ctk.CTkLabel(right,text="Resultado",font=(FONT,12,"bold"),text_color=TEXT1).pack(anchor="w",pady=(0,10))
        g=ctk.CTkFrame(right,fg_color="transparent"); g.pack(fill="x",pady=(0,10))
        g.columnconfigure(0,weight=1); g.columnconfigure(1,weight=1)
        self.mc_cbt=MetricCard(g,"Bitrate Total"); self.mc_cbt.grid(row=0,column=0,sticky="ew",padx=(0,8),pady=(0,8))
        self.mc_cpd=MetricCard(g,"Por camera / dia"); self.mc_cpd.grid(row=0,column=1,sticky="ew",pady=(0,8))
        self.mc_cst=MetricCard(g,"Total Necessario"); self.mc_cst.grid(row=1,column=0,sticky="ew",padx=(0,8))
        self.mc_cd1=MetricCard(g,"Dias com 1 TB"); self.mc_cd1.grid(row=1,column=1,sticky="ew")
        self.cam_sum=InfoBox(right); self.cam_sum.lbl.configure(wraplength=440); self.cam_sum.pack(fill="x",pady=(10,0))

    def _upd_cam(self):
        try: cur=int(self.v_ncam.get())
        except: return
        self._upd_q(self._cam_q,cur)

    def _calc_cam(self,*_):
        try:
            ncam=int(self.v_ncam.get()); res=RES_MAP.get(self.v_res.get(),2)
            comp=COMP_MAP.get(self.v_comp.get(),0.5); fps=int(self.v_fps.get().replace(" fps",""))
            dias=int(self.v_dias.get()); horas=int(self.v_horas.get())
            auto=self.v_bitmode.get()=="Automatico"
        except: return
        self._upd_cam()
        if auto: br=BR_BASE.get(res,2048)*comp*(fps/15); self.entry_bit.configure(state="disabled",fg_color=BG_HOVER)
        else: br=float(self.v_bitrate.get()); self.entry_bit.configure(state="normal",fg_color=BG_FIELD)
        mbps=(br*ncam)/1000; gb_cam=(br*3600*horas)/(8*1024*1024)
        total_tb=(gb_cam*ncam*dias)/1024; d1tb=(1024/(gb_cam*ncam)) if gb_cam*ncam>0 else 0
        self.mc_cbt.set(f"{mbps:.1f} Mbps",f"{br:.0f} Kbps por camera",GREEN_PRIMARY)
        self.mc_cpd.set(fmt(gb_cam,"GB"),"por camera por dia",TEXT1)
        self.mc_cst.set(fmt(total_tb),f"{ncam} cam. x {dias} dias x {horas}h",AMBER)
        self.mc_cd1.set(f"{d1tb:.1f} dias","de gravacao por 1 TB",GREEN_PRIMARY)
        self.cam_sum.set(
            f"  {ncam} camera{'s' if ncam>1 else ''}  |  {self.v_res.get()}  |  {self.v_comp.get()}  |  {fps} fps\n"
            f"  Retencao: {dias} dias x {horas}h/dia  |  Bitrate: {br:.0f} Kbps/camera\n"
            f"  Armazenamento total necessario: {fmt(total_tb)}")
        self._upd_combined()

    # ──────────────────────────────────────────── COMBINED ──────────────────
    def _combined_panel(self):
        p=ctk.CTkScrollableFrame(self.content,fg_color="transparent",scrollbar_button_color=BORDER)
        self._panels["combinado"]=p
        ctk.CTkLabel(p,text="Analise Combinada",font=(FONT,16,"bold"),text_color=TEXT1).pack(anchor="w")
        ctk.CTkLabel(p,text="Comparacao entre volume disponivel no RAID e o necessario pelas cameras",
                     font=(FONT,10),text_color=TEXT2).pack(anchor="w",pady=(2,16))

        top=ctk.CTkFrame(p,fg_color="transparent"); top.pack(fill="x",pady=(0,12))
        top.columnconfigure(0,weight=1); top.columnconfigure(1,weight=1); top.columnconfigure(2,weight=1)
        self.mc_xr=MetricCard(top,"Disponivel no RAID"); self.mc_xr.grid(row=0,column=0,sticky="ew",padx=(0,8))
        self.mc_xc=MetricCard(top,"Necessario pelas Cameras"); self.mc_xc.grid(row=0,column=1,sticky="ew",padx=(0,8))
        self.mc_xl=MetricCard(top,"Saldo / Deficit"); self.mc_xl.grid(row=0,column=2,sticky="ew")

        vc=self._card(p); vc.pack(fill="x",pady=(0,12))
        vr=ctk.CTkFrame(vc,fg_color="transparent"); vr.pack(fill="x",padx=18,pady=16)
        self.lbl_vi=ctk.CTkLabel(vr,text="",font=(FONT,26)); self.lbl_vi.pack(side="left")
        vt=ctk.CTkFrame(vr,fg_color="transparent"); vt.pack(side="left",padx=12)
        self.lbl_vt=ctk.CTkLabel(vt,text="Configure o RAID e as cameras para ver a analise",
                                  font=(FONT,12,"bold"),text_color=TEXT2); self.lbl_vt.pack(anchor="w")
        self.lbl_vs=ctk.CTkLabel(vt,text="",font=(FONT,10),text_color=TEXT2,wraplength=600,justify="left")
        self.lbl_vs.pack(anchor="w",pady=(4,0))

        gc=self._card(p); gc.pack(fill="x",pady=(0,12))
        gt=ctk.CTkFrame(gc,fg_color="transparent"); gt.pack(fill="x",padx=16,pady=(14,8))
        ctk.CTkLabel(gt,text="Utilizacao do storage RAID",font=(FONT,10,"bold"),text_color=TEXT2).pack(side="left")
        self.lbl_gpct=ctk.CTkLabel(gt,text="0%",font=(FONT,11,"bold"),text_color=GREEN_PRIMARY); self.lbl_gpct.pack(side="right")
        self.pb_comb=ctk.CTkProgressBar(gc,fg_color=BG_FIELD,progress_color=GREEN_PRIMARY,height=10,corner_radius=5)
        self.pb_comb.pack(fill="x",padx=16,pady=(0,16)); self.pb_comb.set(0)

        tc=self._card(p,"Resumo Tecnico"); tc.pack(fill="x")
        tf=ctk.CTkFrame(tc,fg_color="transparent"); tf.pack(fill="x",padx=18,pady=10)
        self._tbl=[]
        for i,lbl in enumerate(["RAID configurado","Volume RAID disponivel","Numero de cameras","Armazenamento necessario","Saldo de espaco","Taxa de utilizacao"]):
            row=ctk.CTkFrame(tf,fg_color=BG_FIELD if i%2==0 else "transparent",corner_radius=4); row.pack(fill="x",pady=1)
            ctk.CTkLabel(row,text=lbl,font=(FONT,10),text_color=TEXT3,width=220,anchor="w").pack(side="left",padx=10,pady=7)
            v=ctk.CTkLabel(row,text="--",font=(FONT,10,"bold"),text_color=TEXT1); v.pack(side="right",padx=10)
            self._tbl.append(v)

    def _upd_combined(self):
        try: n=int(self.v_nhd.get()); tam=float(self.v_thd.get().replace(" TB","")); hs=int(self.v_hs.get())
        except: return
        raid=self.v_raid.get()
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
        col=GREEN_PRIMARY if pct<70 else AMBER if pct<90 else RED
        self.mc_xr.set(fmt(util_tb),"volume RAID disponivel",GREEN_PRIMARY)
        self.mc_xc.set(fmt(cam_tb),"necessario para cameras",AMBER)
        if livre>=0:
            self.mc_xl.set(f"+{fmt(livre)}","espaco livre",GREEN_PRIMARY)
            self.lbl_vt.configure(text=f"Storage suficiente  -  {fmt(livre)} de margem disponivel",text_color=GREEN_PRIMARY)
            self.lbl_vs.configure(text=f"O RAID fornece {fmt(util_tb)} e as cameras precisam de {fmt(cam_tb)}. Utilizacao de {pct:.1f}%.")
        else:
            self.mc_xl.set(f"-{fmt(abs(livre))}","deficit!",RED)
            self.lbl_vt.configure(text=f"Storage insuficiente  -  deficit de {fmt(abs(livre))}",text_color=RED)
            self.lbl_vs.configure(text=f"O RAID tem {fmt(util_tb)}, mas as cameras exigem {fmt(cam_tb)}. Adicione HDs ou reduza cameras/retencao.")
        self.pb_comb.set(pct/100); self.pb_comb.configure(progress_color=col)
        self.lbl_gpct.configure(text=f"{pct:.1f}%",text_color=col)
        vals=[raid,fmt(util_tb),f"{ncam} cameras",fmt(cam_tb),f"+{fmt(livre)}" if livre>=0 else f"-{fmt(abs(livre))}",f"{pct:.1f}%"]
        cols=[TEXT1,GREEN_PRIMARY,TEXT1,AMBER,GREEN_PRIMARY if livre>=0 else RED,col]
        for lb,v,c in zip(self._tbl,vals,cols): lb.configure(text=v,text_color=c)

    def _footer(self):
        ctk.CTkFrame(self,fg_color=GREEN_DARKER,height=2,corner_radius=0).pack(fill="x",side="bottom")
        ft=ctk.CTkFrame(self,fg_color=BG_PANEL,height=32,corner_radius=0); ft.pack(fill="x",side="bottom"); ft.pack_propagate(False)
        ctk.CTkLabel(ft,text="Intelbras Storage Calculator  |  Valores estimados para dimensionamento tecnico",
                     font=(FONT,9),text_color=TEXT3).pack(side="left",padx=20,pady=8)
        ctk.CTkLabel(ft,text="2025 Intelbras  |  v3.0 PRO",font=(FONT,9),text_color=TEXT3).pack(side="right",padx=20)

if __name__=="__main__":
    app=App(); app.mainloop()
