from .PEE import ParEngranesEsfuerzo as PEE
import numpy as np

class ParEngranesResistencia(PEE):
    def __init__(self):
        super().__init__()
        self.K_L_p = None  # factor de vida
        self.K_L_g = None
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
        self.calc_K_L()
        self.calc_C_L()
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
    
    def calc_K_L(self):
        K_L_g = 1.6831*self.ciclos_g**(-0.0323) 
        K_L_p = 1.6831*self.ciclos_p**(-0.0323) 
        if self.K_L_g is None:
            self.K_L_g = K_L_g
        if self.K_L_p is None:
            self.K_L_p = K_L_p
    
    def calc_C_L(self):
        C_L_g = 2.466*self.ciclos_g**(-0.056)
        C_L_p = 2.466*self.ciclos_p**(-0.056)
        if self.C_L_g is None:
            self.C_L_g = C_L_g
        if self.C_L_p is None:
            self.C_L_p = C_L_p


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
    
    def resumen_resistencia(self, dec=2,name=None):
        import os

        if getattr(self, "pinion", None) is None or getattr(self, "engrane", None) is None:
            raise RuntimeError("Faltan engranes: inicializa el par y calcula esfuerzos/resistencia antes de resumir.")

        p, g = self.pinion, self.engrane

        # ---------------- helpers ----------------
        def fmt(x):
            if x is None: 
                return "-"
            try:
                if isinstance(x, int):
                    return f"{x}"
                return f"{float(x):.{dec}f}"
            except Exception:
                return str(x)

        def row(lbl, vp, vg, unit=""):
            unit = f" {unit}" if unit else ""
            return f"{lbl:<28} {fmt(vp):>14} | {fmt(vg):>14}{unit}"

        def get_any(elem, par_attr_name, self_attr_name=None):
            """
            Busca primero en el elemento (piñón/engrane), luego en self.
            Si self_attr_name no se da, usa el mismo nombre.
            """
            self_key = self_attr_name or par_attr_name
            v = getattr(elem, par_attr_name, None)
            if v is None:
                v = getattr(self, self_key, None)
            return v

        # HB (si está en p/g úsala; si no, cae a self.HB_p/HB_g)
        HBp = get_any(p, "HB", "HB_p")
        HBg = get_any(g, "HB", "HB_g")

        # “cumple” helpers
        def ok_tag(v, umbral=1.0):
            if v is None: 
                return "-"
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

        # Parámetros de servicio / globales (en self)
        lines.append("---- Parámetros de servicio ----")
        lines.append(f"{'Temperatura [°C]':<28} {fmt(getattr(self,'temperatura',None)):>14}")
        lines.append(f"{'Confiabilidad R [-]':<28} {fmt(getattr(self,'R',None)):>14}")
        lines.append(f"{'K_T [-]':<28} {fmt(getattr(self,'K_T',None)):>14}")
        lines.append(f"{'K_R [-]':<28} {fmt(getattr(self,'K_R',None)):>14}")
        lines.append(f"{'Caso engrane':<28} {str(getattr(self,'caso_engrane','-')):>14}")
        lines.append(f"{'Rq [µm]':<28} {fmt(getattr(self,'Rq',None)):>14}")
        lines.append("")

        # Cabecera paralelo
        lines.append(f"{'':28} {'PIÑÓN':>14} | {'ENGRANE':>14}")
        lines.append("-"*28 + "-+-" + "-"*31)

        # Coeficientes por elemento (permite que vivan en p/g o en self con sufijo _p/_g)
        lines.append("---- Coeficientes por elemento ----")
        lines.append(row("K_L [-]",   get_any(p, "K_L", "K_L_p"),   get_any(g, "K_L", "K_L_g")))
        lines.append(row("C_L [-]",   get_any(p, "C_L", "C_L_p"),   get_any(g, "C_L", "C_L_g")))
        lines.append(row("C_H [-]",   get_any(p, "C_H", "C_H_p"),   get_any(g, "C_H", "C_H_g")))
        lines.append(row("pSF (flex) [MPa]",  get_any(p, "pSF", "pSF_p"),   get_any(g, "pSF", "pSF_g")))
        lines.append(row("pSFC (cont.) [MPa]",get_any(p, "pSFC","pSFC_p"),  get_any(g, "pSFC","pSFC_g")))
        lines.append(row("HB (dureza) [-]",   HBp,                         HBg))
        lines.append("")

        # Tensiones (si están calculadas en p/g)
        lines.append("---- Tensiones ----")
        lines.append(row("sigma_f [MPa]", getattr(p, "sigma_f", None), getattr(g, "sigma_f", None)))
        lines.append(row("sigma_c [MPa]", getattr(p, "sigma_c", None), getattr(g, "sigma_c", None)))
        lines.append("")

        # Seguridad (si están calculadas en p/g)
        lines.append("---- Seguridad ----")
        lines.append(row("safe_f (perm.) [MPa]", getattr(p, "safe_f", None), getattr(g, "safe_f", None)))
        lines.append(row("safe_c (perm.) [MPa]", getattr(p, "safe_c", None), getattr(g, "safe_c", None)))
        lines.append(row("factor_f [-]", getattr(p, "factor_f", None), getattr(g, "factor_f", None)))
        lines.append(row("factor_c [-]", getattr(p, "factor_c", None), getattr(g, "factor_c", None)))
        lines.append(row("cumple flexión", ok_tag(getattr(p, "factor_f", None)), ok_tag(getattr(g, "factor_f", None))))
        lines.append(row("cumple contacto", ok_tag(getattr(p, "factor_c", None)), ok_tag(getattr(g, "factor_c", None))))
        lines.append("")

        texto = "\n".join(lines)

        # Carpeta/archivo}
        if name is None:
            carpeta = f"conjunto_{self.id}"
        else: 
            carpeta = f"planetario_{self.id}"
        os.makedirs(carpeta, exist_ok=True)
        ruta = os.path.join(carpeta, f"resistencia_{getattr(self,'id','-')}.txt")
        with open(ruta, "w", encoding="utf-8") as f:
            f.write(texto)
        return ruta

    def evaluar_resistencia(self, umbral: float = 1.45):
        """
        Retorna (cumple, data), donde:
        - cumple: True si TODOS los factores de seguridad (flexión y picadura) en piñón y engrane >= umbral.
        - data: {
            "pinion": {
                "flexion":  {"esfuerzo": sigma_f_p, "resistencia": safe_f_p, "factor": factor_f_p},
                "picadura":{"esfuerzo": sigma_c_p, "resistencia": safe_c_p, "factor": factor_c_p}
            },
            "engrane": {
                "flexion":  {"esfuerzo": sigma_f_g, "resistencia": safe_f_g, "factor": factor_f_g},
                "picadura":{"esfuerzo": sigma_c_g, "resistencia": safe_c_g, "factor": factor_c_g}
            }
            }

        Requisitos:
        - self.pinion y self.engrane inicializados.
        - Tensiones y resistencias calculadas previamente en p/g:
            sigma_f, sigma_c, safe_f, safe_c, factor_f, factor_c
        """
        # Verificaciones básicas
        if getattr(self, "pinion", None) is None or getattr(self, "engrane", None) is None:
            raise RuntimeError("Faltan engranes: inicializa el par y calcula esfuerzos/resistencia antes de evaluar.")

        p, g = self.pinion, self.engrane

        # Helper seguro para obtener float o None
        def _f(x):
            try:
                return None if x is None else float(x)
            except Exception:
                return None

        # Extraer valores del piñón
        sigma_f_p = _f(getattr(p, "sigma_f", None))
        sigma_c_p = _f(getattr(p, "sigma_c", None))
        safe_f_p  = _f(getattr(p, "safe_f",  None))
        safe_c_p  = _f(getattr(p, "safe_c",  None))
        fact_f_p  = _f(getattr(p, "factor_f", None))
        fact_c_p  = _f(getattr(p, "factor_c", None))

        # Extraer valores del engrane
        sigma_f_g = _f(getattr(g, "sigma_f", None))
        sigma_c_g = _f(getattr(g, "sigma_c", None))
        safe_f_g  = _f(getattr(g, "safe_f",  None))
        safe_c_g  = _f(getattr(g, "safe_c",  None))
        fact_f_g  = _f(getattr(g, "factor_f", None))
        fact_c_g  = _f(getattr(g, "factor_c", None))

        data = {
            "pinion": {
                "flexion":  {"esfuerzo": sigma_f_p, "resistencia": safe_f_p, "factor": fact_f_p},
                "picadura": {"esfuerzo": sigma_c_p, "resistencia": safe_c_p, "factor": fact_c_p},
            },
            "engrane": {
                "flexion":  {"esfuerzo": sigma_f_g, "resistencia": safe_f_g, "factor": fact_f_g},
                "picadura": {"esfuerzo": sigma_c_g, "resistencia": safe_c_g, "factor": fact_c_g},
            }
        }

        # Regla de decisión: todos los factores definidos y >= umbral
        factores = (fact_f_p, fact_c_p, fact_f_g, fact_c_g)
        cumple = all((f is not None and f >= umbral) for f in factores)

        return cumple, data



    
    

    
    
