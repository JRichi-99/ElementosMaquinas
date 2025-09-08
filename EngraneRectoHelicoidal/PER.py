from PEE import ParEngranesEsfuerzo as PEE
import numpy as np

class ParEngranesResistencia(PEE):
    def __init__(self):
        super().__init__()
        self.K_L = None  # factor de vida
        self.K_T = None  # factor de temperatura
        self.K_R = None  # factor de confiabilidad
        self.C_L = None  # factor de lubricación (contacto)
        self.C_H_p = None   # factor de dureza (contacto)
        self.C_H_g = None
        self.temperatura = None 
        self.R = None
        self.caso_engrane = None
        self.Rq = None 
        self.pSF_g = None
        self.pSF_p = None
        self.pSFC_g = None
        self.pSFC_p = None
        self.HB_p = None
        self.HB_g = None
  
        
    def resistance_params(self, parametros: dict):
        self.K_L_g         = parametros.get("K_L_g")
        self.K_L_p         = parametros.get("K_L_p")
        self.K_T         = parametros.get("K_T")
        self.K_R         = parametros.get("K_R")
        self.C_L_p         = parametros.get("C_L_p")
        self.C_L_g         = parametros.get("C_L_g")
        self.C_H_g       = parametros.get("C_H_g")
        self.C_H_p      = parametros.get("C_H_p")
        self.temperatura = parametros.get("temperatura")
        self.R           = parametros.get("R")
        self.caso_engrane= parametros.get("caso_engrane")
        self.Rq          = parametros.get("Rq")
        self.pSF_g = parametros.get("pSF_g")
        self.pSF_p = parametros.get("pSF_p")
        self.pSFC_g = parametros.get("pSFC_g")
        self.pSFC_p = parametros.get("pSFC_p")

        self.HB_g = parametros.get("HB_g")
        self.HB_p = parametros.get("HB_p")

        

    def calc_resistencia(self, pinion=True,engrane=True):
        self.calc_C_H()
        self.calc_K_T()
        self.calc_K_R()
        if pinion:
            self.pinion.calc_resistance(
                K_L=self.K_L_p,
                K_T=self.K_T,
                K_R=self.K_R,
                C_L=self.C_L_p,
                C_H=self.C_H_p,
                pSF = self.pSF_p,
                pSFC = self.pSFC_p
            )
        if engrane:
            self.engrane.calc_resistance(
                K_L=self.K_L_g,
                K_T=self.K_T,
                K_R=self.K_R,
                C_L=self.C_L_g,
                C_H=self.C_H_g,
                pSF = self.pSF_g,
                pSFC = self.pSFC_g
            )
    
    def calc_C_H(self):
        if self.C_H_p is not None: 
            print("Se selecciono valor de C_H_p", self.C_H_p)
        else: 
            self.C_H_p = 1
        if self.C_H_g is not None:
            print("Se selecciono valor de C_H_g: ", self.C_H_g)
            return
        hb_p = self.HB_p
        hb_g = self.HB_g
        hb_r = hb_p/hb_g
        if hb_r <= 1.2:
            A = 0
        elif hb_r <=1.7:
            A = 8.98e-3*hb_r-8.29e-3
        else:
            A = 6.98e-3
        B = 0.75e-3*np.exp(-0.0112*self.Rq)
        if self.caso_engrane == 'masa':
            self.C_H_g = 1+A*(self.m_g-1)
        elif self.caso_engrane == 'superficie':
            self.C_H_g = 1+B*(450-hb_g)
        else:
            raise ValueError("Error caso engrane para  C_H")

    def calc_K_T(self):
        if self.K_T is not None:
            print("Se selecciono valor de K_T", self.K_T)
            return
        if self.temperatura < 110:
            self.K_T = 1
        else:
            self.K_T=(220+self.temperatura)/330

    def calc_K_R(self):
        if self.K_R is not None:
            print("Se selecciono K_R: ", self.K_R)
            return
        if self.R <= 0.99 and self.R >= 0.9:
            self.K_R = 0.7-0.15*np.log10(1-self.R)
        elif self.R <= 0.9999:
            self.K_R = 0.5-0.25*np.log10(1-self.R)
        else:
            raise ValueError("R fuera de rango")
    
    def resumen_resistencia(self, dec=2, escribir=True):
        import os
        if getattr(self, "pinion", None) is None or getattr(self, "engrane", None) is None:
            raise RuntimeError("Faltan engranes: inicializa el par y calcula esfuerzos/resistencia antes de resumir.")

        p, g = self.pinion, self.engrane

        # ---------------- helpers ----------------
        def fmt(x):
            if x is None: return "-"
            try:
                if isinstance(x, int): return f"{x}"
                return f"{float(x):.{dec}f}"
            except Exception:
                return str(x)

        def row(lbl, vp, vg, unit=""):
            unit = f" {unit}" if unit else ""
            return f"{lbl:<24} {fmt(vp):>14} | {fmt(vg):>14}{unit}"

        # HB (tomar del engrane si existe, si no del par)
        HBp = getattr(p, "HB", None) if getattr(p, "HB", None) is not None else getattr(self, "HB_p", None)
        HBg = getattr(g, "HB", None) if getattr(g, "HB", None) is not None else getattr(self, "HB_g", None)

        # “cumple” helpers
        def ok_tag(v, umbral=1.0):
            if v is None: return "-"
            try:
                return "OK" if float(v) >= umbral else "NO"
            except Exception:
                return "-"

        # ---------------- armado ----------------
        lines = []
        lines.append(f"================= RESUMEN DE RESISTENCIA (ID {getattr(self,'id','-')}) =================")
        lines.append(f"Tipo: {getattr(self,'clase','-')} | Acople: {getattr(self,'acople','-')}")
        lines.append(f"Np={fmt(getattr(p,'N',None))} | Ng={fmt(getattr(g,'N',None))} | m_g=Ng/Np={fmt(getattr(self,'m_g', None))}")
        lines.append("")

        # Parámetros de servicio / globales
        lines.append("---- Parámetros de servicio ----")
        lines.append(f"{'Temperatura [°C]':<24} {fmt(getattr(self,'temperatura',None)):>14}")
        lines.append(f"{'Confiabilidad R [-]':<24} {fmt(getattr(self,'R',None)):>14}")
        lines.append(f"{'K_T [-]':<24} {fmt(getattr(self,'K_T',None)):>14}")
        lines.append(f"{'K_R [-]':<24} {fmt(getattr(self,'K_R',None)):>14}")
        lines.append(f"{'Caso engrane':<24} {str(getattr(self,'caso_engrane','-')):>14}")
        lines.append(f"{'Rq [µm]':<24} {fmt(getattr(self,'Rq',None)):>14}")
        lines.append("")

        # Cabecera paralelo
        lines.append(f"{'':24} {'PIÑÓN':>14} | {'ENGRANE':>14}")
        lines.append("-"*24 + "-+-" + "-"*31)

        # Coeficientes por elemento
        lines.append("---- Coeficientes por elemento ----")
        lines.append(row("K_L [-]", getattr(self, "K_L_p", None), getattr(self, "K_L_g", None)))
        lines.append(row("C_L [-]", getattr(self, "C_L_p", None), getattr(self, "C_L_g", None)))
        lines.append(row("C_H [-]", getattr(self, "C_H_p", None), getattr(self, "C_H_g", None)))
        lines.append(row("pSF (flex) [MPa]", getattr(self, "pSF_p", None), getattr(self, "pSF_g", None), ""))
        lines.append(row("pSFC (cont.) [MPa]", getattr(self, "pSFC_p", None), getattr(self, "pSFC_g", None), ""))
        lines.append(row("HB (dureza) [-]", HBp, HBg))
        lines.append("")

        # Tensiones
        lines.append("---- Tensiones ----")
        lines.append(row("sigma_f [MPa]", getattr(p, "sigma_f", None), getattr(g, "sigma_f", None)))
        lines.append(row("sigma_c [MPa]", getattr(p, "sigma_c", None), getattr(g, "sigma_c", None)))
        lines.append("")

        # Seguridad
        lines.append("---- Seguridad ----")
        lines.append(row("safe_f (perm.) [MPa]", getattr(p, "safe_f", None), getattr(g, "safe_f", None)))
        lines.append(row("safe_c (perm.) [MPa]", getattr(p, "safe_c", None), getattr(g, "safe_c", None)))
        lines.append(row("factor_f [-]", getattr(p, "factor_f", None), getattr(g, "factor_f", None)))
        lines.append(row("factor_c [-]", getattr(p, "factor_c", None), getattr(g, "factor_c", None)))
        lines.append(row("cumple flexión", ok_tag(getattr(p, "factor_f", None)), ok_tag(getattr(g, "factor_f", None))))
        lines.append(row("cumple contacto", ok_tag(getattr(p, "factor_c", None)), ok_tag(getattr(g, "factor_c", None))))
        lines.append("")

        texto = "\n".join(lines)

        if not escribir:
            return texto

        carpeta = f"conjunto_{self.id}"
        os.makedirs(carpeta, exist_ok=True)
        ruta = os.path.join(carpeta, f"resistencia_{self.id}.txt")
        with open(ruta, "w", encoding="utf-8") as f:
            f.write(texto)
        return ruta



    
    

    
    
