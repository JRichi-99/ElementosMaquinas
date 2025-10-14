import numpy as np

class EngranajeGeometria:
    id = 0
    def __init__(self):
        self.id = EngranajeGeometria.id
        EngranajeGeometria.id +=1
        # Info general
        self.rol = None                 # 'pinion' o 'engrane'
        self.sist_dientes = None        # 'total' o 'parcial'
        self.acople = None              # 'externos' o 'internos'
        self.clase = None               # 'recto' o 'heli'
        self.F = None                   # ancho de cara

        # Dientes
        self.N = None

        # Ángulos (rad) — todos vienen dados
        self.phi_n = None               # presión normal
        self.phi_t = None               # presión transversal
        self.psi = None                 # hélice
        self.psi_b = None               # hélice en base

        # Módulos (mm) — todos vienen dados
        self.m = None                   # módulo normal
        self.m_t = None                 # módulo transversal

        # Ajuste de perfil
        self.xp = None                  # desplazamiento de perfil

        # Diámetros y radios
        self.d_p = None; self.r_p = None
        self.d_b = None; self.r_b = None
        self.d_r = None; self.r_r = None
        self.d_a = None; self.r_a = None

        # Geometría del diente
        self.a = None                   # addendum
        self.b = None                   # dedendum
        self.e = None                   # espesor circular en paso (transversal)
        self.ht = None                  # a + b
        self.tolerancia = None          # b - a

        # Resistencia (se calcula en otra etapa)
        self.r_curvatura = None
        self.Ne = None

    # ============ API: recibe todo derivado y calcula diente/diámetros ============
    def calc_geometric(
        self,
        m,              # módulo normal [mm]
        m_t,            # módulo transversal [mm]
        phi_n,          # ángulo de presión normal [rad]
        phi_t,          # ángulo de presión transversal [rad]
        F,              # ancho de cara [mm]
        N,              # número de dientes
        rol,            # 'pinion' | 'engrane'
        psi=0.0,        # ángulo de hélice [rad] (ya viene dado, no se deriva nada)
        psi_b=0.0,      # ángulo de hélice en base [rad] (ya viene dado)
        sistema_dientes='total',
        acople='externos',
        xp=0.0
    ):
        # ---- Asignación directa (sin derivaciones)
        self.m = float(m)
        self.m_t = float(m_t)
        self.phi_n = float(phi_n)
        self.phi_t = float(phi_t)
        self.psi = float(psi)
        self.psi_b = float(psi_b)

        self.N = int(N)
        self.F = float(F)
        self.rol = str(rol)
        self.sist_dientes = str(sistema_dientes)
        self.acople = str(acople)
        self.xp = float(xp)

        # Clase solo por claridad (no deriva nada)
        self.clase = 'heli' if abs(self.psi) > 0.0 else 'recto'

        # ---- Geometría del diente y diámetros
        self._diametros_radio_diente(
            m=self.m,
            m_t=self.m_t,
            N=self.N,
            phi_t=self.phi_t,
            sistema_dientes=self.sist_dientes,
            xp=self.xp,
            rol=self.rol
        )

    def _diametros_radio_diente(self, m, m_t, N, phi_t, sistema_dientes, xp, rol):
        # Diámetro y radio de paso (transversal)
        d_p = N * m_t
        r_p = 0.5 * d_p

        # Base (transversal)
        d_b = d_p * np.cos(phi_t)
        r_b = 0.5 * d_b

        # Signo típico para desplazamiento de perfil
        signo = 1.0 if rol == 'pinion' else -1.0

        # Alturas radiales usando módulo normal (estándar)
        if sistema_dientes == 'total':
            a = m * (1.0 + signo * float(xp))    # addendum con corrección
            b = 1.25 * m                         # dedendum estándar
        else:
            a = 0.8 * m
            b = 1.0 * m

        ht = a + b
        self.Ne = N*np.sqrt((1+np.cos(self.psi)**2)/2)/(np.cos(self.psi)**2)

        # Espesor circular en el paso (transversal)
        e = 0.5 * np.pi * m_t

        # Diámetros de cabeza y raíz
        d_a = d_p + 2.0 * a
        r_a = 0.5 * d_a
        d_r = d_p - 2.0 * b
        r_r = 0.5 * d_r

        # Tolerancia simple
        tolerancia = b - a

        # Guardar
        self.d_p, self.r_p = d_p, r_p
        self.d_b, self.r_b = d_b, r_b
        self.d_r, self.r_r = d_r, r_r
        self.d_a, self.r_a = d_a, r_a
        self.a, self.b, self.ht = a, b, ht
        self.e = e
        self.tolerancia = tolerancia

    def resume_geometric(self):
        lines = []

        # helper: redondear
        def fmt(x, nd=2):
            if x is None:
                return "-"
            try:
                if isinstance(x, int):
                    return f"{x}"
                if isinstance(x, float):
                    return f"{x:.{nd}f}"
                return str(x)
            except Exception:
                return str(x)

        # helper: convertir radianes a grados con redondeo
        def rad2deg(val, nd=2):
            import numpy as np
            return "-" if val is None else f"{np.degrees(val):.{nd}f}"

        # Información general
        lines.append(f"ID: {self.id}")
        lines.append(f"Rol: {self.rol}")
        lines.append(f"Clase: {self.clase}")
        lines.append(f"Acople: {self.acople}")
        lines.append(f"Sistema de dientes: {self.sist_dientes}")
        lines.append(f"Número de dientes N: {fmt(self.N)}")
        lines.append(f"Numero virtual de dientes Ne {fmt(self.Ne)}")

        # Módulos
        lines.append(f"m (módulo normal): {fmt(self.m)} mm")
        lines.append(f"m_t (módulo transversal): {fmt(self.m_t)} mm")
        
        # Ángulos
        lines.append(f"φ_n (ángulo presión normal): {rad2deg(self.phi_n)} °")
        lines.append(f"φ_t (ángulo presión transversal): {rad2deg(self.phi_t)} °")
        lines.append(f"ψ (ángulo de hélice): {rad2deg(self.psi)} °")
        lines.append(f"ψ_b (ángulo de hélice en base): {rad2deg(self.psi_b)} °")

        # Diámetros y radios
        lines.append(f"d_p (diámetro paso): {fmt(self.d_p)} mm")
        lines.append(f"r_p (radio paso): {fmt(self.r_p)} mm")
        lines.append(f"d_b (diámetro base): {fmt(self.d_b)} mm")
        lines.append(f"r_b (radio base): {fmt(self.r_b)} mm")
        lines.append(f"d_a (diámetro exterior): {fmt(self.d_a)} mm")
        lines.append(f"r_a (radio exterior): {fmt(self.r_a)} mm")
        lines.append(f"d_r (diámetro raíz): {fmt(self.d_r)} mm")
        lines.append(f"r_r (radio raíz): {fmt(self.r_r)} mm")

        # Alturas y espesores
        lines.append(f"a (addendum): {fmt(self.a)} mm")
        lines.append(f"b (dedendum): {fmt(self.b)} mm")
        lines.append(f"ht (altura total): {fmt(self.ht)} mm")
        lines.append(f"e (espesor en paso): {fmt(self.e)} mm")

        # Holguras y tolerancias
        lines.append(f"Tolerancia: {fmt(self.tolerancia)} mm")

        # Otros parámetros
        lines.append(f"Desplazamiento de perfil xp: {fmt(self.xp)}")
        lines.append(f"Radio de curvatura: {fmt(self.r_curvatura)} mm")
        lines.append(f"Ancho de cara F: {fmt(self.F)} mm")

        return lines
