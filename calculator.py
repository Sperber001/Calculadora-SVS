import tkinter as tk
from tkinter import ttk
import math

BG_DARK   = "#0D1117"
BG_PANEL  = "#161B22"
BG_CARD   = "#1E2530"
BG_FIELD  = "#242B35"
ACCENT    = "#E8300B"
TEXT_PRI  = "#EAEAEA"
TEXT_SEC  = "#8B949E"
TEXT_MUT  = "#4A5568"
BORDER    = "#2D3748"
SUCCESS   = "#3FB950"
WARNING   = "#D29922"
INFO      = "#388BFD"
FONT      = "Segoe UI"

RAID_INFO = {
    "RAID 0 — Striping":        "Sem redundância. Capacidade = todos os HDs. Se 1 falhar, perde tudo.",
    "RAID 1 — Mirroring":       "Espelhamento total. Tolera falha de 50% dos discos. Mínimo 2 HDs.",
    "RAID 5 — Paridade simples":"Tolera falha de 1 disco. 1 HD reservado para paridade. Mínimo 3 HDs.",
    "RAID 6 — Dupla paridade":  "Tolera falha de 2 discos. 2 HDs para paridade. Mínimo 4 HDs.",
    "RAID 10 — Mirror+Stripe":  "Combina espelhamento e striping. Mínimo 4 HDs (número par).",
    "JBOD — Sem RAID":          "Discos independentes. Sem redundância, sem perda de capacidade.",
}
BITRATE_BASE = {0.5:512, 1:1024, 2:2048, 4:4096, 5:5120, 8:8192, 12:12288}
RES_MAP  = {"D1 / CIF (0.5 MP)":0.5,"720p HD (1 MP)":1,"1080p Full HD (2 MP)":2,
            "4 MP":4,"3K / 5 MP":5,"4K Ultra HD (8 MP)":8,"12 MP":12}
COMP_MAP = {"H.264":1.0,"H.265 / H.265+":0.5,"MJPEG":1.5}

def fmt_tb(v):
    if v>=1000: return f"{v/1000:.2f} PB"
    if v>=1:    return f"{v:.2f} TB"
    return f"{v*1024:.1f} GB"
def fmt_gb(v):
    if v>=1024: return f"{v/1024:.2f} TB"
    return f"{v:.2f} GB"

