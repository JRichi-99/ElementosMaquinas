import numpy as np
from .PET import ParEngranesTransmision 

class ParEngranesEsfuerzo(ParEngranesTransmision):
    def __init__(self):
        super().__init__()

        # Índice de geometría de contacto (AGMA)
        self.I = None

        # Factores/coeficientes (inicializados)
        self.K_A = None   # factor de aplicación
        self.K_M = None   # distribución de carga
        self.K_S = None   # tamaño
        self.K_B = None   # borde
        self.K_I = None   # carga interna
        self.K_V = None   # dinámico

        self.J_pin = None 
        self.J_eng = None 
        self.Jp_pin= None 
        self.Jmod_pin= None 
        self.Jp_eng= None 
        self.Jmod_eng= None 

        self.K_I_pin= None
        self.K_I_eng = None

        self.F   = None   # ancho de cara a usar en esfuerzo (mm)
        self.C_p = None   # coeficiente elástico [√MPa]
        self.C_F = None   # factor superficial
        self.Q_v = None   # Calidad


    def calc_esfuerzos(self, pinion=True, engrane=True):
        self.calc_J()
        self.calc_I()
        self.calc_k_v()
        if pinion:
            self.pinion.calc_tensions(
            K_A=self.K_A, K_M=self.K_M, K_S=self.K_S, K_B=self.K_B, K_I=self.K_I_pin, K_V=self.K_V,
            J=self.J_pin, F=self.F, C_p=self.C_p, C_F=self.C_F, I=self.I)
        if engrane:
            self.engrane.calc_tensions(
            K_A=self.K_A, K_M=self.K_M, K_S=self.K_S, K_B=self.K_B, K_I=self.K_I_eng, K_V=self.K_V,
            J=self.J_eng, F=self.F, C_p=self.C_p, C_F=self.C_F, I=self.I)


    def tension_params(self, parametros):
        # Factores AGMA
        self.K_A     = parametros.get("K_A",     self.K_A)
        self.K_M     = parametros.get("K_M",     self.K_M)
        self.K_S     = parametros.get("K_S",     self.K_S)
        self.K_B     = parametros.get("K_B",     self.K_B)
        self.K_V     = parametros.get("K_V",     self.K_V)

        self.K_I_pin = parametros.get("K_I_pin")
        self.K_I_eng = parametros.get("K_I_eng")

        # J parciales / modificadores
        self.Jp_pin  = parametros.get("Jp_pin",  self.Jp_pin)
        self.Jmod_pin= parametros.get("Jmod_pin",self.Jmod_pin)
        self.Jp_eng  = parametros.get("Jp_eng",  self.Jp_eng)
        self.Jmod_eng= parametros.get("Jmod_eng",self.Jmod_eng)
        self.J_pin   = parametros.get("Jp",      self.J_pin)
        self.J_eng   = parametros.get("Jg",      self.J_eng)

        # Coeficientes de contacto / calidad
        self.C_p     = parametros.get("C_p",     self.C_p)
        self.C_F     = parametros.get("C_F",     self.C_F)
        self.Q_v     = parametros.get("Q_v",     self.Q_v)

        self.I       = parametros.get("I",       self.I)

    def calc_k_v(self):
        if self.K_V is not None:
            print("Se introdujo K_V: ",self.K_V)
            return
        Qv = float(self.Q_v)
        Vt = float(self.pinion.Vt)

        # --- B ---
        if Qv >= 6 and Qv <= 12:
            B = (((12.0 - Qv)) ** (2.0 / 3.0))/ 4.0
        elif Qv < 6:
            B = 1.0
        else:  # Qv > 12
            B = 0.0

        # --- A ---
        A = 50.0 + 56.0 * (1.0 - B)

        # --- Kv ---
        denom = A + (200.0 * Vt) ** 0.5
        K_v = (A / denom) ** B

        self.K_V = K_v

    def calc_J(self):
        if self.J_eng is None:
            #print("Entro J_eng: ", self.J_eng)
            self.J_eng = self.Jp_eng*self.Jmod_eng
        if self.J_pin is None:
            #print("Entro J_pin: ", self.J_pin)
            self.J_pin = self.Jp_pin*self.Jmod_pin


    def calc_I(self):
        if self.I is not None:
            print("Se introdujo I: ",self.I)
            return
        """
        Calcula el índice de geometría de contacto I.
        Requiere: phi_n, m_n, pinion/engrane con r_curvatura y d_p,
        y 'acople' ('externos'|'internos').
        """
        # Validaciones
        if self.phi_n is None or self.m_n is None:
            raise RuntimeError("Faltan ángulos/razón de contacto (phi_n, m_n).")
        if self.pinion is None or self.engrane is None:
            raise RuntimeError("Piñón/Engrane no inicializados (llama set_par antes).")
        if self.pinion.r_curvatura is None or self.engrane.r_curvatura is None:
            raise RuntimeError("Radios de curvatura no calculados (llama r_curvatura() antes).")
        if self.pinion.d_p is None or self.engrane.d_p is None:
            raise RuntimeError("Diámetros de paso no definidos.")

        num = np.cos(float(self.phi_n))
        denom_1 = float(self.pinion.d_p) * float(self.m_n)

        inv_p = 1.0 / float(self.pinion.r_curvatura)
        inv_g = 1.0 / float(self.engrane.r_curvatura)

        if self.acople == "externos":
            denom_2 = inv_p + inv_g
        elif self.acople == "internos":
            denom_2 = inv_p - inv_g
        else:
            raise ValueError(f"Acople inválido: {self.acople}")

        self.I = num / (denom_1 * denom_2)
    
    def resumen_esfuerzos(self, dec=2, name=None):
        import os
        import numpy as np  # usado en conversión a rpm

        if getattr(self, "pinion", None) is None or getattr(self, "engrane", None) is None:
            raise RuntimeError("Faltan engranes: inicializa el par (set_par) y calcula esfuerzos antes de resumir.")

        p = self.pinion
        g = self.engrane

        def fmt(x):
            if x is None: return "-"
            try:
                if isinstance(x, int): return f"{x}"
                return f"{float(x):.{dec}f}"
            except Exception:
                return str(x)

        def deg(x):
            return "-" if x is None else f"{np.degrees(float(x)):.{dec}f}"

        def row(etq, vp, vg, unit=""):
            unit = f" {unit}" if unit else ""
            return f"{etq:<18} {fmt(vp):>14} | {fmt(vg):>14}{unit}"

        # Encabezado
        lines = []
        lines.append(f"== RESUMEN DE ESFUERZOS (ID {getattr(self,'id','-')}) ==")
        lines.append(f"Tipo: {getattr(self,'clase','-')} | Acople: {getattr(self,'acople','-')}")
        lines.append(f"Relación mg=Ng/Np: {fmt(getattr(self,'m_g', getattr(self,'i', None)))}")
        lines.append("")

        # ------------------- PARÁMETROS / CONSTANTES USADOS -------------------
        lines.append("--- Parámetros usados ---")
        # Factores globales AGMA
        lines.append(f"{'K_A':<6}: {fmt(getattr(self,'K_A',None))}    "
                    f"{'K_M':<6}: {fmt(getattr(self,'K_M',None))}    "
                    f"{'K_S':<6}: {fmt(getattr(self,'K_S',None))}")
        lines.append(f"{'K_B':<6}: {fmt(getattr(self,'K_B',None))}    "
                    f"{'K_V':<6}: {fmt(getattr(self,'K_V',None))}")
        # Coeficiente de impacto/ distribución por elemento (si lo usas como K_I separado por piñón/engrane)
        lines.append(f"{'':18} {'PIÑÓN':>14} | {'ENGRANE':>14}")
        lines.append("-"*18 + "-+-" + "-"*31)
        lines.append(row("K_I [-]", getattr(self,'K_I_pin',None), getattr(self,'K_I_eng',None)))

        # Calidad / contacto global
        lines.append("")
        lines.append(f"{'C_p':<6}: {fmt(getattr(self,'C_p',None))} [√MPa]    "
                    f"{'C_F':<6}: {fmt(getattr(self,'C_F',None))}    "
                    f"{'Q_v':<6}: {fmt(getattr(self,'Q_v',None))}")
        lines.append(f"{'I (AGMA)':<10}: {fmt(getattr(self,'I',None))}    "
                    f"{'F (mm)':<10}: {fmt(getattr(self,'F',None))}")
        # J desglosados
        lines.append(f"{'Jp_pin':<10}: {fmt(getattr(self,'Jp_pin', None))}    "
                    f"{'Jmod_pin':<10}: {fmt(getattr(self,'Jmod_pin', None))}    "
                    f"{'J_pin (ef)':<12}: {fmt(getattr(self,'J_pin', None))}")
        lines.append(f"{'Jp_eng':<10}: {fmt(getattr(self,'Jp_eng', None))}    "
                    f"{'Jmod_eng':<10}: {fmt(getattr(self,'Jmod_eng', None))}    "
                    f"{'J_eng (ef)':<12}: {fmt(getattr(self,'J_eng', None))}")
        lines.append("")

        # ------------------- TABLA EN PARALELO -------------------
        lines.append(f"{'':18} {'PIÑÓN':>14} | {'ENGRANE':>14}")
        lines.append("-"*18 + "-+-" + "-"*31)

        # CARGA
        lines.append("--- Carga ---")
        lines.append(row("T", getattr(p, "T", None), getattr(g, "T", None), "[N·m]"))
        lines.append(row("Omega", getattr(p, "Omega", None), getattr(g, "Omega", None), "[rad/s]"))
        # Conversión a rpm (si Omega es None se rompería; asumimos que existe como en tu versión original)
        lines.append(row("Omega", getattr(p, "Omega", None)*30/np.pi, getattr(g, "Omega", None)*30/np.pi, "[rpm]"))
        lines.append(row("H", getattr(p, "H", None), getattr(g, "H", None), "[W]"))
        lines.append("")

        # FUERZAS
        lines.append("--- Fuerzas ---")
        lines.append(row("Wt", getattr(p, "Wt", None), getattr(g, "Wt", None), "[N]"))
        lines.append(row("Wr", getattr(p, "Wr", None), getattr(g, "Wr", None), "[N]"))
        lines.append(row("Wa", getattr(p, "Wa", None), getattr(g, "Wa", None), "[N]"))
        lines.append(row("Wn", getattr(p, "Wn", None), getattr(g, "Wn", None), "[N]"))
        lines.append("")

        # CINEMÁTICA
        lines.append("--- Cinemática ---")
        lines.append(row("Vt", getattr(p, "Vt", None), getattr(g, "Vt", None), "[m/s]"))
        lines.append("")

        # TENSIONES
        lines.append("--- Tensiones ---")
        lines.append(row("sigma_f", getattr(p, "sigma_f", None), getattr(g, "sigma_f", None), "[MPa]"))
        lines.append(row("sigma_c", getattr(p, "sigma_c", None), getattr(g, "sigma_c", None), "[MPa]"))
        lines.append("")

        texto = "\n".join(lines)

        # ------------------- ESCRITURA -------------------
        if name is None:
            carpeta = f"conjunto_{self.id}"
        else: 
            carpeta = f"planetario_{self.id}"

        filename = f"esfuerzos_{self.id}.txt"
        os.makedirs(carpeta, exist_ok=True)
        ruta = os.path.join(carpeta, filename)
        with open(ruta, "w", encoding="utf-8") as f:
            f.write(texto)



    
    









