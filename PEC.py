import numpy as np
from PEG import ParEngranesGeometria

class ParEngranesCompatibilidad(ParEngranesGeometria):
    def __init__(self):
        super().__init__()
        self.interferencia = None
        self.pinion_min_N = None


    def orientacion_dientes(self, m_g, phi_n, psi, m=None, pi_n=None, sistema_dientes=None):
        """
        Calcula el N mínimo del piñón (Np_min) para el par dado (m, φ_t, ψ) y,
        a partir de la transmisión m_g = Ng/Np, calcula Ng. Usa el método
        minimo_dientes(...) que no depende del estado del objeto.

        Return
        ------
        dict con m, phi_t, psi, m_g, sistema_dientes, clase, Np_min, Ng, mensaje
        """
        # --- módulo ---
        if m is None and pi_n is not None:
            m = 25.4 / float(pi_n)  # conversión PD -> módulo [mm]
        if m is None:
            raise ValueError("Debes proporcionar 'm' o 'pi_n'.")

        if m_g is None or m_g <= 0:
            raise ValueError("m_g (Ng/Np) debe ser > 0.")

        # clase por ψ
        clase = 'heli' if abs(float(psi)) > 0.0 else 'recto'
        sd = sistema_dientes or getattr(self, "sistema_dientes", "total")
        phi_n = np.deg2rad(float(phi_n))
        phi_t = np.arctan(np.tan(phi_n)/np.cos(np.deg2rad(float(psi))))
        psi=np.deg2rad(float(psi))

        
        # obtener Np mínimo con tu función independiente
        Np_min, msg = self.minimo_dientes(
            clase=clase,
            phi_t=phi_t,
            psi=psi,
            m_g=m_g,
            sistema_dientes=sd
        )

        Ng = int(np.ceil(m_g * Np_min)) if Np_min is not None else None

        print("=== Dientes desde transmisión ===")
        print(f"m (módulo normal): {self._fmt(m)} mm")
        print(f"φ_n (presion): {self._deg(phi_t)}°")
        print(f"ψ (hélice): {self._deg(psi)}°")
        print(msg)
        print(f"Relación m_g = Ng/Np: {self._fmt(m_g, 3)}")
        if Ng is not None:
            print(f"Número de dientes requerido en el engrane (Ng): {Ng}")



    # ----------------- helpers -----------------
    def _fmt(self, x, nd=2):
        if x is None:
            return "-"
        if isinstance(x, int):
            return f"{x}"
        if isinstance(x, float):
            return f"{x:.{nd}f}"
        return str(x)

    def _deg(self, x, nd=2):
        return "-" if x is None else f"{np.degrees(x):.{nd}f}"

    def _dims(self):
        """Obtiene dimensiones necesarias desde piñón/engrane (seguro)."""
        if self.pinion is None or self.engrane is None:
            raise RuntimeError("Debes inicializar el par (set_par) antes de chequear compatibilidad.")
        return {
            # Piñón
            "rb_p": float(self.pinion.r_b), "rr_p": float(self.pinion.r_r),
            "a_p": float(self.pinion.a),    "b_p": float(self.pinion.b),
            # Engrane
            "rb_g": float(self.engrane.r_b), "rr_g": float(self.engrane.r_r),
            "a_g":  float(self.engrane.a),   "b_g":  float(self.engrane.b),
        }

    # ----------------- chequeos -----------------
    def check_interference(self):
        """
        Criterios básicos anti-interferencia. Si alguno falla -> hay interferencia.
        Define self.interferencia = True/False. Devuelve lista de mensajes.
        """
        d = self._dims()
        rb_g, rr_g, a_g = d["rb_g"], d["rr_g"], d["a_g"]
        rb_p, rr_p, a_p, b_p = d["rb_p"], d["rr_p"], d["a_p"], d["b_p"]

        lines = []
        # --- Criterios de interferencia (según tu planteo) ---
        c1 = (rb_g - rr_g) < 0.25 * a_g
        c2 = (rb_p - rr_p) < 0.25 * a_p
        c3 = (rb_p - rr_p) < (b_p - a_g)

        self.interferencia = not (c1 and c2 and c3)

        if not c1:
            lines.append(f"Criterio 1 NO se cumple (engrane): {self._fmt(rb_g - rr_g)} < {self._fmt(0.25*a_g)}")
        if not c2:
            lines.append(f"Criterio 2 NO se cumple (piñón): {self._fmt(rb_p - rr_p)} < {self._fmt(0.25*a_p)}")
        if not c3:
            lines.append(f"Criterio 3 NO se cumple: {self._fmt(rb_p - rr_p)} < {self._fmt(b_p - a_g)}")

        if c1 and c2 and c3:
            lines.append("No hay interferencia (todos los criterios se cumplen).")

        lines.append(f"Interferencia: {'SÍ' if self.interferencia else 'NO'}")
        return lines

    def check_contacto(self):
        """
        Verifica razones de contacto y condiciones de ancho de cara.
        Devuelve lista de mensajes.
        """
        lines = []

        # --- Razón de contacto tangencial ---
        if self.m_p is None:
            lines.append("Razón de contacto tangencial m_p: no calculada.")
        else:
            if self.m_p < 1.4 or self.m_p > 2.0:
                lines.append(f"Razón de contacto m_p fuera de rango (recomendado ~1.4–2.0): {self._fmt(self.m_p)}")
            else:
                lines.append(f"Razón de contacto m_p OK: {self._fmt(self.m_p)}")

        # --- Razón de solape axial (helicoidal) ---
        if self.clase == 'heli':
            m_f = 0.0 if self.m_f in (None, 0) else float(self.m_f)
            if m_f < 1.15:
                lines.append(f"Razón de solape m_f (axial) INSUFICIENTE: {self._fmt(m_f)} < 1.15")
            else:
                lines.append(f"Razón de solape m_f (axial) OK: {self._fmt(m_f)}")

            # Verificaciones de ancho de cara vs paso axial
            if self.p_x not in (None, 0) and self.F not in (None, 0):
                lines.append(f"Verificación F > p_x: {'OK' if (self.F > self.p_x) else 'NO'} "
                             f"({self._fmt(self.F)} > {self._fmt(self.p_x)})")
            else:
                lines.append("Verificación F > p_x: N/A (p_x o F no definidos)")

            # F > 3*m_t / tan(psi)
            if self.F not in (None, 0) and self.m_t not in (None, 0) and self.psi not in (None, 0):
                tanpsi = np.tan(self.psi)
                lim = 3.0 * self.m_t / tanpsi if abs(tanpsi) > 1e-12 else np.inf
                ok = self.F > lim
                lines.append(f"Verificación F > 3*m_t/tan(psi): {'OK' if ok else 'NO'} "
                             f"({self._fmt(self.F)} > {self._fmt(lim)})")
            else:
                lines.append("Verificación F > 3*m_t/tan(psi): N/A (F, m_t o psi no definidos)")
        else:
            lines.append("Razones axiales: N/A (engranaje recto)")

        return lines

    def minimo_dientes(self, clase, phi_t, psi, m_g=None, sistema_dientes="total"):
        """
        Calcula el número mínimo de dientes del piñón (Np_min) para evitar socavado (undercut).
        No usa atributos del objeto, recibe todo por parámetros.

        Parámetros
        ----------
        clase : str
            'recto' o 'heli'
        phi_t : float
            Ángulo de presión transversal [rad]
        psi : float
            Ángulo de hélice [rad]
        m_g : float, opcional
            Relación de transmisión (Ng/Np), necesario si clase='heli'
        sistema_dientes : str
            'total' o 'parcial'

        Devuelve
        --------
        (Np_min, msg)
            Np_min = número mínimo de dientes (int o None si no aplica)
            msg = string con explicación
        """


        # Caso engranaje recto
        if clase == 'recto':
            s = np.sin(phi_t)
            if abs(s) < 1e-12:
                return None, "No se puede calcular N mínimo (sin(φ_t)≈0)."

            if sistema_dientes == "total":
                pinion_min_N = 4 * (1.0 + np.sqrt(1.0 + 3.0 * s * s)) / (6.0 * s * s)
            else:  # 'parcial' -> multiplicador 0.8
                pinion_min_N = 4 * 0.8 * (1.0 + np.sqrt(1.0 + 3.0 * s * s)) / (6.0 * s * s)

            Np_min = int(np.ceil(pinion_min_N))
            self.pinion_min_N = Np_min
            return Np_min, f"N mínimo piñón (recto, {sistema_dientes}): {Np_min}"

        # Caso engranaje helicoidal
        elif clase == 'heli':
            if m_g is None:
                return None, "No se puede calcular N mínimo (m_g no definido)."

            k = 1.0 if sistema_dientes == "total" else 0.8
            s2 = (np.sin(phi_t) ** 2)
            if s2 < 1e-18:
                return None, "No se puede calcular N mínimo (sin^2(φ_t)≈0)."

            numer = 2.0 * k * np.cos(psi)
            denom = (1.0 + 2.0 * m_g) * s2
            inner = m_g + np.sqrt(m_g ** 2 + (1.0 + 2.0 * m_g) * s2)
            Nmin = (numer / denom) * inner

            Np_min = int(np.ceil(Nmin))
            self.pinion_min_N = Np_min
            return Np_min, f"N mínimo piñón (helicoidal, {sistema_dientes}): {Np_min}"

        else:
            return None, "Clase de engrane desconocida para cálculo de dientes mínimos."


    def check_minimo_dientes(self):
        """
        Compara N del piñón con N mínimo calculado.
        """
        lines = []
        if self.pinion is None:
            raise RuntimeError("Piñón no inicializado.")

        if self.pinion_min_N is None:
            lines.append("No fue posible determinar N mínimo del piñón.")
            return lines

        if int(self.pinion.N) < int(self.pinion_min_N):
            lines.append(f"Piñón con dientes INSUFICIENTES: {int(self.pinion.N)} < {int(self.pinion_min_N)}")
        else:
            lines.append(f"Piñón con dientes suficientes: {int(self.pinion.N)} ≥ {int(self.pinion_min_N)}")
        return lines

    def resumen_compatibilidad(self, dec=2):
        lines = []
        lines.append(f"== RESUMEN DE COMPATIBILIDAD (ID {self.id}) ==")
        lines.append(f"Tipo: {self.clase or '-'} | Acople: {self.acople or '-'}")
        lines.append(f"Dientes: Np={self._fmt(getattr(self.pinion,'N',None))} | Ng={self._fmt(getattr(self.engrane,'N',None))}")
        lines.append(f"Ángulos [°]: φ_n={self._deg(self.phi_n)} | φ_t={self._deg(self.phi_t)} | ψ={self._deg(self.psi)}")
        lines.append(f"m_p={self._fmt(self.m_p, dec)} | m_f={self._fmt(self.m_f, dec)} | m_n={self._fmt(self.m_n, dec)}")
        lines.append("")  # separador

        # Interferencia
        lines.append("-- Interferencia --")
        try:
            lines += self.check_interference()
        except Exception as e:
            lines.append(f"(Error en check_interference): {e}")
        lines.append("")

        # Contacto
        lines.append("-- Contacto --")
        try:
            lines += self.check_contacto()
        except Exception as e:
            lines.append(f"(Error en check_contacto): {e}")
        lines.append("")

        # Dientes mínimos
        lines.append("-- Dientes mínimos --")
        try:
            self.minimo_dientes(clase = self.clase, phi_t=self.phi_t,
                                        psi=self.psi, m_g=self.m_g, 
                                        sistema_dientes=self.sistema_dientes)
            
            lines += self.check_minimo_dientes()
        except Exception as e:
            lines.append(f"(Error en mínimo de dientes): {e}")

        texto = "\n".join(lines)

        import os
        ruta = os.path.join(f"conjunto_{self.id}", f"compatibilidad_{self.id}.txt")
        # --- Escritura opcional ---
        with open(ruta, "w", encoding="utf-8") as f:
            f.write(texto)

        return texto