class ResultCard(tk.Frame):
    def __init__(self, parent, label, **kw):
        super().__init__(parent, bg=BG_FIELD, highlightbackground=BORDER, highlightthickness=1, **kw)
        tk.Label(self, text=label, font=(FONT,8), fg=TEXT_SEC, bg=BG_FIELD).pack(pady=(10,2))
        self.val = tk.Label(self, text="—", font=(FONT,18,"bold"), fg=TEXT_PRI, bg=BG_FIELD)
        self.val.pack()
        self.sub = tk.Label(self, text="", font=(FONT,8), fg=TEXT_MUT, bg=BG_FIELD)
        self.sub.pack(pady=(0,10))
    def set(self, v, s="", c=TEXT_PRI):
        self.val.config(text=v, fg=c)
        self.sub.config(text=s)

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Intelbras — Calculadora de Storage")
        self.configure(bg=BG_DARK)
        self.resizable(True, True)
        self.minsize(860, 660)
        try:
            self.state("zoomed")
        except:
            self.geometry("860x700")
        self._style()
        self._header()
        self._nav()
        self._build_raid()
        self._build_cam()
        self._build_combined()
        self._footer()
        self.show("RAID")
        self.after(100, lambda: (self.calc_raid(), self.calc_cam()))

    def _style(self):
        s = ttk.Style(self)
        s.theme_use("clam")
        for w in ("TCombobox","TSpinbox"):
            s.configure(w, fieldbackground=BG_FIELD, background=BG_FIELD,
                        foreground=TEXT_PRI, arrowcolor=TEXT_SEC,
                        bordercolor=BORDER, selectbackground=BG_FIELD,
                        selectforeground=TEXT_PRI, font=(FONT,10))
            s.map(w, fieldbackground=[("readonly",BG_FIELD)],
                  selectbackground=[("readonly",BG_FIELD)],
                  selectforeground=[("readonly",TEXT_PRI)])

    def _header(self):
        h = tk.Frame(self, bg=BG_PANEL, height=58)
        h.pack(fill="x"); h.pack_propagate(False)
        logo = tk.Frame(h, bg=ACCENT, width=34, height=34)
        logo.pack(side="left", padx=(18,10), pady=12)
        logo.pack_propagate(False)
        tk.Label(logo, text="i", font=(FONT,16,"bold"), fg="white", bg=ACCENT).place(relx=.5,rely=.5,anchor="center")
        tf = tk.Frame(h, bg=BG_PANEL); tf.pack(side="left")
        tk.Label(tf, text="INTELBRAS", font=(FONT,12,"bold"), fg=TEXT_PRI, bg=BG_PANEL).pack(anchor="w")
        tk.Label(tf, text="Calculadora de Storage & CFTV", font=(FONT,8), fg=TEXT_SEC, bg=BG_PANEL).pack(anchor="w")
        tk.Label(h, text="v1.0", font=(FONT,8), fg=TEXT_MUT, bg=BG_PANEL).pack(side="right", padx=18)

    def _nav(self):
        self.nav = tk.Frame(self, bg=BG_DARK); self.nav.pack(fill="x")
        tk.Frame(self.nav, bg=BORDER, height=1).pack(fill="x")
        row = tk.Frame(self.nav, bg=BG_DARK); row.pack(fill="x")
        self.tab_btns = {}
        self.panels   = {}
        for name, icon in [("RAID","💾"),("Câmeras","📹"),("Combinado","📊")]:
            b = tk.Button(row, text=f"  {icon}  {name}  ", font=(FONT,10),
                          bd=0, relief="flat", bg=BG_DARK, fg=TEXT_SEC,
                          cursor="hand2", activebackground=BG_PANEL,
                          activeforeground=TEXT_PRI,
                          command=lambda n=name: self.show(n))
            b.pack(side="left")
            self.tab_btns[name] = b
        tk.Frame(self.nav, bg=BORDER, height=1).pack(fill="x")
        self.content = tk.Frame(self, bg=BG_DARK)
        self.content.pack(fill="both", expand=True, padx=14, pady=10)

    def show(self, name):
        for n,b in self.tab_btns.items():
            b.config(bg=(BG_PANEL if n==name else BG_DARK),
                     fg=(ACCENT if n==name else TEXT_SEC))
        for n,p in self.panels.items():
            (p.pack if n==name else p.pack_forget)(fill="both", expand=True) if n==name else p.pack_forget()

    def _combo(self, p, var, vals, w=30, cmd=None):
        cb = ttk.Combobox(p, textvariable=var, values=vals, state="readonly", width=w, font=(FONT,10))
        if cmd: cb.bind("<<ComboboxSelected>>", lambda e: cmd())
        return cb
    def _spin(self, p, var, mn, mx, step=1, w=14):
        return ttk.Spinbox(p, from_=mn, to=mx, increment=step, textvariable=var, width=w, font=(FONT,10))
    def _lbl(self, p, t, size=9, color=TEXT_SEC, bold=False):
        return tk.Label(p, text=t, font=(FONT,size,"bold" if bold else "normal"), fg=color, bg=BG_CARD)
    def _field(self, p, label):
        f = tk.Frame(p, bg=BG_CARD); f.pack(fill="x", pady=4)
        tk.Label(f, text=label, font=(FONT,8), fg=TEXT_SEC, bg=BG_CARD).pack(anchor="w", pady=(0,3))
        return f
    def _card(self, p):
        c = tk.Frame(p, bg=BG_CARD, highlightbackground=BORDER, highlightthickness=1)
        return c

    # ── RAID TAB ──────────────────────────────────────────────────────────────
    def _build_raid(self):
        p = tk.Frame(self.content, bg=BG_DARK)
        self.panels["RAID"] = p
        p.columnconfigure(0, weight=3); p.columnconfigure(1, weight=2); p.rowconfigure(0, weight=1)

        left = self._card(p); left.grid(row=0,column=0,sticky="nsew",padx=(0,8))
        tk.Label(left, text="Configuração de Discos", font=(FONT,11,"bold"),
                 fg=ACCENT, bg=BG_CARD).pack(anchor="w", padx=14, pady=(12,8))
        tk.Frame(left, bg=BORDER, height=1).pack(fill="x", padx=14)
        body = tk.Frame(left, bg=BG_CARD); body.pack(fill="x", padx=14, pady=10)

        self.v_nhd = tk.IntVar(value=4)
        self.v_nhd.trace_add("write", lambda *_: self.calc_raid())
        f = self._field(body,"Número de HDs")
        self._spin(f, self.v_nhd, 1, 64).pack(fill="x")

        self.v_thd_str = tk.StringVar(value="4.0 TB")
        f2 = self._field(body,"Capacidade por HD")
        self._combo(f2, self.v_thd_str,
                    [f"{v} TB" for v in [0.5,1,2,3,4,6,8,10,12,14,16,18,20]],
                    w=28, cmd=self.calc_raid).pack(fill="x")

        self.v_raid = tk.StringVar(value="RAID 5 — Paridade simples")
        f3 = self._field(body,"Tipo de RAID")
        self._combo(f3, self.v_raid, list(RAID_INFO.keys()), w=28, cmd=self.calc_raid).pack(fill="x")
        self.lbl_rdesc = tk.Label(body, text="", font=(FONT,8), fg=TEXT_SEC,
                                  bg=BG_CARD, wraplength=280, justify="left")
        self.lbl_rdesc.pack(anchor="w", pady=(2,6))

        hs_row = tk.Frame(body, bg=BG_CARD); hs_row.pack(fill="x", pady=4)
        tk.Label(hs_row, text="Hot Spare", font=(FONT,10), fg=TEXT_PRI, bg=BG_CARD).pack(side="left")
        self.v_hs = tk.BooleanVar(value=False)
        self.v_hs.trace_add("write", lambda *_: self.calc_raid())
        tk.Checkbutton(hs_row, variable=self.v_hs, bg=BG_CARD,
                       activebackground=BG_CARD, selectcolor=BG_FIELD,
                       fg=ACCENT, activeforeground=ACCENT,
                       relief="flat").pack(side="left", padx=6)
        tk.Label(body, text="1 HD reservado em standby para substituição automática em caso de falha.",
                 font=(FONT,8), fg=TEXT_MUT, bg=BG_CARD, wraplength=280, justify="left").pack(anchor="w")

        right = tk.Frame(p, bg=BG_DARK); right.grid(row=0,column=1,sticky="nsew")
        self.rc_rd = ResultCard(right,"HDs no Array"); self.rc_rd.pack(fill="x",pady=(0,6))
        self.rc_rb = ResultCard(right,"Capacidade Bruta"); self.rc_rb.pack(fill="x",pady=(0,6))
        self.rc_ru = ResultCard(right,"Volume Disponível"); self.rc_ru.pack(fill="x",pady=(0,6))
        self.rc_re = ResultCard(right,"Eficiência"); self.rc_re.pack(fill="x",pady=(0,6))
        self.lbl_rinfo = tk.Label(right, text="", font=(FONT,8), fg=TEXT_SEC,
                                  bg=BG_FIELD, wraplength=260, justify="left", padx=10, pady=8)
        self.lbl_rinfo.pack(fill="x")

    def calc_raid(self, *_):
        try:
            n   = int(self.v_nhd.get())
            tam = float(self.v_thd_str.get().replace(" TB",""))
        except: return
        raid = self.v_raid.get()
        hs   = self.v_hs.get()
        self.lbl_rdesc.config(text=RAID_INFO.get(raid,""))
        dr  = max(n-1,1) if hs else n
        bruto = dr*tam; util=0; err=""
        r = raid.split(" — ")[0]
        if   r=="RAID 0":  util=bruto
        elif r=="RAID 1":
            if dr<2: err="RAID 1 requer mínimo 2 HDs."
            else: util=math.floor(dr/2)*tam
        elif r=="RAID 5":
            if dr<3: err="RAID 5 requer mínimo 3 HDs."
            else: util=(dr-1)*tam
        elif r=="RAID 6":
            if dr<4: err="RAID 6 requer mínimo 4 HDs."
            else: util=(dr-2)*tam
        elif r=="RAID 10":
            if dr<4 or dr%2!=0: err="RAID 10 requer mínimo 4 HDs (par)."
            else: util=(dr/2)*tam
        elif r=="JBOD": util=bruto
        efic = round((util/bruto)*100) if bruto>0 else 0
        self.rc_rd.set(str(dr),"discos no array")
        self.rc_rb.set(fmt_tb(bruto),f"{bruto:.1f} TB bruto")
        if err:
            self.rc_ru.set("—",err,WARNING)
            self.rc_re.set("—","",TEXT_MUT)
            self.lbl_rinfo.config(text=err, fg=WARNING)
        else:
            col = SUCCESS if efic>=75 else WARNING if efic>=50 else ACCENT
            self.rc_ru.set(fmt_tb(util),f"{util:.2f} TB disponíveis",INFO)
            self.rc_re.set(f"{efic}%","do espaço bruto aproveitado",col)
            hs_t = f"  Hot Spare: 1 HD ({tam} TB) em standby." if hs else ""
            self.lbl_rinfo.config(text=f"Array com {dr} HD(s) de {tam} TB.{hs_t}", fg=TEXT_SEC)
        self._upd_combined()

    # ── CÂMERAS TAB ───────────────────────────────────────────────────────────
    def _build_cam(self):
        p = tk.Frame(self.content, bg=BG_DARK)
        self.panels["Câmeras"] = p
        p.columnconfigure(0,weight=3); p.columnconfigure(1,weight=2); p.rowconfigure(0,weight=1)

        left = self._card(p); left.grid(row=0,column=0,sticky="nsew",padx=(0,8))
        tk.Label(left, text="Parâmetros de Gravação", font=(FONT,11,"bold"),
                 fg=ACCENT, bg=BG_CARD).pack(anchor="w", padx=14, pady=(12,8))
        tk.Frame(left, bg=BORDER, height=1).pack(fill="x", padx=14)
        body = tk.Frame(left, bg=BG_CARD); body.pack(fill="x", padx=14, pady=10)

        self.v_ncam = tk.IntVar(value=8)
        self.v_ncam.trace_add("write", lambda *_: self.calc_cam())
        f = self._field(body,"Número de câmeras")
        self._spin(f, self.v_ncam, 1, 512).pack(fill="x")

        self.v_res = tk.StringVar(value="1080p Full HD (2 MP)")
        f2 = self._field(body,"Resolução")
        self._combo(f2, self.v_res, list(RES_MAP.keys()), w=28, cmd=self.calc_cam).pack(fill="x")

        self.v_comp = tk.StringVar(value="H.265 / H.265+")
        f3 = self._field(body,"Compressão de vídeo")
        self._combo(f3, self.v_comp, list(COMP_MAP.keys()), w=28, cmd=self.calc_cam).pack(fill="x")

        self.v_fps = tk.StringVar(value="15 fps")
        f4 = self._field(body,"Frames por segundo (FPS)")
        self._combo(f4, self.v_fps,
                    ["1 fps","5 fps","10 fps","15 fps","20 fps","25 fps","30 fps"],
                    w=28, cmd=self.calc_cam).pack(fill="x")

        self.v_bitmode = tk.StringVar(value="Automático (por resolução)")
        f5 = self._field(body,"Modo de bitrate")
        self._combo(f5, self.v_bitmode,
                    ["Automático (por resolução)","Manual (Kbps)"],
                    w=28, cmd=self.calc_cam).pack(fill="x")

        self.fr_bit = self._field(body,"Bitrate por câmera (Kbps)")
        self.v_bitrate = tk.IntVar(value=2048)
        self.v_bitrate.trace_add("write", lambda *_: self.calc_cam())
        self.spin_bit = self._spin(self.fr_bit, self.v_bitrate, 64, 32000, step=64)
        self.spin_bit.pack(fill="x")

        r2 = tk.Frame(body, bg=BG_CARD); r2.pack(fill="x", pady=4)
        c1 = tk.Frame(r2, bg=BG_CARD); c1.pack(side="left",expand=True,fill="x",padx=(0,6))
        tk.Label(c1,text="Dias de retenção",font=(FONT,8),fg=TEXT_SEC,bg=BG_CARD).pack(anchor="w",pady=(0,3))
        self.v_dias = tk.IntVar(value=30)
        self.v_dias.trace_add("write", lambda *_: self.calc_cam())
        self._spin(c1, self.v_dias, 1, 365, w=12).pack(fill="x")

        c2 = tk.Frame(r2, bg=BG_CARD); c2.pack(side="left",expand=True,fill="x")
        tk.Label(c2,text="Horas/dia gravando",font=(FONT,8),fg=TEXT_SEC,bg=BG_CARD).pack(anchor="w",pady=(0,3))
        self.v_horas = tk.IntVar(value=24)
        self.v_horas.trace_add("write", lambda *_: self.calc_cam())
        self._spin(c2, self.v_horas, 1, 24, w=12).pack(fill="x")

        right = tk.Frame(p, bg=BG_DARK); right.grid(row=0,column=1,sticky="nsew")
        self.rc_cbt = ResultCard(right,"Bitrate Total"); self.rc_cbt.pack(fill="x",pady=(0,6))
        self.rc_cpd = ResultCard(right,"Por câmera / dia"); self.rc_cpd.pack(fill="x",pady=(0,6))
        self.rc_cst = ResultCard(right,"Armazenamento Necessário"); self.rc_cst.pack(fill="x",pady=(0,6))
        self.rc_cd1 = ResultCard(right,"Dias com 1 TB"); self.rc_cd1.pack(fill="x",pady=(0,6))
        self.lbl_cinfo = tk.Label(right, text="", font=(FONT,8), fg=TEXT_SEC,
                                  bg=BG_FIELD, wraplength=260, justify="left", padx=10, pady=8)
        self.lbl_cinfo.pack(fill="x")

    def calc_cam(self, *_):
        try:
            ncam  = int(self.v_ncam.get())
            res   = RES_MAP.get(self.v_res.get(),2)
            comp  = COMP_MAP.get(self.v_comp.get(),0.5)
            fps   = int(self.v_fps.get().replace(" fps",""))
            dias  = int(self.v_dias.get())
            horas = int(self.v_horas.get())
            auto  = "Auto" in self.v_bitmode.get()
        except: return
        if auto:
            br = BITRATE_BASE.get(res,2048)*comp*(fps/15)
            self.spin_bit.config(state="disabled")
        else:
            br = float(self.v_bitrate.get())
            self.spin_bit.config(state="normal")
        total_mbps = (br*ncam)/1000
        gb_cam     = (br*3600*horas)/(8*1024*1024)
        total_tb   = (gb_cam*ncam*dias)/1024
        d1tb       = (1024/(gb_cam*ncam)) if gb_cam*ncam>0 else 0
        self.rc_cbt.set(f"{total_mbps:.1f} Mbps",f"{br:.0f} Kbps por câmera",INFO)
        self.rc_cpd.set(fmt_gb(gb_cam),"gravação contínua",TEXT_PRI)
        self.rc_cst.set(fmt_tb(total_tb),f"{ncam} câm. × {dias} dias",ACCENT)
        self.rc_cd1.set(f"{d1tb:.1f} dias","por 1 TB de armazenamento",SUCCESS)
        self.lbl_cinfo.config(
            text=f"{ncam} câmera{'s' if ncam>1 else ''} | {self.v_comp.get()} | {fps} fps\n"
                 f"Retenção: {dias} dias × {horas}h/dia\n"
                 f"Total necessário: {fmt_tb(total_tb)}")
        self._upd_combined()

    # ── COMBINADO TAB ─────────────────────────────────────────────────────────
    def _build_combined(self):
        p = tk.Frame(self.content, bg=BG_DARK)
        self.panels["Combinado"] = p

        tk.Label(p, text="Análise Combinada — RAID vs Necessidade de Armazenamento",
                 font=(FONT,11,"bold"), fg=TEXT_PRI, bg=BG_DARK).pack(anchor="w", pady=(0,10))

        row = tk.Frame(p, bg=BG_DARK); row.pack(fill="x")
        self.rc_xr = ResultCard(row,"Disponível no RAID")
        self.rc_xr.pack(side="left",expand=True,fill="x",padx=(0,6))
        self.rc_xc = ResultCard(row,"Necessário pelas Câmeras")
        self.rc_xc.pack(side="left",expand=True,fill="x",padx=(0,6))
        self.rc_xl = ResultCard(row,"Espaço Livre")
        self.rc_xl.pack(side="left",expand=True,fill="x")

        self.vrd_frame = tk.Frame(p, bg=BG_FIELD, highlightbackground=BORDER, highlightthickness=1)
        self.vrd_frame.pack(fill="x", pady=10)
        self.lbl_vrd  = tk.Label(self.vrd_frame, text="", font=(FONT,11,"bold"),
                                  fg=SUCCESS, bg=BG_FIELD, padx=14, pady=10)
        self.lbl_vrd.pack(anchor="w")
        self.lbl_vsub = tk.Label(self.vrd_frame, text="", font=(FONT,9),
                                  fg=TEXT_SEC, bg=BG_FIELD, padx=14, pady=(0,10),
                                  wraplength=760, justify="left")
        self.lbl_vsub.pack(anchor="w")

        gf = self._card(p); gf.pack(fill="x")
        tk.Label(gf, text="Utilização do Storage", font=(FONT,9), fg=TEXT_SEC, bg=BG_CARD).pack(anchor="w",padx=14,pady=(10,4))
        bg_bar = tk.Frame(gf, bg=BORDER, height=24); bg_bar.pack(fill="x",padx=14,pady=(0,4))
        bg_bar.pack_propagate(False)
        self.gauge = tk.Frame(bg_bar, bg=ACCENT, height=24)
        self.gauge.place(x=0,y=0,relheight=1,relwidth=0)
        self.lbl_pct = tk.Label(gf, text="", font=(FONT,8), fg=TEXT_SEC, bg=BG_CARD)
        self.lbl_pct.pack(anchor="e",padx=14,pady=(0,10))

    def _upd_combined(self):
        try:
            n   = int(self.v_nhd.get())
            tam = float(self.v_thd_str.get().replace(" TB",""))
        except: return
        raid=self.v_raid.get(); hs=self.v_hs.get()
        dr=max(n-1,1) if hs else n
        r=raid.split(" — ")[0]; util=0
        if   r=="RAID 0":  util=dr*tam
        elif r=="RAID 1" and dr>=2: util=math.floor(dr/2)*tam
        elif r=="RAID 5" and dr>=3: util=(dr-1)*tam
        elif r=="RAID 6" and dr>=4: util=(dr-2)*tam
        elif r=="RAID 10" and dr>=4 and dr%2==0: util=(dr/2)*tam
        elif r=="JBOD":    util=dr*tam
        try:
            ncam=int(self.v_ncam.get())
            res=RES_MAP.get(self.v_res.get(),2)
            comp=COMP_MAP.get(self.v_comp.get(),0.5)
            fps=int(self.v_fps.get().replace(" fps",""))
            dias=int(self.v_dias.get()); horas=int(self.v_horas.get())
            auto="Auto" in self.v_bitmode.get()
            br=BITRATE_BASE.get(res,2048)*comp*(fps/15) if auto else float(self.v_bitrate.get())
            cam_tb=(br*3600*horas*ncam*dias)/(8*1024*1024*1024)
        except: return
        livre=util-cam_tb
        pct=min((cam_tb/util)*100,100) if util>0 else 0
        self.rc_xr.set(fmt_tb(util),"volume RAID disponível",INFO)
        self.rc_xc.set(fmt_tb(cam_tb),"necessário para câmeras",ACCENT)
        if livre>=0:
            self.rc_xl.set(fmt_tb(livre),"espaço livre",SUCCESS)
            self.lbl_vrd.config(text=f"✔  Storage suficiente — {fmt_tb(livre)} de margem livre",fg=SUCCESS)
            sub=f"O RAID fornece {fmt_tb(util)}, as câmeras precisam de {fmt_tb(cam_tb)}. Utilização: {pct:.1f}%."
        else:
            self.rc_xl.set(f"−{fmt_tb(abs(livre))}","déficit!",ACCENT)
            self.lbl_vrd.config(text=f"⚠  Storage insuficiente — déficit de {fmt_tb(abs(livre))}",fg=ACCENT)
            sub=f"O RAID tem {fmt_tb(util)}, mas as câmeras exigem {fmt_tb(cam_tb)}. Adicione HDs ou reduza retenção/câmeras."
        self.lbl_vsub.config(text=sub)
        self.gauge.place(relwidth=min(pct/100,1))
        self.gauge.config(bg=SUCCESS if pct<70 else WARNING if pct<90 else ACCENT)
        self.lbl_pct.config(text=f"{pct:.1f}% utilizado")

    def _footer(self):
        ft = tk.Frame(self, bg=BG_PANEL, height=28); ft.pack(fill="x",side="bottom")
        ft.pack_propagate(False)
        tk.Label(ft, text="Intelbras Storage Calculator  ·  Valores estimados para dimensionamento técnico",
                 font=(FONT,8), fg=TEXT_MUT, bg=BG_PANEL).pack(side="left",padx=14,pady=5)
        tk.Label(ft, text="© 2025 Intelbras", font=(FONT,8), fg=TEXT_MUT, bg=BG_PANEL).pack(side="right",padx=14)

if __name__ == "__main__":
    app = App()
    app.mainloop()
