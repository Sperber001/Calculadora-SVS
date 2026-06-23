import tkinter as tk
from tkinter import ttk, font as tkfont
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

# ── RAID / CAM DATA ────────────────────────────────────────────────────────
RAID_DATA = {
    "RAID 0":  ("Striping — sem redundância",       "Todo espaço disponível. Se 1 HD falhar, perde tudo.", 1,   lambda d,t: d*t),
    "RAID 1":  ("Mirroring — espelho total",         "Tolera falha de metade dos discos. Mín. 2 HDs.",      2,   lambda d,t: math.floor(d/2)*t),
    "RAID 5":  ("Paridade simples distribuída",      "Tolera falha de 1 disco. 1 HD para paridade. Mín. 3 HDs.", 3, lambda d,t: (d-1)*t),
    "RAID 6":  ("Dupla paridade distribuída",        "Tolera falha de 2 discos. 2 HDs para paridade. Mín. 4 HDs.", 4, lambda d,t: (d-2)*t),
    "RAID 10": ("Mirror + Stripe combinados",        "Alta performance e redundância. Mín. 4 HDs (par).",   4,   lambda d,t: (d//2)*t),
    "JBOD":    ("Discos independentes, sem RAID",    "Sem redundância. Capacidade total de todos os HDs.",  1,   lambda d,t: d*t),
}
TB_SIZES   = [0.5,1,2,3,4,6,8,10,12,14,16,18,20]
RES_MAP    = {"D1 / CIF — 0.5 MP":0.5,"720p HD — 1 MP":1,"1080p Full HD — 2 MP":2,
              "4 MP":4,"3K / 5 MP":5,"4K Ultra HD — 8 MP":8,"12 MP":12}
COMP_MAP   = {"H.265 / H.265+":0.5,"H.264":1.0,"MJPEG":1.5}
BR_BASE    = {0.5:512,1:1024,2:2048,4:4096,5:5120,8:8192,12:12288}

def fmt(v, unit="TB"):
    if unit == "TB":
        if v >= 1000: return f"{v/1000:.1f} PB"
        if v >= 1:    return f"{v:.2f} TB"
        return f"{v*1024:.0f} GB"
    if unit == "GB":
        if v >= 1024: return f"{v/1024:.2f} TB"
        return f"{v:.1f} GB"
    return str(v)

# ── CUSTOM WIDGETS ─────────────────────────────────────────────────────────
class HoverButton(tk.Label):
    def __init__(self, parent, text, command=None, style="primary", **kw):
        self.styles = {
            "primary":   (ACCENT,  ACCENT2, WHITE),
            "secondary": (BG4,     BG3,     TEXT1),
            "ghost":     ("",      BG4,     TEXT2),
            "success":   (GREEN,   GREEN2,  "#052E16"),
            "info":      (BLUE,    BLUE2,   WHITE),
        }
        bg, hbg, fg = self.styles.get(style, self.styles["primary"])
        self._bg = bg; self._hbg = hbg; self._fg = fg
        self._cmd = command
        super().__init__(parent, text=text, fg=fg,
                         bg=bg if bg else parent.cget("bg"),
                         font=(FONT, 10, "bold"), cursor="hand2",
                         padx=18, pady=8, **kw)
        self.bind("<Enter>",    self._on)
        self.bind("<Leave>",    self._off)
        self.bind("<Button-1>", self._click)

    def _on(self, _=None):
        self.config(bg=self._hbg if self._hbg else self.master.cget("bg"), fg=WHITE)
    def _off(self, _=None):
        self.config(bg=self._bg if self._bg else self.master.cget("bg"), fg=self._fg)
    def _click(self, _=None):
        if self._cmd: self._cmd()

class Divider(tk.Frame):
    def __init__(self, parent, **kw):
        super().__init__(parent, bg=CARD_BORDER, height=1, **kw)

class Card(tk.Frame):
    def __init__(self, parent, **kw):
        super().__init__(parent, bg=CARD, highlightbackground=CARD_BORDER,
                         highlightthickness=1, **kw)

class MetricCard(tk.Frame):
    def __init__(self, parent, label, icon="●", **kw):
        super().__init__(parent, bg=BG3, highlightbackground=CARD_BORDER,
                         highlightthickness=1, **kw)
        top = tk.Frame(self, bg=BG3)
        top.pack(fill="x", padx=14, pady=(14,4))
        tk.Label(top, text=icon, font=(FONT,10), fg=TEXT3, bg=BG3).pack(side="left")
        tk.Label(top, text=label, font=(FONT,9), fg=TEXT2, bg=BG3).pack(side="left", padx=6)
        self.val_lbl = tk.Label(self, text="—", font=(FONT,22,"bold"), fg=TEXT1, bg=BG3)
        self.val_lbl.pack(anchor="w", padx=14)
        self.sub_lbl = tk.Label(self, text="", font=(FONT,8), fg=TEXT3, bg=BG3)
        self.sub_lbl.pack(anchor="w", padx=14, pady=(0,14))

    def set(self, val, sub="", color=TEXT1):
        self.val_lbl.config(text=val, fg=color)
        self.sub_lbl.config(text=sub)

class StyledCombo(ttk.Combobox):
    def __init__(self, parent, var, values, cmd=None, **kw):
        super().__init__(parent, textvariable=var, values=values,
                         state="readonly", font=(FONT,10), **kw)
        if cmd: self.bind("<<ComboboxSelected>>", lambda e: cmd())

class StyledSpin(ttk.Spinbox):
    def __init__(self, parent, var, mn, mx, step=1, **kw):
        super().__init__(parent, from_=mn, to=mx, increment=step,
                         textvariable=var, font=(FONT,10), **kw)

class ProgressBar(tk.Frame):
    def __init__(self, parent, **kw):
        super().__init__(parent, bg=BG4, height=8, **kw)
        self.fill = tk.Frame(self, bg=GREEN, height=8)
        self.fill.place(x=0, y=0, relheight=1, relwidth=0)

    def set(self, pct):
        pct = max(0, min(pct, 100))
        self.fill.place(relwidth=pct/100)
        if pct < 70:   col = GREEN
        elif pct < 90: col = AMBER
        else:          col = ACCENT
        self.fill.config(bg=col)

# ── FIELD BUILDER ─────────────────────────────────────────────────────────
def field_frame(parent, label):
    f = tk.Frame(parent, bg=CARD)
    f.pack(fill="x", pady=5)
    tk.Label(f, text=label.upper(), font=(FONT,8,"bold"), fg=TEXT3, bg=CARD,
             letterSpacing=2).pack(anchor="w", pady=(0,5))
    return f

# ── MAIN APP ───────────────────────────────────────────────────────────────
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Intelbras Storage Calculator")
        self.configure(bg=BG)
        self.minsize(940, 680)
        try:    self.state("zoomed")
        except: self.geometry("940x700")
        self._setup_styles()
        self._build_header()
        self._build_sidebar()
        self._build_content()
        self._build_footer()
        self._show("raid")
        self.after(120, lambda: (self._calc_raid(), self._calc_cam()))

    # ── STYLES ──────────────────────────────────────────────────────────────
    def _setup_styles(self):
        s = ttk.Style(self)
        s.theme_use("clam")
        for w in ("TCombobox","TSpinbox"):
            s.configure(w,
                fieldbackground=BG4, background=BG4, foreground=TEXT1,
                arrowcolor=TEXT2, bordercolor=CARD_BORDER, lightcolor=CARD_BORDER,
                darkcolor=CARD_BORDER, insertcolor=TEXT1,
                selectbackground=BLUE, selectforeground=WHITE,
                font=(FONT,10), padding=8, relief="flat")
            s.map(w,
                fieldbackground=[("readonly",BG4),("disabled",BG3)],
                foreground=[("disabled",TEXT3)],
                selectbackground=[("readonly",BG4)],
                selectforeground=[("readonly",TEXT1)])

    # ── HEADER ──────────────────────────────────────────────────────────────
    def _build_header(self):
        hdr = tk.Frame(self, bg=BG2, height=64)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)

        # left — logo
        left = tk.Frame(hdr, bg=BG2)
        left.pack(side="left", padx=20, pady=12)

        logo_outer = tk.Frame(left, bg=ACCENT, width=38, height=38)
        logo_outer.pack(side="left")
        logo_outer.pack_propagate(False)
        inner = tk.Frame(logo_outer, bg=WHITE, width=14, height=14)
        inner.place(relx=0.5, rely=0.5, anchor="center")

        info = tk.Frame(left, bg=BG2)
        info.pack(side="left", padx=12)
        tk.Label(info, text="INTELBRAS", font=(FONT,13,"bold"),
                 fg=WHITE, bg=BG2).pack(anchor="w")
        tk.Label(info, text="Storage & CFTV Calculator", font=(FONT,9),
                 fg=TEXT2, bg=BG2).pack(anchor="w")

        # right — badge
        right = tk.Frame(hdr, bg=BG2)
        right.pack(side="right", padx=20)
        badge = tk.Frame(right, bg=BG4, highlightbackground=CARD_BORDER, highlightthickness=1)
        badge.pack()
        tk.Label(badge, text="v2.0  PRO", font=(FONT,9,"bold"),
                 fg=BLUE2, bg=BG4, padx=10, pady=4).pack()

        Divider(self).pack(fill="x")

    # ── SIDEBAR ─────────────────────────────────────────────────────────────
    def _build_sidebar(self):
        self.sidebar = tk.Frame(self, bg=BG2, width=200)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        Divider(self.sidebar).pack(fill="x")

        nav_lbl = tk.Frame(self.sidebar, bg=BG2)
        nav_lbl.pack(fill="x", padx=16, pady=(20,8))
        tk.Label(nav_lbl, text="FERRAMENTAS", font=(FONT,8,"bold"),
                 fg=TEXT3, bg=BG2).pack(anchor="w")

        self._nav_btns = {}
        nav_items = [
            ("raid",      "💾",  "Calculadora RAID"),
            ("cameras",   "📹",  "Câmeras & Gravação"),
            ("combinado", "📊",  "Análise Combinada"),
        ]
        for key, icon, label in nav_items:
            btn = self._make_nav_btn(key, icon, label)
            self._nav_btns[key] = btn

        Divider(self.sidebar).pack(fill="x", pady=16)

        # quick info box
        info = tk.Frame(self.sidebar, bg=BG3, highlightbackground=CARD_BORDER,
                        highlightthickness=1)
        info.pack(fill="x", padx=12, pady=4)
        tk.Label(info, text="Dica rápida", font=(FONT,9,"bold"),
                 fg=BLUE2, bg=BG3, padx=12, pady=(10,4)).pack(anchor="w")
        self.tip_lbl = tk.Label(info, text="Configure o RAID\ne depois as câmeras\npara ver a análise\ncombinada.",
                                font=(FONT,8), fg=TEXT2, bg=BG3,
                                justify="left", wraplength=160, padx=12, pady=(0,12))
        self.tip_lbl.pack(anchor="w")

        Divider(self.sidebar).pack(fill="x", side="bottom")

    def _make_nav_btn(self, key, icon, label):
        frame = tk.Frame(self.sidebar, bg=BG2, cursor="hand2")
        frame.pack(fill="x")

        indicator = tk.Frame(frame, bg=BG2, width=3)
        indicator.pack(side="left", fill="y")

        inner = tk.Frame(frame, bg=BG2)
        inner.pack(side="left", fill="both", expand=True, padx=12, pady=10)

        icon_lbl = tk.Label(inner, text=icon, font=(FONT,14), bg=BG2, fg=TEXT2)
        icon_lbl.pack(side="left")
        text_lbl = tk.Label(inner, text=label, font=(FONT,10), bg=BG2, fg=TEXT2)
        text_lbl.pack(side="left", padx=10)

        def enter(_): 
            if self._active != key:
                frame.config(bg=BG3); inner.config(bg=BG3)
                indicator.config(bg=BG3)
                icon_lbl.config(bg=BG3); text_lbl.config(bg=BG3)
        def leave(_):
            if self._active != key:
                frame.config(bg=BG2); inner.config(bg=BG2)
                indicator.config(bg=BG2)
                icon_lbl.config(bg=BG2); text_lbl.config(bg=BG2)
        def click(_): self._show(key)

        for w in (frame, inner, icon_lbl, text_lbl, indicator):
            w.bind("<Enter>", enter)
            w.bind("<Leave>", leave)
            w.bind("<Button-1>", click)

        return {"frame":frame,"inner":inner,"indicator":indicator,
                "icon":icon_lbl,"text":text_lbl}

    def _show(self, key):
        self._active = key
        for k, w in self._nav_btns.items():
            active = k == key
            bg     = BG3 if active else BG2
            ind    = ACCENT if active else BG2
            fg     = WHITE if active else TEXT2
            wfg    = TEXT1 if active else TEXT2
            for widget in (w["frame"], w["inner"]):
                widget.config(bg=bg)
            w["indicator"].config(bg=ind)
            w["icon"].config(bg=bg, fg=fg)
            w["text"].config(bg=bg, fg=wfg, font=(FONT,10,"bold" if active else "normal"))

        for k, p in self._panels.items():
            if k == key: p.pack(fill="both", expand=True)
            else:        p.pack_forget()

    # ── CONTENT AREA ────────────────────────────────────────────────────────
    def _build_content(self):
        self._active = ""
        self._panels = {}

        self.main = tk.Frame(self, bg=BG)
        self.main.pack(side="left", fill="both", expand=True)

        self._build_raid_panel()
        self._build_cam_panel()
        self._build_combined_panel()

    # ── SECTION HEADER ──────────────────────────────────────────────────────
    def _section_header(self, parent, title, subtitle=""):
        hdr = tk.Frame(parent, bg=BG)
        hdr.pack(fill="x", padx=24, pady=(20,16))
        tk.Label(hdr, text=title, font=(FONT,16,"bold"),
                 fg=TEXT1, bg=BG).pack(anchor="w")
        if subtitle:
            tk.Label(hdr, text=subtitle, font=(FONT,10),
                     fg=TEXT2, bg=BG).pack(anchor="w", pady=(2,0))
        Divider(parent).pack(fill="x", padx=24)

    # ── RAID PANEL ──────────────────────────────────────────────────────────
    def _build_raid_panel(self):
        p = tk.Frame(self.main, bg=BG)
        self._panels["raid"] = p

        self._section_header(p, "Calculadora RAID",
            "Configure os discos e o tipo de array para calcular o volume disponível")

        body = tk.Frame(p, bg=BG)
        body.pack(fill="both", expand=True, padx=24, pady=16)
        body.columnconfigure(0, weight=2)
        body.columnconfigure(1, weight=3)
        body.rowconfigure(0, weight=1)

        # ── LEFT: inputs ──
        left = Card(body)
        left.grid(row=0, column=0, sticky="nsew", padx=(0,12))

        tk.Label(left, text="Configuração dos Discos", font=(FONT,11,"bold"),
                 fg=TEXT1, bg=CARD, padx=20, pady=16).pack(anchor="w")
        Divider(left).pack(fill="x")

        form = tk.Frame(left, bg=CARD, padx=20, pady=16)
        form.pack(fill="x")

        # num HDs
        ff = field_frame(form, "Número de HDs")
        self.v_nhd = tk.IntVar(value=4)
        self.v_nhd.trace_add("write", lambda *_: self._calc_raid())
        row = tk.Frame(ff, bg=CARD); row.pack(fill="x")
        for val in [2,4,8,12,16,24]:
            v = val
            b = tk.Label(row, text=str(v), font=(FONT,10), bg=BG4, fg=TEXT2,
                         width=4, pady=6, cursor="hand2",
                         highlightbackground=CARD_BORDER, highlightthickness=1)
            b.pack(side="left", padx=(0,4))
            b.bind("<Button-1>", lambda e, x=v: (self.v_nhd.set(x), self._update_nhd_btns()))
            b.bind("<Enter>", lambda e, w=b: w.config(bg=BG3, fg=TEXT1))
            b.bind("<Leave>", lambda e, w=b: self._update_nhd_btns())
        self._nhd_btns_row = row
        # custom entry
        custom_f = tk.Frame(ff, bg=CARD); custom_f.pack(fill="x", pady=(6,0))
        tk.Label(custom_f, text="Personalizado:", font=(FONT,9), fg=TEXT3, bg=CARD).pack(side="left")
        StyledSpin(custom_f, self.v_nhd, 1, 64, width=8).pack(side="left", padx=8)

        # tamanho HD
        ff2 = field_frame(form, "Capacidade por HD")
        self.v_thd = tk.StringVar(value="4 TB")
        self.v_thd.trace_add("write", lambda *_: self._calc_raid())
        StyledCombo(ff2, self.v_thd, [f"{v} TB" for v in TB_SIZES],
                    cmd=self._calc_raid, width=32).pack(fill="x")

        # RAID type — cards visuais
        ff3 = field_frame(form, "Tipo de RAID")
        self.v_raid = tk.StringVar(value="RAID 5")
        raid_grid = tk.Frame(ff3, bg=CARD); raid_grid.pack(fill="x")
        self._raid_btn_widgets = {}
        raids = ["RAID 0","RAID 1","RAID 5","RAID 6","RAID 10","JBOD"]
        for i, r in enumerate(raids):
            col = i % 3; row2 = i // 3
            btn = tk.Frame(raid_grid, bg=BG4, highlightbackground=CARD_BORDER,
                           highlightthickness=1, cursor="hand2")
            btn.grid(row=row2, column=col, padx=(0,6), pady=(0,6), sticky="ew")
            raid_grid.columnconfigure(col, weight=1)
            lbl = tk.Label(btn, text=r, font=(FONT,10,"bold"), bg=BG4, fg=TEXT2,
                           pady=8, cursor="hand2")
            lbl.pack()
            def on_click(e, rv=r): self.v_raid.set(rv); self._update_raid_btns(); self._calc_raid()
            def on_enter(e, bw=btn, lw=lbl, rv=r):
                if self.v_raid.get() != rv:
                    bw.config(highlightbackground=BLUE); lw.config(fg=TEXT1)
            def on_leave(e, bw=btn, lw=lbl, rv=r):
                self._update_raid_btns()
            for w in (btn, lbl):
                w.bind("<Button-1>", on_click)
                w.bind("<Enter>", on_enter)
                w.bind("<Leave>", on_leave)
            self._raid_btn_widgets[r] = (btn, lbl)

        self.lbl_raid_desc = tk.Label(form, text="", font=(FONT,9), fg=TEXT2,
                                      bg=CARD, wraplength=320, justify="left")
        self.lbl_raid_desc.pack(anchor="w", pady=(6,0))

        # Hot Spare
        ff4 = field_frame(form, "Hot Spare")
        hs_row = tk.Frame(ff4, bg=CARD); hs_row.pack(fill="x")
        self.v_hs = tk.BooleanVar(value=False)
        self.v_hs.trace_add("write", lambda *_: self._calc_raid())
        self.hs_btn = HoverButton(hs_row, "  Desativado", style="secondary",
                                  command=self._toggle_hs)
        self.hs_btn.pack(side="left")
        self.hs_info = tk.Label(hs_row, text="", font=(FONT,9), fg=TEXT3, bg=CARD, padx=10)
        self.hs_info.pack(side="left")

        self._update_nhd_btns()
        self._update_raid_btns()

        # ── RIGHT: results ──
        right = tk.Frame(body, bg=BG)
        right.grid(row=0, column=1, sticky="nsew")

        results_title = tk.Frame(right, bg=BG)
        results_title.pack(fill="x", pady=(0,12))
        tk.Label(results_title, text="Resultado do Array", font=(FONT,11,"bold"),
                 fg=TEXT1, bg=BG).pack(side="left")

        grid2 = tk.Frame(right, bg=BG)
        grid2.pack(fill="x", pady=(0,12))
        grid2.columnconfigure(0, weight=1); grid2.columnconfigure(1, weight=1)

        self.mc_discos = MetricCard(grid2, "HDs no Array", "🖴")
        self.mc_discos.grid(row=0, column=0, sticky="ew", padx=(0,8), pady=(0,8))
        self.mc_bruto  = MetricCard(grid2, "Capacidade Bruta", "📦")
        self.mc_bruto.grid(row=0, column=1, sticky="ew", pady=(0,8))
        self.mc_util   = MetricCard(grid2, "Volume Disponível", "✅")
        self.mc_util.grid(row=1, column=0, sticky="ew", padx=(0,8))
        self.mc_efic   = MetricCard(grid2, "Eficiência de Uso", "📈")
        self.mc_efic.grid(row=1, column=1, sticky="ew")

        # usage bar
        bar_card = Card(right)
        bar_card.pack(fill="x", pady=(12,0))
        bar_top = tk.Frame(bar_card, bg=CARD)
        bar_top.pack(fill="x", padx=16, pady=(14,8))
        tk.Label(bar_top, text="Aproveitamento do storage", font=(FONT,9,"bold"),
                 fg=TEXT2, bg=CARD).pack(side="left")
        self.lbl_pct_raid = tk.Label(bar_top, text="", font=(FONT,9,"bold"),
                                     fg=BLUE2, bg=CARD)
        self.lbl_pct_raid.pack(side="right")
        self.pbar_raid = ProgressBar(bar_card)
        self.pbar_raid.pack(fill="x", padx=16, pady=(0,6))
        self.lbl_bar_sub = tk.Label(bar_card, text="", font=(FONT,8),
                                    fg=TEXT3, bg=CARD, padx=16, pady=(0,10))
        self.lbl_bar_sub.pack(anchor="w")

        # info box
        self.info_raid = tk.Label(right, text="", font=(FONT,9), fg=TEXT2, bg=BG3,
                                  wraplength=400, justify="left", padx=14, pady=10,
                                  highlightbackground=CARD_BORDER, highlightthickness=1)
        self.info_raid.pack(fill="x", pady=(12,0))

    def _toggle_hs(self):
        self.v_hs.set(not self.v_hs.get())
        if self.v_hs.get():
            self.hs_btn.config(text="  Ativado", bg=GREEN, fg="#052E16")
            self.hs_info.config(text="1 HD reservado em standby para substituição automática")
        else:
            self.hs_btn.config(text="  Desativado", bg=BG4, fg=TEXT2)
            self.hs_info.config(text="")

    def _update_nhd_btns(self):
        cur = self.v_nhd.get()
        for child in self._nhd_btns_row.winfo_children():
            try:
                val = int(child.cget("text"))
                if val == cur:
                    child.config(bg=ACCENT, fg=WHITE,
                                 highlightbackground=ACCENT, highlightthickness=2)
                else:
                    child.config(bg=BG4, fg=TEXT2,
                                 highlightbackground=CARD_BORDER, highlightthickness=1)
            except: pass

    def _update_raid_btns(self):
        cur = self.v_raid.get()
        for r, (btn, lbl) in self._raid_btn_widgets.items():
            if r == cur:
                btn.config(bg=ACCENT, highlightbackground=ACCENT, highlightthickness=2)
                lbl.config(bg=ACCENT, fg=WHITE)
            else:
                btn.config(bg=BG4, highlightbackground=CARD_BORDER, highlightthickness=1)
                lbl.config(bg=BG4, fg=TEXT2)

    def _calc_raid(self, *_):
        try:
            n   = int(self.v_nhd.get())
            tam = float(self.v_thd.get().replace(" TB","").replace(",","."))
        except: return
        self._update_nhd_btns()
        raid = self.v_raid.get()
        hs   = self.v_hs.get()

        if raid in RAID_DATA:
            subtitle, desc, min_d, calc = RAID_DATA[raid]
            self.lbl_raid_desc.config(text=f"▸  {desc}")
        else:
            return

        dr    = max(n-1,1) if hs else n
        bruto = dr * tam
        err   = ""

        if dr < min_d and raid != "JBOD" and raid != "RAID 0":
            err = f"⚠  {raid} requer mínimo {min_d} HDs no array."
            util = 0
        else:
            try:    util = calc(dr, tam)
            except: util = 0

        efic = round((util/bruto)*100) if bruto > 0 else 0

        self.mc_discos.set(str(dr), "discos ativos no array")
        self.mc_bruto.set(fmt(bruto), f"{bruto:.1f} TB total bruto")

        if err:
            self.mc_util.set("—", err, ACCENT)
            self.mc_efic.set("—", "", TEXT3)
            self.pbar_raid.set(0)
            self.lbl_pct_raid.config(text="0%")
            self.lbl_bar_sub.config(text=err)
            self.info_raid.config(text=err, fg=AMBER)
        else:
            col = GREEN if efic >= 75 else AMBER if efic >= 50 else ACCENT
            self.mc_util.set(fmt(util), f"{util:.2f} TB disponíveis para uso", BLUE2)
            self.mc_efic.set(f"{efic}%", "do espaço bruto aproveitado", col)
            self.pbar_raid.set(efic)
            self.lbl_pct_raid.config(text=f"{efic}% aproveitado")
            hs_t = f"  •  1 HD ({tam} TB) reservado como Hot Spare." if hs else ""
            self.lbl_bar_sub.config(
                text=f"{dr} HD(s) × {tam} TB  •  {raid}  •  {subtitle}{hs_t}")
            self.info_raid.config(
                text=f"Capacidade útil: {fmt(util)}   |   Overhead RAID: {fmt(bruto-util)}   |   {efic}% de eficiência",
                fg=TEXT2)
        self._update_combined()

    # ── CAM PANEL ───────────────────────────────────────────────────────────
    def _build_cam_panel(self):
        p = tk.Frame(self.main, bg=BG)
        self._panels["cameras"] = p

        self._section_header(p, "Câmeras & Gravação",
            "Calcule o armazenamento necessário para o seu sistema de CFTV")

        body = tk.Frame(p, bg=BG)
        body.pack(fill="both", expand=True, padx=24, pady=16)
        body.columnconfigure(0, weight=2)
        body.columnconfigure(1, weight=3)
        body.rowconfigure(0, weight=1)

        # ── LEFT ──
        left = Card(body)
        left.grid(row=0, column=0, sticky="nsew", padx=(0,12))
        tk.Label(left, text="Parâmetros de Gravação", font=(FONT,11,"bold"),
                 fg=TEXT1, bg=CARD, padx=20, pady=16).pack(anchor="w")
        Divider(left).pack(fill="x")
        form = tk.Frame(left, bg=CARD, padx=20, pady=16); form.pack(fill="x")

        # câmeras — quick select
        ff = field_frame(form, "Número de câmeras")
        self.v_ncam = tk.IntVar(value=8)
        self.v_ncam.trace_add("write", lambda *_: self._calc_cam())
        cam_row = tk.Frame(ff, bg=CARD); cam_row.pack(fill="x")
        self._cam_btns_row = cam_row
        for val in [4,8,16,32,64]:
            v=val
            b = tk.Label(cam_row, text=str(v), font=(FONT,10), bg=BG4, fg=TEXT2,
                         width=4, pady=6, cursor="hand2",
                         highlightbackground=CARD_BORDER, highlightthickness=1)
            b.pack(side="left", padx=(0,4))
            b.bind("<Button-1>", lambda e, x=v: (self.v_ncam.set(x), self._update_cam_btns()))
            b.bind("<Enter>", lambda e, w=b: w.config(bg=BG3,fg=TEXT1))
            b.bind("<Leave>", lambda e, w=b: self._update_cam_btns())
        cust = tk.Frame(ff, bg=CARD); cust.pack(fill="x", pady=(6,0))
        tk.Label(cust, text="Personalizado:", font=(FONT,9), fg=TEXT3, bg=CARD).pack(side="left")
        StyledSpin(cust, self.v_ncam, 1, 512, width=8).pack(side="left", padx=8)

        # resolução
        ff2 = field_frame(form, "Resolução")
        self.v_res = tk.StringVar(value="1080p Full HD — 2 MP")
        StyledCombo(ff2, self.v_res, list(RES_MAP.keys()), cmd=self._calc_cam, width=32).pack(fill="x")

        # compressão + fps lado a lado
        row2 = tk.Frame(form, bg=CARD); row2.pack(fill="x")
        c1 = tk.Frame(row2, bg=CARD); c1.pack(side="left", expand=True, fill="x", padx=(0,8))
        tk.Label(c1, text="COMPRESSÃO", font=(FONT,8,"bold"), fg=TEXT3, bg=CARD).pack(anchor="w", pady=(5,5))
        self.v_comp = tk.StringVar(value="H.265 / H.265+")
        StyledCombo(c1, self.v_comp, list(COMP_MAP.keys()), cmd=self._calc_cam, width=16).pack(fill="x")

        c2 = tk.Frame(row2, bg=CARD); c2.pack(side="left", expand=True, fill="x")
        tk.Label(c2, text="FPS", font=(FONT,8,"bold"), fg=TEXT3, bg=CARD).pack(anchor="w", pady=(5,5))
        self.v_fps = tk.StringVar(value="15 fps")
        StyledCombo(c2, self.v_fps,
                    ["1 fps","5 fps","10 fps","15 fps","20 fps","25 fps","30 fps"],
                    cmd=self._calc_cam, width=12).pack(fill="x")

        # bitrate
        ff3 = field_frame(form, "Modo de bitrate")
        self.v_bitmode = tk.StringVar(value="Automático")
        StyledCombo(ff3, self.v_bitmode, ["Automático","Manual (Kbps)"],
                    cmd=self._calc_cam, width=32).pack(fill="x")

        self.ff_manual = tk.Frame(form, bg=CARD)
        self.ff_manual.pack(fill="x", pady=(4,0))
        tk.Label(self.ff_manual, text="BITRATE POR CÂMERA (KBPS)",
                 font=(FONT,8,"bold"), fg=TEXT3, bg=CARD).pack(anchor="w", pady=(5,5))
        self.v_bitrate = tk.IntVar(value=2048)
        self.v_bitrate.trace_add("write", lambda *_: self._calc_cam())
        self.spin_bit = StyledSpin(self.ff_manual, self.v_bitrate, 64, 32000, step=64, width=32)
        self.spin_bit.pack(fill="x")

        # retenção
        row3 = tk.Frame(form, bg=CARD); row3.pack(fill="x", pady=(10,0))
        d1 = tk.Frame(row3, bg=CARD); d1.pack(side="left", expand=True, fill="x", padx=(0,8))
        tk.Label(d1, text="DIAS DE RETENÇÃO", font=(FONT,8,"bold"), fg=TEXT3, bg=CARD).pack(anchor="w", pady=(5,5))
        self.v_dias = tk.IntVar(value=30)
        self.v_dias.trace_add("write", lambda *_: self._calc_cam())
        StyledSpin(d1, self.v_dias, 1, 365, width=14).pack(fill="x")

        d2 = tk.Frame(row3, bg=CARD); d2.pack(side="left", expand=True, fill="x")
        tk.Label(d2, text="HORAS/DIA GRAVANDO", font=(FONT,8,"bold"), fg=TEXT3, bg=CARD).pack(anchor="w", pady=(5,5))
        self.v_horas = tk.IntVar(value=24)
        self.v_horas.trace_add("write", lambda *_: self._calc_cam())
        StyledSpin(d2, self.v_horas, 1, 24, width=14).pack(fill="x")

        self._update_cam_btns()

        # ── RIGHT ──
        right = tk.Frame(body, bg=BG)
        right.grid(row=0, column=1, sticky="nsew")
        tk.Label(right, text="Resultado", font=(FONT,11,"bold"),
                 fg=TEXT1, bg=BG).pack(anchor="w", pady=(0,12))

        grid3 = tk.Frame(right, bg=BG); grid3.pack(fill="x", pady=(0,12))
        grid3.columnconfigure(0,weight=1); grid3.columnconfigure(1,weight=1)

        self.mc_cbt  = MetricCard(grid3, "Bitrate Total", "📡")
        self.mc_cbt.grid(row=0, column=0, sticky="ew", padx=(0,8), pady=(0,8))
        self.mc_cpd  = MetricCard(grid3, "Por câmera / dia", "📷")
        self.mc_cpd.grid(row=0, column=1, sticky="ew", pady=(0,8))
        self.mc_cst  = MetricCard(grid3, "Total Necessário", "💽")
        self.mc_cst.grid(row=1, column=0, sticky="ew", padx=(0,8))
        self.mc_cd1  = MetricCard(grid3, "Dias com 1 TB", "📅")
        self.mc_cd1.grid(row=1, column=1, sticky="ew")

        # summary card
        self.cam_summary = Card(right)
        self.cam_summary.pack(fill="x", pady=(12,0))
        self.lbl_cam_sum = tk.Label(self.cam_summary, text="", font=(FONT,9),
                                    fg=TEXT2, bg=CARD, justify="left",
                                    padx=16, pady=14, wraplength=420)
        self.lbl_cam_sum.pack(anchor="w")

    def _update_cam_btns(self):
        cur = self.v_ncam.get()
        for child in self._cam_btns_row.winfo_children():
            try:
                val = int(child.cget("text"))
                if val == cur:
                    child.config(bg=BLUE, fg=WHITE,
                                 highlightbackground=BLUE, highlightthickness=2)
                else:
                    child.config(bg=BG4, fg=TEXT2,
                                 highlightbackground=CARD_BORDER, highlightthickness=1)
            except: pass

    def _calc_cam(self, *_):
        try:
            ncam  = int(self.v_ncam.get())
            res   = RES_MAP.get(self.v_res.get(), 2)
            comp  = COMP_MAP.get(self.v_comp.get(), 0.5)
            fps   = int(self.v_fps.get().replace(" fps",""))
            dias  = int(self.v_dias.get())
            horas = int(self.v_horas.get())
            auto  = self.v_bitmode.get() == "Automático"
        except: return

        self._update_cam_btns()

        if auto:
            br = BR_BASE.get(res, 2048) * comp * (fps/15)
            self.spin_bit.config(state="disabled")
        else:
            br = float(self.v_bitrate.get())
            self.spin_bit.config(state="normal")

        total_mbps = (br * ncam) / 1000
        gb_cam     = (br * 3600 * horas) / (8 * 1024 * 1024)
        total_tb   = (gb_cam * ncam * dias) / 1024
        d1tb       = (1024 / (gb_cam * ncam)) if gb_cam * ncam > 0 else 0

        self.mc_cbt.set(f"{total_mbps:.1f} Mbps", f"{br:.0f} Kbps por câmera", BLUE2)
        self.mc_cpd.set(fmt(gb_cam,"GB"), "por câmera por dia", TEXT1)
        self.mc_cst.set(fmt(total_tb), f"{ncam} câm. × {dias} dias × {horas}h", ACCENT)
        self.mc_cd1.set(f"{d1tb:.1f} dias", "de gravação por 1 TB", GREEN)

        self.lbl_cam_sum.config(
            text=f"▸  {ncam} câmera{'s' if ncam>1 else ''}  ·  {self.v_res.get()}  ·  "
                 f"{self.v_comp.get()}  ·  {fps} fps\n"
                 f"▸  Retenção: {dias} dias × {horas}h/dia  ·  "
                 f"Bitrate estimado: {br:.0f} Kbps/câmera\n"
                 f"▸  Armazenamento total necessário: {fmt(total_tb)}")
        self._update_combined()

    # ── COMBINED PANEL ──────────────────────────────────────────────────────
    def _build_combined_panel(self):
        p = tk.Frame(self.main, bg=BG)
        self._panels["combinado"] = p

        self._section_header(p, "Análise Combinada",
            "Comparação entre o volume disponível no RAID e o necessário pelas câmeras")

        body = tk.Frame(p, bg=BG)
        body.pack(fill="both", expand=True, padx=24, pady=16)

        # top 3 metrics
        top = tk.Frame(body, bg=BG); top.pack(fill="x", pady=(0,16))
        top.columnconfigure(0,weight=1); top.columnconfigure(1,weight=1); top.columnconfigure(2,weight=1)

        self.mc_xraid = MetricCard(top, "Disponível no RAID", "🖴")
        self.mc_xraid.grid(row=0, column=0, sticky="ew", padx=(0,8))
        self.mc_xcam  = MetricCard(top, "Necessário pelas câmeras", "📹")
        self.mc_xcam.grid(row=0, column=1, sticky="ew", padx=(0,8))
        self.mc_xlivr = MetricCard(top, "Saldo / Déficit", "⚖")
        self.mc_xlivr.grid(row=0, column=2, sticky="ew")

        # verdict
        self.verdict_card = Card(body)
        self.verdict_card.pack(fill="x", pady=(0,16))
        vrow = tk.Frame(self.verdict_card, bg=CARD)
        vrow.pack(fill="x", padx=20, pady=16)
        self.lbl_verdict_icon = tk.Label(vrow, text="", font=(FONT,28), bg=CARD)
        self.lbl_verdict_icon.pack(side="left")
        vtxt = tk.Frame(vrow, bg=CARD); vtxt.pack(side="left", padx=12)
        self.lbl_verdict_title = tk.Label(vtxt, text="", font=(FONT,13,"bold"), fg=GREEN, bg=CARD)
        self.lbl_verdict_title.pack(anchor="w")
        self.lbl_verdict_sub = tk.Label(vtxt, text="", font=(FONT,9), fg=TEXT2,
                                        bg=CARD, wraplength=600, justify="left")
        self.lbl_verdict_sub.pack(anchor="w", pady=(4,0))

        # gauge
        gauge_card = Card(body); gauge_card.pack(fill="x", pady=(0,16))
        g_top = tk.Frame(gauge_card, bg=CARD); g_top.pack(fill="x", padx=20, pady=(14,8))
        tk.Label(g_top, text="Utilização do storage RAID", font=(FONT,9,"bold"),
                 fg=TEXT2, bg=CARD).pack(side="left")
        self.lbl_gauge_pct = tk.Label(g_top, text="", font=(FONT,11,"bold"), fg=BLUE2, bg=CARD)
        self.lbl_gauge_pct.pack(side="right")
        self.pbar_combined = ProgressBar(gauge_card)
        self.pbar_combined.pack(fill="x", padx=20, pady=(0,14))

        # breakdown table
        tbl_card = Card(body); tbl_card.pack(fill="x")
        tk.Label(tbl_card, text="Resumo Técnico", font=(FONT,10,"bold"),
                 fg=TEXT1, bg=CARD, padx=20, pady=(14,8)).pack(anchor="w")
        Divider(tbl_card).pack(fill="x")
        self.tbl_frame = tk.Frame(tbl_card, bg=CARD, padx=20, pady=12)
        self.tbl_frame.pack(fill="x")
        self._tbl_rows = []
        for i, (lbl, key) in enumerate([
            ("RAID configurado","raid_type"), ("Volume RAID disponível","raid_util"),
            ("Câmeras","cam_n"), ("Armazenamento necessário","cam_stor"),
            ("Saldo de espaço","saldo"), ("Taxa de utilização","pct"),
        ]):
            row = tk.Frame(self.tbl_frame, bg=CARD if i%2==0 else BG3)
            row.pack(fill="x")
            tk.Label(row, text=lbl, font=(FONT,9), fg=TEXT3,
                     bg=row.cget("bg"), padx=10, pady=6, width=28, anchor="w").pack(side="left")
            val = tk.Label(row, text="—", font=(FONT,9,"bold"), fg=TEXT1,
                           bg=row.cget("bg"), padx=10)
            val.pack(side="right")
            self._tbl_rows.append(val)

    def _update_combined(self):
        try:
            n   = int(self.v_nhd.get())
            tam = float(self.v_thd.get().replace(" TB","").replace(",","."))
        except: return

        raid = self.v_raid.get()
        hs   = self.v_hs.get()
        dr   = max(n-1,1) if hs else n

        if raid in RAID_DATA:
            _, _, min_d, calc = RAID_DATA[raid]
            util_tb = calc(dr,tam) if dr >= min_d else 0
        else: return

        try:
            ncam  = int(self.v_ncam.get())
            res   = RES_MAP.get(self.v_res.get(),2)
            comp  = COMP_MAP.get(self.v_comp.get(),0.5)
            fps   = int(self.v_fps.get().replace(" fps",""))
            dias  = int(self.v_dias.get())
            horas = int(self.v_horas.get())
            auto  = self.v_bitmode.get() == "Automático"
            br    = BR_BASE.get(res,2048)*comp*(fps/15) if auto else float(self.v_bitrate.get())
            cam_tb = (br*3600*horas*ncam*dias)/(8*1024*1024*1024)
        except: return

        livre = util_tb - cam_tb
        pct   = min((cam_tb/util_tb)*100, 100) if util_tb > 0 else 0

        self.mc_xraid.set(fmt(util_tb), "volume RAID disponível", BLUE2)
        self.mc_xcam.set(fmt(cam_tb),   "necessário para câmeras", AMBER)

        if livre >= 0:
            self.mc_xlivr.set(f"+{fmt(livre)}", "espaço livre restante", GREEN)
            self.lbl_verdict_icon.config(text="✅")
            self.lbl_verdict_title.config(
                text=f"Storage suficiente — {fmt(livre)} de margem disponível", fg=GREEN)
            self.lbl_verdict_sub.config(
                text=f"O array RAID fornece {fmt(util_tb)} e as câmeras precisam de {fmt(cam_tb)}. "
                     f"Utilização de {pct:.1f}% do armazenamento disponível.")
        else:
            self.mc_xlivr.set(f"−{fmt(abs(livre))}", "déficit de armazenamento", ACCENT)
            self.lbl_verdict_icon.config(text="⚠️")
            self.lbl_verdict_title.config(
                text=f"Storage insuficiente — déficit de {fmt(abs(livre))}", fg=ACCENT)
            self.lbl_verdict_sub.config(
                text=f"O RAID tem apenas {fmt(util_tb)}, mas as câmeras exigem {fmt(cam_tb)}. "
                     f"Considere adicionar mais HDs, aumentar a capacidade, reduzir câmeras ou o período de retenção.")

        self.pbar_combined.set(pct)
        col = GREEN if pct < 70 else AMBER if pct < 90 else ACCENT
        self.lbl_gauge_pct.config(text=f"{pct:.1f}%", fg=col)

        vals = [raid, fmt(util_tb), f"{ncam} câmeras", fmt(cam_tb),
                f"+{fmt(livre)}" if livre>=0 else f"−{fmt(abs(livre))}",
                f"{pct:.1f}%"]
        cols = [TEXT1,BLUE2,TEXT1,AMBER,
                GREEN if livre>=0 else ACCENT,
                GREEN if pct<70 else AMBER if pct<90 else ACCENT]
        for lbl, v, c in zip(self._tbl_rows, vals, cols):
            lbl.config(text=v, fg=c)

    # ── FOOTER ──────────────────────────────────────────────────────────────
    def _build_footer(self):
        Divider(self).pack(fill="x", side="bottom")
        ft = tk.Frame(self, bg=BG2, height=32)
        ft.pack(fill="x", side="bottom")
        ft.pack_propagate(False)
        tk.Label(ft, text="Intelbras Storage Calculator  ·  Valores estimados para dimensionamento técnico",
                 font=(FONT,8), fg=TEXT3, bg=BG2).pack(side="left", padx=20, pady=8)
        tk.Label(ft, text="© 2025 Intelbras  ·  v2.0",
                 font=(FONT,8), fg=TEXT3, bg=BG2).pack(side="right", padx=20)

if __name__ == "__main__":
    app = App()
    app.mainloop()
