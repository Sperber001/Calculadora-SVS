import customtkinter as ctk
import math
import tkinter as tk
from tkinter import filedialog, messagebox
from datetime import datetime
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.units import cm
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    REPORTLAB_OK = True
except ImportError:
    REPORTLAB_OK = False


# ── ÍCONE EMBUTIDO (base64) ────────────────────────────────────────────────
_ICON_B64 = """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"""
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
TEXT2         = "#B8D4BC"
TEXT3         = "#7AAB84"
WHITE         = "#FFFFFF"
AMBER         = "#F59E0B"
RED           = "#E53935"
FONT          = "Segoe UI"
# Fatores de conversão baseados na referência técnica Seagate/IEC
FATOR_TIB   = 1 / 1.099511628   # TB fabricante → TiB exibido no SO  (~0.9095)
FATOR_UTIL  = 0.90               # Fator útil após formatação (NTFS/EXT4/XFS) ~1% overhead + conversão
DECIMAL_TO_BINARY = FATOR_TIB   # alias para compatibilidade


RAID_DATA = {
    "RAID 0":  ("Striping sem redundância",     "Sem proteção. Se 1 HD falhar, perde tudo.",                   1, lambda d,t: d*t),
    "RAID 1":  ("Mirroring — espelho total",       "Tolera falha de metade dos discos. Mín. 2 HDs.",              2, lambda d,t: math.floor(d/2)*t),
    "RAID 5":  ("Paridade simples distribuída",  "Tolera falha de 1 disco. 1 HD para paridade. Mín. 3 HDs.",   3, lambda d,t: (d-1)*t),
    "RAID 6":  ("Dupla paridade distribuída",    "Tolera falha de 2 discos. 2 HDs para paridade. Mín. 4 HDs.",4, lambda d,t: (d-2)*t),
    "RAID 10": ("Mirror + Stripe combinados",    "Alta performance e redundância. Mín. 4 HDs (par).",             4, lambda d,t: (d//2)*t),
    "JBOD":    ("Discos independentes sem RAID", "Sem redundância. Capacidade total de todos os HDs.",          1, lambda d,t: d*t),
}
TB_SIZES = [0.5,1,2,3,4,6,8,10,12,14,16,18,20,22,24]
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
        ctk.CTkLabel(self, text=label, font=(FONT,11), text_color=TEXT2).pack(anchor="w", padx=14, pady=12)
        self.val = ctk.CTkLabel(self, text="--", font=(FONT,22,"bold"), text_color=TEXT1)
        self.val.pack(anchor="w", padx=14)
        self.sub = ctk.CTkLabel(self, text="", font=(FONT,10), text_color=TEXT3)
        self.sub.pack(anchor="w", padx=14, pady=12)
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
        # Aplicar ícone SVS
        try:
            import base64, tempfile, os
            _ico_data = base64.b64decode(_ICON_B64)
            _tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".ico")
            _tmp.write(_ico_data); _tmp.close()
            self.iconbitmap(_tmp.name)
            os.unlink(_tmp.name)
        except: pass
        self.configure(fg_color=BG_DARK)
        self.minsize(1000, 680)
        try: self.state("zoomed")
        except: self.geometry("1000x700")
        self._active = ""
        self._panels = {}
        self._header()
        self._footer()      # footer primeiro (side=bottom), body depois expande
        self._layout()
        self._sidebar()
        self._raid_panel()
        self._cam_panel()
        self._combined_panel()
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
        badge = ctk.CTkFrame(right, fg_color=GREEN_DARKER, corner_radius=14, border_width=1, border_color=GREEN_DARK)
        badge.pack()
        ctk.CTkLabel(badge, text="v3.0 PRO", font=(FONT,9,"bold"), text_color=GREEN_PRIMARY).pack(padx=10, pady=5)

        self._div_line = ctk.CTkFrame(self, fg_color=GREEN_DARKER, height=2, corner_radius=0)
        self._div_line.pack(fill="x")

    def _layout(self):
        self.body = ctk.CTkFrame(self, fg_color="transparent"); self.body.pack(fill="both", expand=True)

    def _sidebar(self):
        self.sb = ctk.CTkFrame(self.body, fg_color=BG_PANEL, width=220, corner_radius=0)
        self.sb.pack(side="left", fill="y"); self.sb.pack_propagate(False)
        ctk.CTkFrame(self.sb, fg_color=BORDER, height=1, corner_radius=0).pack(fill="x")
        ctk.CTkLabel(self.sb, text="FERRAMENTAS", font=(FONT,9,"bold"), text_color=TEXT3).pack(anchor="w", padx=16, pady=20)
        self._nav_ws = {}
        for key,icon,label in [("raid","💾","Calculadora RAID"),("cameras","📹","Câmeras & Gravação"),("combinado","📊","Análise Combinada")]:
            self._nav_ws[key] = self._nav_btn(key, icon, label)
        ctk.CTkFrame(self.sb, fg_color=BORDER, height=1, corner_radius=0).pack(fill="x", pady=16)
        tip = ctk.CTkFrame(self.sb, fg_color=BG_CARD, corner_radius=8, border_width=1, border_color=BORDER)
        tip.pack(fill="x", padx=12)
        ctk.CTkLabel(tip, text="Dica rápida", font=(FONT,10,"bold"), text_color=GREEN_PRIMARY).pack(anchor="w", padx=12, pady=10)
        ctk.CTkLabel(tip, text="Configure o RAID\ne depois as cameras\npara ver a analise\ncombinada.",
                     font=(FONT,9), text_color=TEXT2, justify="left").pack(anchor="w", padx=12, pady=10)
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
            ctk.CTkLabel(c, text=title, font=(FONT,12,"bold"), text_color=TEXT1).pack(anchor="w", padx=18, pady=14)
            ctk.CTkFrame(c, fg_color=BORDER, height=1, corner_radius=0).pack(fill="x")
        return c

    def _fl(self, p, label):
        f = ctk.CTkFrame(p, fg_color="transparent"); f.pack(fill="x", pady=5)
        ctk.CTkLabel(f, text=label, font=(FONT,9,"bold"), text_color=TEXT3).pack(anchor="w", pady=5)
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
        row = ctk.CTkFrame(p, fg_color="transparent"); row.pack(fill="x", pady=4)
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
            b.pack(side="left", padx=4)
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
        ctk.CTkLabel(p, text="Configure os discos e o tipo de array para calcular o volume disponível",
                     font=(FONT,10), text_color=TEXT2).pack(anchor="w", pady=16)

        body = ctk.CTkFrame(p, fg_color="transparent"); body.pack(fill="both", expand=True)
        body.columnconfigure(0,weight=2); body.columnconfigure(1,weight=3); body.rowconfigure(0,weight=1)

        left = self._card(body,"Configuração dos Discos"); left.grid(row=0,column=0,sticky="nsew",padx=12)
        frm = ctk.CTkFrame(left,fg_color="transparent"); frm.pack(fill="x",padx=18,pady=12)

        ff=self._fl(frm,"NÚMERO DE HDs")
        self.v_nhd=tk.IntVar(value=4); self.v_nhd.trace_add("write",lambda *_:self._calc_raid())
        _,self._nhd_q=self._qbtns(ff,[2,4,8,12,16,24],self.v_nhd,self._calc_raid)
        cust=ctk.CTkFrame(ff,fg_color="transparent"); cust.pack(fill="x",pady=4)
        ctk.CTkLabel(cust,text="Personalizado:",font=(FONT,10),text_color=TEXT3).pack(side="left")
        self._entry(cust,self.v_nhd,width=70).pack(side="left",padx=8)

        ff2=self._fl(frm,"CAPACIDADE POR HD (anunciada pelo fabricante)")
        self.v_thd=tk.StringVar(value="4 TB"); self.v_thd.trace_add("write",lambda *_:self._calc_raid())
        self._combo(ff2,self.v_thd,[f"{v} TB" for v in TB_SIZES],cmd=self._calc_raid,width=260).pack(fill="x")

        # Toggle decimal → binário
        conv_row=ctk.CTkFrame(ff2,fg_color="transparent"); conv_row.pack(fill="x",pady=6)
        self.v_conv=tk.BooleanVar(value=True)
        self.v_conv.trace_add("write",lambda *_:self._calc_raid())
        self.chk_conv=ctk.CTkSwitch(conv_row,
            text="Aplicar conversão real (decimal → binário)",
            variable=self.v_conv, onvalue=True, offvalue=False,
            font=(FONT,10), text_color=TEXT2,
            fg_color=BORDER, progress_color=GREEN_PRIMARY,
            button_color=TEXT1, button_hover_color=GREEN_PRIMARY)
        self.chk_conv.pack(anchor="w")
        self.lbl_cap_real=ctk.CTkLabel(ff2,
            text="Capacidade real no sistema: 3.64 TB",
            font=(FONT,9,"bold"), text_color=GREEN_PRIMARY)
        self.lbl_cap_real.pack(anchor="w",pady=2)
        self.lbl_cap_loss=ctk.CTkLabel(ff2,
            text="Perda de ~9.05% por diferença decimal/binário",
            font=(FONT,9), text_color=TEXT3)
        self.lbl_cap_loss.pack(anchor="w")

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
            b.grid(row=i//3,column=i%3,padx=6,pady=6,sticky="ew"); rg.columnconfigure(i%3,weight=1)
            self._rbw[r]=b
        self.lbl_rdesc=ctk.CTkLabel(frm,text="Tolera falha de 1 disco. Min. 3 HDs.",
                                    font=(FONT,10),text_color=TEXT2,wraplength=300,justify="left")
        self.lbl_rdesc.pack(anchor="w",pady=4)

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
            b.pack(side="left",padx=4); self._hs_btns.append((b,v))
        ch=ctk.CTkFrame(ff4,fg_color="transparent"); ch.pack(fill="x",pady=6)
        ctk.CTkLabel(ch,text="Personalizado:",font=(FONT,10),text_color=TEXT3).pack(side="left")
        self._entry(ch,self.v_hs,width=60).pack(side="left",padx=8)
        self.lbl_hs=ctk.CTkLabel(ff4,text="Sem disco de reserva configurado.",font=(FONT,9),text_color=TEXT3)
        self.lbl_hs.pack(anchor="w",pady=4)

        self._upd_nhd(); self._upd_rbw(); self._upd_hs()

        right=ctk.CTkFrame(body,fg_color="transparent"); right.grid(row=0,column=1,sticky="nsew")
        ctk.CTkLabel(right,text="Resultado do Array",font=(FONT,12,"bold"),text_color=TEXT1).pack(anchor="w",pady=10)
        g=ctk.CTkFrame(right,fg_color="transparent"); g.pack(fill="x",pady=10)
        g.columnconfigure(0,weight=1); g.columnconfigure(1,weight=1)
        self.mc_rd=MetricCard(g,"HDs no Array"); self.mc_rd.grid(row=0,column=0,sticky="ew",padx=8,pady=8)
        self.mc_rb=MetricCard(g,"Capacidade Bruta"); self.mc_rb.grid(row=0,column=1,sticky="ew",pady=8)
        self.mc_ru=MetricCard(g,"Volume Disponível"); self.mc_ru.grid(row=1,column=0,sticky="ew",padx=8)
        self.mc_re=MetricCard(g,"Eficiência de Uso"); self.mc_re.grid(row=1,column=1,sticky="ew")

        pc=self._card(right); pc.pack(fill="x",pady=10)
        pt=ctk.CTkFrame(pc,fg_color="transparent"); pt.pack(fill="x",padx=16,pady=14)
        ctk.CTkLabel(pt,text="Aproveitamento do Storage",font=(FONT,10,"bold"),text_color=TEXT2).pack(side="left")
        self.lbl_pct_r=ctk.CTkLabel(pt,text="",font=(FONT,10,"bold"),text_color=GREEN_PRIMARY); self.lbl_pct_r.pack(side="right")
        self.pb_raid=ctk.CTkProgressBar(pc,fg_color=BG_FIELD,progress_color=GREEN_PRIMARY,height=10,corner_radius=5)
        self.pb_raid.pack(fill="x",padx=16,pady=6); self.pb_raid.set(0)
        self.lbl_bar_r=ctk.CTkLabel(pc,text="",font=(FONT,9),text_color=TEXT3); self.lbl_bar_r.pack(anchor="w",padx=16,pady=12)
        self.info_r=InfoBox(right); self.info_r.pack(fill="x",pady=10)

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
        elif cur==1: self.lbl_hs.configure(text="1 HD reservado em standby para substituição automática.",text_color=GREEN_PRIMARY)
        else: self.lbl_hs.configure(text=f"{cur} HDs reservados em standby para substituição automática.",text_color=GREEN_PRIMARY)

    def _get_tam(self):
        """Retorna capacidade útil por HD aplicando conversão decimal→binário + overhead formatação."""
        try:
            tam_fab = float(self.v_thd.get().replace(" TB",""))
        except:
            tam_fab = 4.0
        conv = getattr(self, "v_conv", None)
        if conv and conv.get():
            # TiB exibido no SO: TB / 1.099511628 ≈ TB × 0.9095
            tam_tib  = tam_fab * FATOR_TIB
            # Útil real após formatação: TB × 0.90 (regra prática para NVR/DVR)
            tam_util = tam_fab * FATOR_UTIL
        else:
            tam_tib  = tam_fab
            tam_util = tam_fab
        # Atualizar labels informativos
        try:
            if conv and conv.get():
                self.lbl_cap_real.configure(
                    text=f"Exibido no SO: {tam_tib:.2f} TiB  |  Útil (após formatação): {tam_util:.2f} TB",
                    text_color=GREEN_PRIMARY)
                self.lbl_cap_loss.configure(
                    text=f"Fórmula: {tam_fab} TB ÷ 1,0995 = {tam_tib:.2f} TiB  →  útil ≈ {tam_fab} × 0,90 = {tam_util:.2f} TB",
                    text_color=TEXT3)
            else:
                self.lbl_cap_real.configure(
                    text=f"Usando valor do fabricante: {tam_fab:.1f} TB (sem conversão)",
                    text_color=AMBER)
                self.lbl_cap_loss.configure(
                    text="Atenção: valor real no sistema será menor que o anunciado",
                    text_color=TEXT3)
        except: pass
        return tam_util

    def _calc_raid(self, *_):
        try: n=int(self.v_nhd.get()); hs=int(self.v_hs.get())
        except: return
        tam = self._get_tam()
        self._upd_nhd(); self._upd_hs()
        raid=self.v_raid.get()
        if raid not in RAID_DATA: return
        sub,desc,min_d,calc=RAID_DATA[raid]
        self.lbl_rdesc.configure(text=f"  {desc}")
        dr=max(n-hs,1) if hs>0 else n; bruto=dr*tam
        if dr<min_d and raid not in ("JBOD","RAID 0"):
            err=f"  {raid} requer mínimo {min_d} HDs ativos. Reduza hot spares ou adicione HDs."
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
        conv_on = getattr(self,"v_conv",None) and self.v_conv.get()
        tam_fab_val = float(self.v_thd.get().replace(" TB",""))
        rb_sub  = f"{n} × {tam_fab_val:.0f} TB fab. = {n*tam:.2f} TB úteis" if conv_on else f"{n} × {tam_fab_val:.0f} TB (sem conversão)"
        self.mc_rb.set(fmt(n*tam), rb_sub)
        self.mc_ru.set(fmt(util),f"{util:.2f} TB disponíveis",GREEN_PRIMARY)
        self.mc_re.set(f"{efic}%","do espaço aproveitado",col)
        self.pb_raid.set(efic/100); self.pb_raid.configure(progress_color=col)
        self.lbl_pct_r.configure(text=f"{efic}%",text_color=col)
        hs_t=f"  |  {hs} HS reservados" if hs>0 else ""
        self.lbl_bar_r.configure(text=f"{dr} HDs x {tam} TB  |  {raid}{hs_t}")
        self.info_r.set(f"Util: {fmt(util)}   |   Overhead: {fmt(bruto-util)}   |   Hot Spare: {hs} HD(s)   |   Eficiência: {efic}%",TEXT2)
        self._upd_combined()

    # ──────────────────────────────────────────── CAMERAS ───────────────────
    def _cam_panel(self):
        p=ctk.CTkScrollableFrame(self.content,fg_color="transparent",scrollbar_button_color=BORDER)
        self._panels["cameras"]=p
        ctk.CTkLabel(p,text="Câmeras & Gravação",font=(FONT,16,"bold"),text_color=TEXT1).pack(anchor="w")
        ctk.CTkLabel(p,text="Calcule o armazenamento necessário para o seu sistema de CFTV",
                     font=(FONT,10),text_color=TEXT2).pack(anchor="w",pady=16)

        body=ctk.CTkFrame(p,fg_color="transparent"); body.pack(fill="both",expand=True)
        body.columnconfigure(0,weight=2); body.columnconfigure(1,weight=3); body.rowconfigure(0,weight=1)

        left=self._card(body,"Parâmetros de Gravação"); left.grid(row=0,column=0,sticky="nsew",padx=12)
        frm=ctk.CTkFrame(left,fg_color="transparent"); frm.pack(fill="x",padx=18,pady=12)

        ff=self._fl(frm,"NÚMERO DE CÂMERAS")
        self.v_ncam=tk.IntVar(value=8); self.v_ncam.trace_add("write",lambda *_:self._calc_cam())
        _,self._cam_q=self._qbtns(ff,[4,8,16,32,64],self.v_ncam,self._calc_cam)
        cust=ctk.CTkFrame(ff,fg_color="transparent"); cust.pack(fill="x",pady=4)
        ctk.CTkLabel(cust,text="Personalizado:",font=(FONT,10),text_color=TEXT3).pack(side="left")
        self._entry(cust,self.v_ncam,width=70).pack(side="left",padx=8)

        ff2=self._fl(frm,"RESOLUÇÃO")
        self.v_res=tk.StringVar(value="1080p FullHD-2MP")
        self._combo(ff2,self.v_res,list(RES_MAP.keys()),cmd=self._calc_cam,width=260).pack(fill="x")

        r2=ctk.CTkFrame(frm,fg_color="transparent"); r2.pack(fill="x")
        c1=ctk.CTkFrame(r2,fg_color="transparent"); c1.pack(side="left",expand=True,fill="x",padx=8)
        ctk.CTkLabel(c1,text="COMPRESSÃO",font=(FONT,9,"bold"),text_color=TEXT3).pack(anchor="w",pady=5)
        self.v_comp=tk.StringVar(value="H.265/H.265+")
        self._combo(c1,self.v_comp,list(COMP_MAP.keys()),cmd=self._calc_cam,width=120).pack(fill="x")
        c2=ctk.CTkFrame(r2,fg_color="transparent"); c2.pack(side="left",expand=True,fill="x")
        ctk.CTkLabel(c2,text="FPS",font=(FONT,9,"bold"),text_color=TEXT3).pack(anchor="w",pady=5)
        self.v_fps=tk.StringVar(value="15 fps")
        self._combo(c2,self.v_fps,["1 fps","5 fps","10 fps","15 fps","20 fps","25 fps","30 fps"],cmd=self._calc_cam,width=100).pack(fill="x")

        ff3=self._fl(frm,"BITRATE POR CÂMERA (KBPS)")
        self.v_bitrate=tk.IntVar(value=2048); self.v_bitrate.trace_add("write",lambda *_:self._calc_cam())
        self.entry_bit=self._entry(ff3,self.v_bitrate,width=260); self.entry_bit.pack(fill="x")
        ctk.CTkLabel(ff3,text="Digite o bitrate conforme configurado no DVR/NVR",font=(FONT,9),text_color=TEXT3).pack(anchor="w",pady=4)

        r3=ctk.CTkFrame(frm,fg_color="transparent"); r3.pack(fill="x",pady=10)
        d1=ctk.CTkFrame(r3,fg_color="transparent"); d1.pack(side="left",expand=True,fill="x",padx=8)
        ctk.CTkLabel(d1,text="DIAS DE RETENÇÃO",font=(FONT,9,"bold"),text_color=TEXT3).pack(anchor="w",pady=5)
        self.v_dias=tk.IntVar(value=30); self.v_dias.trace_add("write",lambda *_:self._calc_cam())
        self._entry(d1,self.v_dias).pack(fill="x")
        d2=ctk.CTkFrame(r3,fg_color="transparent"); d2.pack(side="left",expand=True,fill="x")
        ctk.CTkLabel(d2,text="HORAS/DIA",font=(FONT,9,"bold"),text_color=TEXT3).pack(anchor="w",pady=5)
        self.v_horas=tk.IntVar(value=24); self.v_horas.trace_add("write",lambda *_:self._calc_cam())
        self._entry(d2,self.v_horas).pack(fill="x")

        self._upd_cam()

        right=ctk.CTkFrame(body,fg_color="transparent"); right.grid(row=0,column=1,sticky="nsew")
        ctk.CTkLabel(right,text="Resultado",font=(FONT,12,"bold"),text_color=TEXT1).pack(anchor="w",pady=10)
        g=ctk.CTkFrame(right,fg_color="transparent"); g.pack(fill="x",pady=10)
        g.columnconfigure(0,weight=1); g.columnconfigure(1,weight=1)
        self.mc_cbt=MetricCard(g,"Bitrate Total"); self.mc_cbt.grid(row=0,column=0,sticky="ew",padx=8,pady=8)
        self.mc_cpd=MetricCard(g,"Por câmera / dia"); self.mc_cpd.grid(row=0,column=1,sticky="ew",pady=8)
        self.mc_cst=MetricCard(g,"Total Necessário"); self.mc_cst.grid(row=1,column=0,sticky="ew",padx=8)
        self.mc_cd1=MetricCard(g,"Dias com 1 TB"); self.mc_cd1.grid(row=1,column=1,sticky="ew")
        self.cam_sum=InfoBox(right); self.cam_sum.lbl.configure(wraplength=440); self.cam_sum.pack(fill="x",pady=10)

    def _upd_cam(self):
        try: cur=int(self.v_ncam.get())
        except: return
        self._upd_q(self._cam_q,cur)

    def _calc_cam(self,*_):
        try:
            ncam=int(self.v_ncam.get()); res=RES_MAP.get(self.v_res.get(),2)
            comp=COMP_MAP.get(self.v_comp.get(),0.5); fps=int(self.v_fps.get().replace(" fps",""))
            dias=int(self.v_dias.get()); horas=int(self.v_horas.get())
        except: return
        self._upd_cam()
        br=float(self.v_bitrate.get())
        mbps=(br*ncam)/1000; gb_cam=(br*3600*horas)/(8*1024*1024)
        total_tb=(gb_cam*ncam*dias)/1024; d1tb=(1024/(gb_cam*ncam)) if gb_cam*ncam>0 else 0
        self.mc_cbt.set(f"{mbps:.1f} Mbps",f"{br:.0f} Kbps por câmera",GREEN_PRIMARY)
        self.mc_cpd.set(fmt(gb_cam,"GB"),"por câmera por dia",TEXT1)
        self.mc_cst.set(fmt(total_tb),f"{ncam} câm. × {dias} dias x {horas}h",AMBER)
        self.mc_cd1.set(f"{d1tb:.1f} dias","de gravação por 1 TB",GREEN_PRIMARY)
        self.cam_sum.set(
            f"  {ncam} câmera{'s' if ncam>1 else ''}  |  {self.v_res.get()}  |  {self.v_comp.get()}  |  {fps} fps\n"
            f"  Retenção: {dias} dias x {horas}h/dia  |  Bitrate: {br:.0f} Kbps/câmera\n"
            f"  Armazenamento total necessário: {fmt(total_tb)}")
        self._upd_combined()

    # ──────────────────────────────────────────── COMBINED ──────────────────
    def _combined_panel(self):
        p=ctk.CTkScrollableFrame(self.content,fg_color="transparent",scrollbar_button_color=BORDER)
        self._panels["combinado"]=p
        ctk.CTkLabel(p,text="Análise Combinada",font=(FONT,16,"bold"),text_color=TEXT1).pack(anchor="w")
        ctk.CTkLabel(p,text="Comparação entre volume disponível no RAID e o necessário pelas câmeras",
                     font=(FONT,10),text_color=TEXT2).pack(anchor="w",pady=16)

        top=ctk.CTkFrame(p,fg_color="transparent"); top.pack(fill="x",pady=12)
        top.columnconfigure(0,weight=1); top.columnconfigure(1,weight=1); top.columnconfigure(2,weight=1)
        self.mc_xr=MetricCard(top,"Disponível no RAID"); self.mc_xr.grid(row=0,column=0,sticky="ew",padx=8)
        self.mc_xc=MetricCard(top,"Necessário pelas Câmeras"); self.mc_xc.grid(row=0,column=1,sticky="ew",padx=8)
        self.mc_xl=MetricCard(top,"Saldo / Deficit"); self.mc_xl.grid(row=0,column=2,sticky="ew")

        vc=self._card(p); vc.pack(fill="x",pady=12)
        vr=ctk.CTkFrame(vc,fg_color="transparent"); vr.pack(fill="x",padx=18,pady=16)
        self.lbl_vi=ctk.CTkLabel(vr,text="",font=(FONT,26)); self.lbl_vi.pack(side="left")
        vt=ctk.CTkFrame(vr,fg_color="transparent"); vt.pack(side="left",padx=12)
        self.lbl_vt=ctk.CTkLabel(vt,text="Configure o RAID e as câmeras para ver a análise",
                                  font=(FONT,12,"bold"),text_color=TEXT2); self.lbl_vt.pack(anchor="w")
        self.lbl_vs=ctk.CTkLabel(vt,text="",font=(FONT,10),text_color=TEXT2,wraplength=600,justify="left")
        self.lbl_vs.pack(anchor="w",pady=4)

        gc=self._card(p); gc.pack(fill="x",pady=12)
        gt=ctk.CTkFrame(gc,fg_color="transparent"); gt.pack(fill="x",padx=16,pady=14)
        ctk.CTkLabel(gt,text="Utilização do Storage RAID",font=(FONT,10,"bold"),text_color=TEXT2).pack(side="left")
        self.lbl_gpct=ctk.CTkLabel(gt,text="0%",font=(FONT,11,"bold"),text_color=GREEN_PRIMARY); self.lbl_gpct.pack(side="right")
        self.pb_comb=ctk.CTkProgressBar(gc,fg_color=BG_FIELD,progress_color=GREEN_PRIMARY,height=10,corner_radius=5)
        self.pb_comb.pack(fill="x",padx=16,pady=16); self.pb_comb.set(0)

        tc=self._card(p,"Resumo Técnico"); tc.pack(fill="x")
        tf=ctk.CTkFrame(tc,fg_color="transparent"); tf.pack(fill="x",padx=18,pady=10)
        self._tbl=[]
        for i,lbl in enumerate(["RAID configurado","Volume RAID disponível","Número de câmeras","Armazenamento necessário","Saldo de espaço","Taxa de utilização"]):
            row=ctk.CTkFrame(tf,fg_color=BG_FIELD if i%2==0 else "transparent",corner_radius=4); row.pack(fill="x",pady=1)
            ctk.CTkLabel(row,text=lbl,font=(FONT,10),text_color=TEXT3,width=220,anchor="w").pack(side="left",padx=10,pady=7)
            v=ctk.CTkLabel(row,text="--",font=(FONT,10,"bold"),text_color=TEXT1); v.pack(side="right",padx=10)
            self._tbl.append(v)

        # Botão exportar PDF
        pdf_row=ctk.CTkFrame(p,fg_color="transparent"); pdf_row.pack(fill="x",pady=16)
        self.btn_pdf=ctk.CTkButton(pdf_row,text="  Exportar Relatório PDF",
                                   command=self._export_pdf,
                                   fg_color=GREEN_PRIMARY,hover_color=GREEN_DARK,
                                   text_color=WHITE,font=(FONT,12,"bold"),
                                   corner_radius=8,height=42,width=260)
        self.btn_pdf.pack(side="left")
        self.lbl_pdf_status=ctk.CTkLabel(pdf_row,text="",font=(FONT,10),text_color=TEXT2)
        self.lbl_pdf_status.pack(side="left",padx=14)

    def _upd_combined(self):
        try: n=int(self.v_nhd.get()); hs=int(self.v_hs.get())
        except: return
        tam = self._get_tam()
        raid=self.v_raid.get()
        if raid not in RAID_DATA: return
        _,_,min_d,calc=RAID_DATA[raid]
        dr=max(n-hs,1) if hs>0 else n
        util_tb=calc(dr,tam) if dr>=min_d else 0
        try:
            ncam=int(self.v_ncam.get()); res=RES_MAP.get(self.v_res.get(),2)
            comp=COMP_MAP.get(self.v_comp.get(),0.5); fps=int(self.v_fps.get().replace(" fps",""))
            dias=int(self.v_dias.get()); horas=int(self.v_horas.get())
            br=float(self.v_bitrate.get())
            cam_tb=(br*3600*horas*ncam*dias)/(8*1024*1024*1024)
        except: return
        livre=util_tb-cam_tb; pct=min((cam_tb/util_tb)*100,100) if util_tb>0 else 0
        col=GREEN_PRIMARY if pct<70 else AMBER if pct<90 else RED
        self.mc_xr.set(fmt(util_tb),"volume RAID disponível",GREEN_PRIMARY)
        self.mc_xc.set(fmt(cam_tb),"necessário para câmeras",AMBER)
        if livre>=0:
            self.mc_xl.set(f"+{fmt(livre)}","espaço livre",GREEN_PRIMARY)
            self.lbl_vt.configure(text=f"Storage suficiente  -  {fmt(livre)} de margem disponível",text_color=GREEN_PRIMARY)
            self.lbl_vs.configure(text=f"O RAID fornece {fmt(util_tb)} e as cameras precisam de {fmt(cam_tb)}. Utilizacao de {pct:.1f}%.")
        else:
            self.mc_xl.set(f"-{fmt(abs(livre))}","déficit!",RED)
            self.lbl_vt.configure(text=f"Storage insuficiente  -  deficit de {fmt(abs(livre))}",text_color=RED)
            self.lbl_vs.configure(text=f"O RAID tem {fmt(util_tb)}, mas as cameras exigem {fmt(cam_tb)}. Adicione HDs ou reduza câmeras/retenção.")
        self.pb_comb.set(pct/100); self.pb_comb.configure(progress_color=col)
        self.lbl_gpct.configure(text=f"{pct:.1f}%",text_color=col)
        vals=[raid,fmt(util_tb),f"{ncam} cameras",fmt(cam_tb),f"+{fmt(livre)}" if livre>=0 else f"-{fmt(abs(livre))}",f"{pct:.1f}%"]
        cols=[TEXT1,GREEN_PRIMARY,TEXT1,AMBER,GREEN_PRIMARY if livre>=0 else RED,col]
        for lb,v,c in zip(self._tbl,vals,cols): lb.configure(text=v,text_color=c)


    def _export_pdf(self):
        if not REPORTLAB_OK:
            messagebox.showerror("Erro", "Biblioteca ReportLab nao encontrada.\nInstale com: pip install reportlab")
            return

        # Coletar dados atuais
        try:
            n     = int(self.v_nhd.get())
            tam   = self._get_tam()
            tam_fab = float(self.v_thd.get().replace(" TB",""))
            hs    = int(self.v_hs.get())
            raid  = self.v_raid.get()
            ncam  = int(self.v_ncam.get())
            res   = self.v_res.get()
            comp  = self.v_comp.get()
            fps   = self.v_fps.get()
            dias  = int(self.v_dias.get())
            horas = int(self.v_horas.get())
            br    = float(self.v_bitrate.get())
        except:
            messagebox.showerror("Erro", "Preencha todos os campos antes de exportar.")
            return

        sub,desc,min_d,calc = RAID_DATA.get(raid, ("","",1,lambda d,t:d*t))
        dr       = max(n-hs,1) if hs>0 else n
        bruto    = dr*tam
        util_tb  = calc(dr,tam) if dr>=min_d else 0
        efic     = round((util_tb/bruto)*100) if bruto>0 else 0
        gb_cam   = (br*3600*horas)/(8*1024*1024)
        cam_tb   = (gb_cam*ncam*dias)/1024
        mbps     = (br*ncam)/1000
        d1tb     = (1024/(gb_cam*ncam)) if gb_cam*ncam>0 else 0
        livre    = util_tb - cam_tb
        pct      = min((cam_tb/util_tb)*100,100) if util_tb>0 else 0

        # Escolher local para salvar
        filepath = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF","*.pdf")],
            initialfile=f"Intelbras_Storage_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
            title="Salvar relatório PDF"
        )
        if not filepath:
            return

        self.btn_pdf.configure(text="  Gerando PDF...", state="disabled")
        self.update()

        try:
            # ── Cores — PDF tema claro profissional ──────────────────────────
            C_GREEN   = colors.HexColor("#00A335")   # verde Intelbras
            C_GDARK   = colors.HexColor("#005C2B")   # verde escuro (cabeçalhos)
            C_GLIGHT  = colors.HexColor("#E8F5ED")   # verde claro (linhas pares)
            C_BG      = colors.white                  # fundo branco
            C_CARD    = colors.HexColor("#F4FAF6")   # fundo de seção
            C_TEXT1   = colors.HexColor("#1A2E1A")   # texto principal escuro
            C_TEXT2   = colors.HexColor("#2E5C3A")   # texto secundário verde-escuro
            C_TEXT3   = colors.HexColor("#5A7A62")   # labels
            C_AMBER   = colors.HexColor("#B45309")   # âmbar escuro (legível)
            C_RED     = colors.HexColor("#B91C1C")   # vermelho escuro
            C_WHITE   = colors.white
            C_BORDER  = colors.HexColor("#B2D8BE")   # borda verde claro
            C_ROW1    = colors.HexColor("#EAF5EE")   # linha par
            C_ROW2    = colors.white                  # linha ímpar

            doc = SimpleDocTemplate(
                filepath, pagesize=A4,
                leftMargin=1.8*cm, rightMargin=1.8*cm,
                topMargin=1.5*cm, bottomMargin=2*cm
            )

            W = A4[0] - 3.6*cm

            styles = getSampleStyleSheet()
            def sty(name,size,color=C_TEXT1,bold=False,align=TA_LEFT,space_before=0,space_after=4):
                return ParagraphStyle(name,fontName="Helvetica-Bold" if bold else "Helvetica",
                                      fontSize=size,textColor=color,alignment=align,
                                      spaceAfter=space_after,spaceBefore=space_before,leading=size+4)

            s_title   = sty("t",20,C_GREEN,True,TA_LEFT,0,2)
            s_sub     = sty("s",10,C_TEXT2,False,TA_LEFT,0,10)
            s_section = sty("sec",12,C_GDARK,True,TA_LEFT,14,6)
            s_body    = sty("b",9,C_TEXT2,False,TA_LEFT,0,3)
            s_value   = sty("v",9,C_TEXT1,True,TA_RIGHT,0,3)
            s_verdict = sty("vd",11,C_GREEN if livre>=0 else C_RED,True,TA_CENTER,0,4)
            s_center  = sty("c",9,C_TEXT2,False,TA_CENTER,0,3)

            story = []

            # ── Cabeçalho ───────────────────────────────────────────────────
            hdr_data = [[
                Paragraph("<b><font color='#00A335' size=18>INTELBRAS</font></b><br/><font color='#8FB898' size=9>Storage &amp; CFTV Calculator</font>", styles["Normal"]),
                Paragraph(f"<font color='#8FB898' size=8>Relatório gerado em<br/>{datetime.now().strftime('%d/%m/%Y às %H:%M')}</font>", ParagraphStyle("r",alignment=TA_RIGHT,fontSize=8,textColor=C_TEXT2,leading=12)),
            ]]
            hdr_tbl = Table(hdr_data, colWidths=[W*0.6, W*0.4])
            hdr_tbl.setStyle(TableStyle([
                ("BACKGROUND",(0,0),(-1,-1),C_GLIGHT),
                ("TOPPADDING",(0,0),(-1,-1),14),
                ("BOTTOMPADDING",(0,0),(-1,-1),14),
                ("LEFTPADDING",(0,0),(0,-1),16),
                ("RIGHTPADDING",(-1,0),(-1,-1),16),
                ("LINEBELOW",(0,0),(-1,-1),3,C_GREEN),
            ]))
            story.append(hdr_tbl)
            story.append(Spacer(1,14))

            # ── Veredicto ───────────────────────────────────────────────────
            vcol = C_GREEN if livre>=0 else C_RED
            vbg  = colors.HexColor("#E8F5ED") if livre>=0 else colors.HexColor("#FEE2E2")
            vtext = f"✔  Storage suficiente — {fmt(livre)} de margem disponível" if livre>=0 else f"⚠  Storage insuficiente — déficit de {fmt(abs(livre))}"
            vd = Table([[Paragraph(f"<b><font color='{'#00A335' if livre>=0 else '#E53935'}' size=12>{vtext}</font></b>", styles["Normal"])]],
                       colWidths=[W])
            vd.setStyle(TableStyle([
                ("BACKGROUND",(0,0),(-1,-1),vbg),
                ("TOPPADDING",(0,0),(-1,-1),12),("BOTTOMPADDING",(0,0),(-1,-1),12),
                ("LEFTPADDING",(0,0),(-1,-1),16),
                ("LINEAFTER",(0,0),(0,-1),4,vcol),
                ("LINEBEFORE",(0,0),(0,-1),4,vcol),
            ]))
            story.append(vd)
            story.append(Spacer(1,14))

            # ── Análise Combinada ────────────────────────────────────────────
            story.append(Paragraph("Análise Combinada", s_section))
            pct_bar = int(min(pct,100))
            bar_col = "#00A335" if pct<70 else "#F59E0B" if pct<90 else "#E53935"
            comb_data = [
                ["Disponível no RAID", fmt(util_tb), "Necessário pelas Câmeras", fmt(cam_tb)],
                ["Saldo de Espaço", f"+{fmt(livre)}" if livre>=0 else f"−{fmt(abs(livre))}", "Taxa de Utilização", f"{pct:.1f}%"],
            ]
            comb_tbl = Table(comb_data, colWidths=[W*0.28, W*0.22, W*0.28, W*0.22])
            comb_tbl.setStyle(TableStyle([
                ("BACKGROUND",(0,0),(0,-1),C_CARD),("BACKGROUND",(2,0),(2,-1),C_CARD),
                ("BACKGROUND",(1,0),(1,-1),C_ROW1),("BACKGROUND",(3,0),(3,-1),C_ROW1),
                ("FONTNAME",(0,0),(0,-1),"Helvetica"),("FONTNAME",(2,0),(2,-1),"Helvetica"),
                ("FONTNAME",(1,0),(1,-1),"Helvetica-Bold"),("FONTNAME",(3,0),(3,-1),"Helvetica-Bold"),
                ("FONTSIZE",(0,0),(-1,-1),9),
                ("TEXTCOLOR",(0,0),(0,-1),C_TEXT3),("TEXTCOLOR",(2,0),(2,-1),C_TEXT3),
                ("TEXTCOLOR",(1,0),(1,-1),C_GREEN),("TEXTCOLOR",(3,0),(3,-1),C_AMBER),
                ("ALIGN",(1,0),(1,-1),"RIGHT"),("ALIGN",(3,0),(3,-1),"RIGHT"),
                ("TOPPADDING",(0,0),(-1,-1),8),("BOTTOMPADDING",(0,0),(-1,-1),8),
                ("LEFTPADDING",(0,0),(-1,-1),10),("RIGHTPADDING",(0,0),(-1,-1),10),
                ("GRID",(0,0),(-1,-1),0.5,C_BORDER),
            ]))
            story.append(comb_tbl)
            story.append(Spacer(1,6))

            # Barra de utilização
            bar_label = f"Utilização do Storage RAID: {pct:.1f}%"
            bar_data = [[Paragraph(f"<font color='#8FB898' size=8>{bar_label}</font>", styles["Normal"])]]
            bar_tbl = Table(bar_data, colWidths=[W])
            bar_tbl.setStyle(TableStyle([
                ("BACKGROUND",(0,0),(-1,-1),C_GLIGHT),
                ("TOPPADDING",(0,0),(-1,-1),6),("BOTTOMPADDING",(0,0),(-1,-1),2),
                ("LEFTPADDING",(0,0),(-1,-1),10),
            ]))
            story.append(bar_tbl)

            # Barra visual
            bar_w = W - 20
            fill_w = (pct_bar/100) * bar_w
            bar_bg   = Table([[""]],colWidths=[W])
            bar_bg.setStyle(TableStyle([
                ("BACKGROUND",(0,0),(-1,-1),C_BORDER),
                ("TOPPADDING",(0,0),(-1,-1),0),("BOTTOMPADDING",(0,0),(-1,-1),0),
                ("LINEBELOW",(0,0),(-1,-1),10,colors.HexColor(bar_col)),
                ("LEFTPADDING",(0,0),(-1,-1),10),
            ]))
            story.append(bar_bg)
            story.append(Spacer(1,14))

            # ── Configuração RAID ─────────────────────────────────────────
            story.append(Paragraph("Configuração do Array RAID", s_section))
            raid_rows = [
                ["Parâmetro","Valor","Parâmetro","Valor"],
                ["Tipo de RAID", raid, "HDs ativos no array", str(dr)],
                ["Capacidade por HD (fab.)", f"{tam_fab:.1f} TB", "Hot Spare(s)", f"{hs} HD(s) = {hs*tam_fab*FATOR_UTIL:.2f} TB úteis"],
                ["Capacidade por HD (útil)", f"{tam:.2f} TB  (×0,90)", "Volume disponível", fmt(util_tb)],
                ["Capacidade bruta (útil)", fmt(n*tam), "Overhead RAID", fmt(bruto-util_tb)],
                ["Eficiência RAID", f"{efic}%", "Nível de proteção", desc],
            ]
            r_tbl = Table(raid_rows, colWidths=[W*0.28, W*0.22, W*0.28, W*0.22])
            rs = [
                ("BACKGROUND",(0,0),(-1,0),C_GDARK),
                ("TEXTCOLOR",(0,0),(-1,0),C_WHITE),
                ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
                ("FONTSIZE",(0,0),(-1,-1),9),
                ("ALIGN",(1,0),(1,-1),"RIGHT"),("ALIGN",(3,0),(3,-1),"RIGHT"),
                ("TOPPADDING",(0,0),(-1,-1),7),("BOTTOMPADDING",(0,0),(-1,-1),7),
                ("LEFTPADDING",(0,0),(-1,-1),10),("RIGHTPADDING",(0,0),(-1,-1),10),
                ("GRID",(0,0),(-1,-1),0.5,C_BORDER),
                ("FONTNAME",(1,1),(1,-1),"Helvetica-Bold"),("TEXTCOLOR",(1,1),(1,-1),C_GREEN),
                ("FONTNAME",(3,1),(3,-1),"Helvetica-Bold"),("TEXTCOLOR",(3,1),(3,-1),C_GREEN),
            ]
            for i in range(1,len(raid_rows)):
                bg = C_ROW1 if i%2==0 else C_ROW2
                rs.append(("BACKGROUND",(0,i),(-1,i),bg))
                rs.append(("TEXTCOLOR",(0,i),(0,i),C_TEXT3))
                rs.append(("TEXTCOLOR",(2,i),(2,i),C_TEXT3))
            r_tbl.setStyle(TableStyle(rs))
            story.append(r_tbl)
            story.append(Spacer(1,14))

            # ── Configuração Câmeras ──────────────────────────────────────
            story.append(Paragraph("Configuração das Câmeras & Gravação", s_section))
            cam_rows = [
                ["Parâmetro","Valor","Parâmetro","Valor"],
                ["Número de câmeras", str(ncam), "Resolução", res],
                ["Compressão", comp, "FPS", fps],
                ["Bitrate por câmera", f"{br:.0f} Kbps", "Bitrate total", f"{mbps:.1f} Mbps"],
                ["Dias de retenção", f"{dias} dias", "Horas/dia gravando", f"{horas}h"],
                ["Por câmera / dia", fmt(gb_cam,"GB"), "Armazenamento total", fmt(cam_tb)],
                ["Dias com 1 TB", f"{d1tb:.1f} dias", "", ""],
            ]
            c_tbl = Table(cam_rows, colWidths=[W*0.28, W*0.22, W*0.28, W*0.22])
            cs = [
                ("BACKGROUND",(0,0),(-1,0),C_GDARK),
                ("TEXTCOLOR",(0,0),(-1,0),C_WHITE),
                ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
                ("FONTSIZE",(0,0),(-1,-1),9),
                ("ALIGN",(1,0),(1,-1),"RIGHT"),("ALIGN",(3,0),(3,-1),"RIGHT"),
                ("TOPPADDING",(0,0),(-1,-1),7),("BOTTOMPADDING",(0,0),(-1,-1),7),
                ("LEFTPADDING",(0,0),(-1,-1),10),("RIGHTPADDING",(0,0),(-1,-1),10),
                ("GRID",(0,0),(-1,-1),0.5,C_BORDER),
                ("FONTNAME",(1,1),(1,-1),"Helvetica-Bold"),("TEXTCOLOR",(1,1),(1,-1),C_GREEN),
                ("FONTNAME",(3,1),(3,-1),"Helvetica-Bold"),("TEXTCOLOR",(3,1),(3,-1),C_GREEN),
            ]
            for i in range(1,len(cam_rows)):
                bg = C_ROW1 if i%2==0 else C_ROW2
                cs.append(("BACKGROUND",(0,i),(-1,i),bg))
                cs.append(("TEXTCOLOR",(0,i),(0,i),C_TEXT3))
                cs.append(("TEXTCOLOR",(2,i),(2,i),C_TEXT3))
            c_tbl.setStyle(TableStyle(cs))
            story.append(c_tbl)
            story.append(Spacer(1,20))

            # ── Rodapé ───────────────────────────────────────────────────
            ft_data = [[
                Paragraph("<font color='#4A6B52' size=7>Intelbras Storage Calculator v3.0 PRO  |  Valores estimados para dimensionamento técnico</font>", styles["Normal"]),
                Paragraph(f"<font color='#4A6B52' size=7>© 2025 Intelbras  |  {datetime.now().strftime('%d/%m/%Y')}</font>",
                          ParagraphStyle("fr",alignment=TA_RIGHT,fontSize=7,textColor=C_TEXT3,leading=10)),
            ]]
            ft_tbl = Table(ft_data, colWidths=[W*0.7,W*0.3])
            ft_tbl.setStyle(TableStyle([
                ("LINEABOVE",(0,0),(-1,0),1,C_GDARK),
                ("TOPPADDING",(0,0),(-1,-1),8),
                ("LEFTPADDING",(0,0),(0,-1),0),
                ("RIGHTPADDING",(-1,0),(-1,-1),0),
            ]))
            story.append(ft_tbl)

            doc.build(story)

            self.lbl_pdf_status.configure(text=f"✔  Salvo com sucesso!", text_color=GREEN_PRIMARY)
            self.btn_pdf.configure(text="  Exportar Relatório PDF", state="normal")

        except Exception as e:
            self.btn_pdf.configure(text="  Exportar Relatório PDF", state="normal")
            self.lbl_pdf_status.configure(text=f"Erro: {str(e)[:60]}", text_color="#E53935")
            messagebox.showerror("Erro ao gerar PDF", str(e))

    def _footer(self):
        # Guardar referência do footer para o toggle conseguir reposicioná-lo
        self._footer_frame = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
        self._footer_frame.pack(fill="x", side="bottom")
        ctk.CTkFrame(self._footer_frame,fg_color=GREEN_DARKER,height=2,corner_radius=0).pack(fill="x")
        ft=ctk.CTkFrame(self._footer_frame,fg_color=BG_PANEL,height=32,corner_radius=0)
        ft.pack(fill="x"); ft.pack_propagate(False)
        ctk.CTkLabel(ft,text="Intelbras Storage Calculator  |  Valores estimados para dimensionamento técnico",
                     font=(FONT,9),text_color=TEXT3).pack(side="left",padx=20,pady=8)
        ctk.CTkLabel(ft,text="© 2025 Intelbras  |  v3.0 PRO",font=(FONT,9),text_color=TEXT3).pack(side="right",padx=20)

if __name__=="__main__":
    app=App(); app.mainloop()
