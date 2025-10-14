from .PEC import ParEngranesCompatibilidad as PEC
import numpy as np

class ParEngranesTransmision(PEC):
    def __init__(self):
        super().__init__()
        self.H = None
        self.transmited = False
        self.ciclos_p = None
        self.ciclos_g = None

    def set_ciclos(self, horas, dias, years):
        self.ciclos_p = self.pinion.Omega * 60 / (2*np.pi) * 60 * horas * dias * years
        self.ciclos_g = self.engrane.Omega * 60 / (2*np.pi) * 60 * horas * dias * years
        self.engrane.ciclos = self.ciclos_g
        self.pinion.ciclos = self.ciclos_p


    def set_load_si(self, H, Omega, T, where):
        if "pinion" == where:
            self.pinion.set_load(T=T, Omega=Omega, H=H)
            self.engrane.set_load(T=T*self.m_g, Omega=Omega*self.m_v, H=H)
        elif "engrane" == where:
            self.engrane.set_load(T=T, Omega=Omega, H=H)
            self.pinion.set_load(T=T/self.m_g, Omega=Omega/self.m_v, H=H)
        self.transmited=True

    
    def set_first_load(self, where, H=None, H_units='si', Omega=None, Omega_units='si', T=None, T_units='si'):
        H, Omega, T = self.get_si_input(H=H, H_units=H_units, Omega=Omega, Omega_units=Omega_units,T=T, T_units=T_units)
        self.set_load_si(H=H,Omega=Omega,T=T,where=where)
    
    def get_si_input(self, H=None, H_units='si', Omega=None, Omega_units='si', T=None, T_units='si'):

        # --- potencia ---
        if H is not None:
            if H_units.lower() == 'si':
                H = float(H)
            elif H_units.lower() == 'hp':
                H = float(H) * 745.7
            else:
                raise ValueError(f"unidad de H desconocida: {H_units}")

        # --- velocidad angular ---
        if Omega is not None:
            if Omega_units.lower() == 'si':
                Omega = float(Omega)
            elif Omega_units.lower() == 'rpm':
                Omega = float(Omega) * 2*np.pi/60.0
            else:
                raise ValueError(f"unidad de Omega desconocida: {Omega_units}")

        # --- torque ---
        if T is not None:
            if T_units.lower() == 'si':
                T = float(T)
            elif T_units.lower() in ['lbft', 'lb-ft']:
                T = float(T) * 1.3558      # 1 lb·ft = 1.3558 N·m
            elif T_units.lower() in ['lbin', 'lb-in']:
                T = float(T) * 0.1130      # 1 lb·in = 0.1130 N·m
            else:
                raise ValueError(f"unidad de T desconocida: {T_units}")
        
        if T is None:
            T = H/Omega
        if H is None: 
            H = T*Omega
        if Omega is None:
            Omega = H/T

        return H, Omega, T

    def resumen_transmision(self):
        """
        Escribe un resumen de la transmisión del PAR (piñón/engrane) en:
            ./conjunto_<self.id>/transmision_<self.id>.txt

        Contiene:
        - Dientes N_p, N_g
        - Relación parcial m_g = N_g / N_p
        - ω (rad/s y rpm), T (N·m) y H (W) para piñón y engrane
        - Fuerzas (Wt, Wr, Wa, Wn) y velocidad periférica Vt ya calculadas en los objetos
        - Estado de propagación (transmited)
        """
        import os
        import numpy as np

        def to_rpm(w):
            if w is None:
                return None
            return (w * 60.0) / (2.0 * np.pi)

        def fmt(x, suf=""):
            if x is None:
                return "-"
            try:
                return f"{float(x):.4f}{(' ' + suf) if suf else ''}"
            except Exception:
                return f"{x}{(' ' + suf) if suf else ''}"

        # ruta de salida
        _id = getattr(self, "id", "par")
        out_dir = f"conjunto_{_id}"
        out_file = os.path.join(out_dir, f"transmision_{_id}.txt")
        os.makedirs(out_dir, exist_ok=True)

        # --- PIÑÓN ---
        Np = getattr(self.pinion, "N", None)
        w_p = getattr(self.pinion, "Omega", None)
        t_p = getattr(self.pinion, "T", None)
        h_p = getattr(self.pinion, "H", None)
        w_p_rpm = to_rpm(w_p)
        Wt_p = getattr(self.pinion, "Wt", None)
        Wr_p = getattr(self.pinion, "Wr", None)
        Wa_p = getattr(self.pinion, "Wa", None)
        Wn_p = getattr(self.pinion, "Wn", None)
        Vt_p = getattr(self.pinion, "Vt", None)

        # --- ENGRAJE ---
        Ng = getattr(self.engrane, "N", None)
        w_g = getattr(self.engrane, "Omega", None)
        t_g = getattr(self.engrane, "T", None)
        h_g = getattr(self.engrane, "H", None)
        w_g_rpm = to_rpm(w_g)
        Wt_g = getattr(self.engrane, "Wt", None)
        Wr_g = getattr(self.engrane, "Wr", None)
        Wa_g = getattr(self.engrane, "Wa", None)
        Wn_g = getattr(self.engrane, "Wn", None)
        Vt_g = getattr(self.engrane, "Vt", None)

        lines = []
        lines.append(f"Resumen transmisión del Par {fmt(_id)}")
        lines.append("=" * 72)
        lines.append(f"Estado de propagación (transmited): {getattr(self, 'transmited', None)}")
        lines.append("")
        lines.append("GEOMETRÍA")
        lines.append(f"  * Dientes: N_p={Np}   N_g={Ng}")
        lines.append(f"  * Ventaja mecánica: m_g = N_g/N_p = {fmt(getattr(self, 'm_g', None))}")
        lines.append(f"  * Relación velocidades : m_v = N_p/N_g = {fmt(getattr(self, 'm_v', None))}")
        lines.append("")
        lines.append("CINEMÁTICA Y FUERZAS")
        lines.append("  Piñón")
        lines.append(f"    - ω = {fmt(w_p,'rad/s')}  ({fmt(w_p_rpm,'rpm')})")
        lines.append(f"    - T = {fmt(t_p,'N·m')}   H = {fmt(h_p,'W')}")
        lines.append(f"    - Wt={fmt(Wt_p,'N')}   Wr={fmt(Wr_p,'N')}   Wa={fmt(Wa_p,'N')}   Wn={fmt(Wn_p,'N')}")
        lines.append(f"    - Vt = {fmt(Vt_p,'m/s')}")
        lines.append("  Engrane")
        lines.append(f"    - ω = {fmt(w_g,'rad/s')}  ({fmt(w_g_rpm,'rpm')})")
        lines.append(f"    - T = {fmt(t_g,'N·m')}   H = {fmt(h_g,'W')}")
        lines.append(f"    - Wt={fmt(Wt_g,'N')}   Wr={fmt(Wr_g,'N')}   Wa={fmt(Wa_g,'N')}   Wn={fmt(Wn_g,'N')}")
        lines.append(f"    - Vt = {fmt(Vt_g,'m/s')}")
        lines.append("")

        with open(out_file, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))





        
        
        