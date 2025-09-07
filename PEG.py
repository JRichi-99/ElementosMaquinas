import numpy as np
from ER import EngranajeResistencia as ER

class ParEngranesGeometria:
    id = 0
    def __init__(self):
        import os
        os.makedirs(f"conjunto_{ParEngranesGeometria.id}", exist_ok=True)
        # ID incremental
        self.id = ParEngranesGeometria.id
        ParEngranesGeometria.id += 1

        # Parámetros del par
        self.C = None      # distancia entre centros
        self.Z = None      # longitud de línea de acción
        self.F = None      # ancho de cara

        # Contacto
        self.m_p = None    # razón de contacto tangencial
        self.m_f = None    # razón de contacto axial 
        self.m_n = None    # razón de contacto total

        # Relaciones
        self.m_g = None    # N_engrane / N_pinion
        self.m_v = None    # N_pinion / N_engrane

        # Módulos / pasos 
        self.m = None                    # módulo normal
        self.p_n = None; self.pi_n = None
        self.m_t = None; self.p_t = None; self.pi_t = None
        self.m_x = None; self.p_x = None; self.pi_x = None
        self.p_b = None                  # paso base (transversal)

        # Ángulos
        self.phi_n = None               # presión normal (rad)
        self.phi_t = None               # presión transversal (rad)
        self.psi = None                 # hélice (rad)
        self.psi_b = None               # hélice en base (rad)

        # Datos auxiliares
        self.pinion = None              # objeto piñón
        self.engrane = None             # objeto engrane
        self.clase = None               # 'recto' | 'heli'
        self.acople = 'externos'        # 'externos' | 'internos'
        self.sistema_dientes = None  # 'total' | 'parcial'

        # Desplazamientos de perfil
        self.xp = 0.0            # desplazamiento piñón

    # ----------------- Setup -----------------
    def set_par(self, phi_n, psi, N_pinion, N_engrane, F_pinion, F_engrane, sistema_dientes='total',acople='externos', m=None, pi_n=None, xp=0.0):
        self.sistema_dientes = sistema_dientes
        self.xp = xp
        # Guardar tipo y acople con validación
        self.clase = 'heli' if abs(psi) > 0.0 else 'recto'
        if acople not in ('externos', 'internos'):
            raise ValueError("acople debe ser 'externos' o 'internos'")
        self.acople = acople

        # Módulo y ángulos
        self.m = self.extract_m(m, pi_n)
        if self.m is None:
            raise ValueError("Se requiere 'm' o 'pi_n' para definir el módulo")
        self.F = min(F_pinion, F_engrane)  # ancho de cara común
        self.phi_n = np.deg2rad(float(phi_n))
        self.psi = np.deg2rad(float(psi))

        # Ángulos derivados
        self.phi_t, self.psi_b = self.angulos(self.phi_n, self.psi)

        # Módulos/pasos/pitch derivados
        self.modulo_paso_pitch(self.m, self.psi, self.phi_t)

        self.crear_instancias(
            N_pinion=N_pinion,
            N_engrane=N_engrane,
            F_pinion=F_pinion,
            F_engrane=F_engrane
        )

        # Calcular distancia entre centros y longitud de acción
        self.compute_couple()

        self.r_curvatura()

    def modulo_paso_pitch(self, m, psi, phi_t):
        # módulos (normal → transversal/axial)
        m_t = m / np.cos(psi)
        if self.clase == 'heli' and np.abs(np.sin(psi)) > 0:
            m_x = m / np.sin(psi)
        else:
            m_x = None

        # pasos
        p_n = np.pi * m
        p_t = np.pi * m_t
        p_x = np.pi * m_x if m_x is not None else None

        # paso base (transversal)
        p_b = p_t * np.cos(phi_t)

        # pitch (inverso del módulo)
        pi_n = 1.0 / m
        pi_t = 1.0 / m_t
        pi_x = (1.0 / m_x) if m_x is not None else None

        # guardar
        self.m_t, self.m_x = m_t, m_x
        self.p_n, self.p_t, self.p_x, self.p_b = p_n, p_t, p_x, p_b
        self.pi_n, self.pi_t, self.pi_x = pi_n, pi_t, pi_x

    def extract_m(self, m, pi_n):
        if m is not None:
            return float(m)
        if pi_n is not None:
            return 1/float(pi_n) *25.4
        return None

    # ----------------- Geometría derivada -----------------
    def angulos(self, phi_n, psi):
        """
        φ_t = atan( tan φ_n / cos ψ )
        ψ_b = arccos( cos ψ * cos φ_n / cos φ_t )
        """
        phi_t = np.arctan(np.tan(phi_n) / np.cos(psi))
        psi_b = np.arccos(np.cos(psi) * np.cos(phi_n) / np.cos(phi_t))
        return phi_t, psi_b
    
    def compute_couple(self):
        self.C = self.engrane.r_p+self.pinion.r_p if self.acople == 'externos' else abs(self.engrane.r_p - self.pinion.r_p)
        self.Z = (np.sqrt((self.pinion.d_p/2 + self.m)**2 - ((self.pinion.d_p/2) * np.cos(self.phi_t))**2)
                + np.sqrt((self.engrane.d_p/2 + self.m)**2 - ((self.engrane.d_p/2) * np.cos(self.phi_t))**2)
                - self.C * np.sin(self.phi_t))
        self.razones()
    
    def razones(self):
        m_g = self.engrane.N/self.pinion.N
        m_v = self.pinion.N/self.engrane.N
        m_p = self.Z/self.p_b
        m_f = self.F/self.p_x if self.p_x else None
        self.m_g = m_g
        self.m_v = m_v
        self.m_p = m_p
        self.m_f = m_f
        self.m_n = self.calc_m_n()
    
    def calc_m_n(self):
        if self.clase == 'recto':
            return 1
        elif self.clase == 'heli':
            na = self.m_p-int(self.m_p)
            nr = self.m_f-int(self.m_f)
            if na <= 1-nr:
                return self.F/((self.m_p*self.F-na*nr*self.p_x)/np.cos(self.psi_b))
            return self.F/((self.m_p*self.F-(1-na)*(1-nr)*self.p_x)/np.cos(self.psi_b))
    
    def r_curvatura(self):
        if self.clase == 'heli':
            self.calc_rho_heli()
        elif self.clase == 'recto':
            self.calc_rho_recto()
    
    def crear_instancias(self, N_pinion, N_engrane, F_pinion, F_engrane):
        # Crear instancias de piñón y engrane
        self.pinion = ER()
        self.pinion.calc_geometric(m=self.m,
            m_t=self.m_t,
            phi_n=self.phi_n,
            phi_t=self.phi_t,
            psi=self.psi,
            psi_b=self.psi_b,
            N=N_pinion,
            F=F_engrane,
            rol='pinion',
            sistema_dientes='total',
            acople=self.acople,
            xp=self.xp
        )
            
        self.engrane = ER()
        self.engrane.calc_geometric(
            m=self.m,
            m_t=self.m_t,
            phi_n=self.phi_n,
            phi_t=self.phi_t,
            psi=self.psi,
            psi_b=self.psi_b,
            N=N_engrane,
            F=F_pinion,
            rol='engrane',
            sistema_dientes='total',
            acople=self.acople,
            xp=self.xp  # desplazamiento opuesto para el engrane
        )

    def calc_rho_heli(self):
        dp   = float(self.pinion.d_p)
        dg   = float(self.engrane.d_p)
        m    = float(self.m)
        C    = float(self.C)
        phi_t  = float(self.phi_t)

        if self.acople == "externos":
            term = (dp/2.0 + m) + C - (dg/2.0 + m)
        elif self.acople == "internos":
            term = (dp/2.0 + m) - C + (dg/2.0 + m)
        else:
            raise ValueError("Acople debe ser 'externos' o 'internos'.")

        rho_p = (0.25 * term**2 - ((dp/2.0) * np.cos(phi_t))**2) ** 0.5
        self.pinion.r_curvatura = rho_p
        self.engrane.r_curvatura = self.C*np.sin(phi_t)-rho_p

    def calc_rho_recto(self):
        dp   = float(self.pinion.d_p)
        dbp  = float(self.pinion.d_b)
        mt   = float(self.m_t)
        xp   = float(getattr(self.pinion, "xp", 0.0))
        phi_n  = float(self.phi_n)
        phi_t = float(self.phi_t)

        rho_p = np.sqrt((dp/2.0 + mt * (1.0 + xp))**2 - (dbp/2.0)**2) - mt*np.cos(phi_n)

        self.pinion.r_curvatura = rho_p
        self.engrane.r_curvatura = self.C*np.sin(phi_t)-rho_p

    def resumen_geometria(self):
        import os

        def fmt(x, nd=2):
            if x is None:
                return "-"
            try:
                # enteros sin decimales, floats con redondeo
                if isinstance(x, (int,)):
                    return f"{x}"
                if isinstance(x, (float,)):
                    return f"{x:.{nd}f}"
                return str(x)
            except Exception:
                return str(x)

        def deg(x):
            import numpy as np
            return None if x is None else np.degrees(x)

        # ---- Preparar nombre de archivo
        filename = os.path.join(f"conjunto_{self.id}", f"geometria_{self.id}.txt")

        # ---- Sistema (par)
        sistema_lines = []
        sistema_lines.append(f"Par de engranajes ID: {self.id}")
        sistema_lines.append(f"Tipo: {self.clase or '-'} | Acople: {self.acople or '-'} | Sistema dientes: {self.sistema_dientes or '-'}")
        # Dientes
        try:
            Np = getattr(self.pinion, "N", None)
            Ng = getattr(self.engrane, "N", None)
        except Exception:
            Np, Ng = None, None
        sistema_lines.append(f"Dientes: Np={fmt(Np,0)} | Ng={fmt(Ng,0)} | m_g={fmt(self.m_g)} | m_v={fmt(self.m_v)}")

        # Geometría global
        sistema_lines.append(f"C (distancia centros): {fmt(self.C)} mm")
        sistema_lines.append(f"Z (long. línea de acción): {fmt(self.Z)} mm")
        sistema_lines.append(f"F (ancho de cara común): {fmt(self.F)} mm")

        # Módulos / pasos
        sistema_lines.append(
            "Módulos: "
            f"m={fmt(self.m)} mm | m_t={fmt(self.m_t)} mm | m_x={fmt(self.m_x)} mm | "
        )

        sistema_lines.append(
            "Pasos: "
            f"p_n={fmt(self.p_n)} mm | p_t={fmt(self.p_t)} mm | p_x={fmt(self.p_x)} mm | p_b={fmt(self.p_b)} mm | "
        )

        sistema_lines.append(
            "Pitch: "
            f"pi_n={fmt(self.pi_n)} 1/mm {fmt(self.pi_n*25.4)} in^-1 | pi_t={fmt(self.pi_t)} 1/mm | pi_x={fmt(self.pi_x)} 1/mm"
        )

        # Ángulos (en grados para lectura humana)
        sistema_lines.append(
            "Ángulos [°]: "
            f"phi_n={fmt(deg(self.phi_n))} | phi_t={fmt(deg(self.phi_t))} | psi={fmt(deg(self.psi))} | psi_b={fmt(deg(self.psi_b))}"
        )

        # Contacto
        sistema_lines.append(
            f"Razones de contacto: m_p={fmt(self.m_p)} | m_f={fmt(self.m_f)} | m_n={fmt(self.m_n)}"
        )

        # Desplazamiento
        sistema_lines.append(f"Desplazamiento de perfil xp: {fmt(self.xp)}")

        # ---- Columnas: piñón y engrane
        pinion_lines = []
        engrane_lines = []

        if self.pinion is not None and hasattr(self.pinion, "resume_geometric"):
            try:
                pinion_lines = self.pinion.resume_geometric()
            except Exception:
                pinion_lines = ["(No se pudo generar el resumen del piñón)"]
        else:
            pinion_lines = ["(Piñón no inicializado)"]

        if self.engrane is not None and hasattr(self.engrane, "resume_geometric"):
            try:
                engrane_lines = self.engrane.resume_geometric()
            except Exception:
                engrane_lines = ["(No se pudo generar el resumen del engrane)"]
        else:
            engrane_lines = ["(Engrane no inicializado)"]

        # Alinear columnas
        max_len = max(len(pinion_lines), len(engrane_lines))
        while len(pinion_lines) < max_len:
            pinion_lines.append("")
        while len(engrane_lines) < max_len:
            engrane_lines.append("")

        col_width = max(len(line) for line in pinion_lines) + 4  # separación

        # ---- Escribir archivo
        with open(filename, "w", encoding="utf-8") as f:
            # Bloque sistema
            f.write("== PARÁMETROS DEL SISTEMA ==\n")
            for ln in sistema_lines:
                f.write(ln + "\n")
            f.write("\n")

            # Bloque columnas
            header = f"{'Piñón'.ljust(col_width)}Engrane\n"
            f.write(header)
            f.write("-" * len(header) + "\n")
            for pl, el in zip(pinion_lines, engrane_lines):
                f.write(f"{pl.ljust(col_width)}{el}\n")

        return filename


