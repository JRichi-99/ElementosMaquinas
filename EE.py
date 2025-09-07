from EG import EngranajeGeometria
import numpy as np

class EngranajeEsfuerzo(EngranajeGeometria):
    def __init__(self):
        super().__init__()
        # Potencia, velocidad y torque
        self.T = None          # N·m
        self.Omega = None      # rad/s
        self.H = None          # W

        # Fuerzas
        self.Wt = None         # N (tangencial)
        self.Wr = None         # N (radial)
        self.Wa = None         # N (axial)
        self.Wn = None         # N (normal al flanco)

        # Cinemática
        self.Vt = None         # m/s (velocidad en el paso)

        self.sigma_c = None
        self.sigma_f = None


    # ----------------- seteo de carga -----------------
    def set_load(self, T=None, Omega=None, H=None):
        # Asignar lo que venga
        if T is not None:     self.T = float(T)
        if Omega is not None: self.Omega = float(Omega)
        if H is not None:     self.H = float(H)

        # Completar el que falte con H = T * Omega
        if self.H is None and (self.T is not None and self.Omega is not None):
            self.H = self.T * self.Omega
        if self.T is None and (self.H is not None and self.Omega is not None and self.Omega != 0.0):
            self.T = self.H / self.Omega
        if self.Omega is None and (self.H is not None and self.T is not None and self.T != 0.0):
            self.Omega = self.H / self.T

        # Validación mínima
        if self.T is None or self.Omega is None or self.H is None:
            raise ValueError("Faltan datos: se requieren dos de (T, Omega, H) para deducir el tercero.")

        self.calc_forces()

    # ----------------- cálculo de fuerzas -----------------
    def calc_forces(self):

        # Wt: usar d_p en mm con T en N·m -> convertir T a N·mm (x1000)
        # Wt = 2*T / d_p  -> 2*(T[N·m]*1000)/d_p[mm] -> N
        self.Wt = 2.0 * float(self.T) * 1000.0 / self.d_p

        # Componentes
        self.Wr = self.Wt * np.tan(float(self.phi_t))
        self.Wa = self.Wt * np.tan(float(self.psi))

        # Fuerza normal al flanco
        self.Wn = self.Wt / (np.cos(self.phi_n) * np.cos(self.psi))

        # Velocidad periférica en el paso: Vt = Omega * r_p (r_p en m)
        self.Vt = float(self.Omega) * (self.r_p/ 1000.0)

    def calc_tensions(self, K_A, K_M, K_S, K_B, K_I, K_V, J, F, C_p, C_F, I):
        """
        Calcula tensiones a flexión (sigma_f) y contacto (sigma_c)
        usando nomenclatura en mayúsculas: K_A, K_M, K_S, K_B, K_I, K_V, J, F, C_p, C_F, I.
        Deja los resultados en self.sigma_f y self.sigma_c.
        """

        Wt = float(self.Wt)
        m_t = float(self.m_t)
        d_p = float(self.d_p)

        # Flexión
        num_f = Wt * K_A * K_M * K_S * K_B * K_I
        denom_f = F * m_t * J *K_V
        self.sigma_f = num_f / denom_f

        # Contacto
        num_c = C_p * np.sqrt(Wt * K_A * K_M * K_S * C_F)
        denom_c = np.sqrt(F * d_p * I * K_V)
        self.sigma_c = num_c / denom_c


    def resume_tension(self, nd=2):
        def fmt(x):
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

        def deg(x):
            import numpy as np
            return "-" if x is None else f"{np.degrees(x):.{nd}f}"

        lines = []
        lines.append("== resumen esfuerzos ==")

        # Carga
        lines.append(f"T [N·m]: {fmt(self.T)}")
        lines.append(f"Omega [rad/s]: {fmt(self.Omega)}")
        lines.append(f"H [W]: {fmt(self.H)}")

        # Fuerzas
        lines.append(f"Wt [N]: {fmt(self.Wt)}")
        lines.append(f"Wr [N]: {fmt(self.Wr)}")
        lines.append(f"Wa [N]: {fmt(self.Wa)}")
        lines.append(f"Wn [N]: {fmt(self.Wn)}")

        # Cinemática
        lines.append(f"Vt [m/s]: {fmt(self.Vt)}")

        # Tensiones
        lines.append(f"sigma_f [MPa]: {fmt(self.sigma_f)}")
        lines.append(f"sigma_c [MPa]: {fmt(self.sigma_c)}")




        return lines




