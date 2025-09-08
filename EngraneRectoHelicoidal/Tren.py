from PER import ParEngranesResistencia as PER
import numpy as np

class TrenEngrane():
    def __init__(self):
        self.pares = {}
        self.conexiones = {}

    def add_pair(self, par:PER):
        self.pares[par.id] = par
    
    def connect(self, id1, id2, efrom, eto):
        # si no existe, inicializamos la lista vacía
        if id1 not in self.conexiones:
            self.conexiones[id1] = []
        if id2 not in self.conexiones:
            self.conexiones[id2] = []
        
        # agregamos conexión en ambos sentidos
        self.conexiones[id1].append({"par": self.pares[id2], "my": efrom, "to": eto})
        self.conexiones[id2].append({"par": self.pares[id1], "my": eto,   "to": efrom})

    
    def solve_transmision(self, start_id, where, H=None, H_units='si', Omega=None, Omega_units='si', T=None, T_units='si'):
        # 1) Setea la carga inicial en el par de arranque
        par: PER = self.pares[start_id]
        par.set_first_load(where=where,
                        H=H, H_units=H_units,
                        Omega=Omega, Omega_units=Omega_units,
                        T=T, T_units=T_units)

        finish = False
        while not finish:
            finish = True
            for par_obj in self.pares.values():
                if par_obj.transmited is False:
                    conexiones = self.conexiones.get(par_obj.id, [])

                    # --- validar: solo 1 conexión por eje (pinion / engrane) ---
                    por_lado = {'pinion': [], 'engrane': []}
                    for c in conexiones:
                        lado = c.get("my")
                        if lado in por_lado:
                            por_lado[lado].append(c)

                    for lado, lst in por_lado.items():
                        if len(lst) > 1:
                            detalles = ", ".join(
                                f"(par {getattr(cc.get('par'), 'id', cc.get('par'))}, to={cc.get('to')})"
                                for cc in lst
                            )
                            raise ValueError(
                                f"Más de una conexión en el eje '{lado}' del par {par_obj.id}: {detalles}"
                            )

                    # --- si hay 0 o 1 por eje, intentamos propagar usando la que exista ---
                    for lado_my in ("pinion", "engrane"):
                        c = por_lado[lado_my][0] if por_lado[lado_my] else None
                        if not c:
                            continue

                        par_conectado: PER = c["par"]  # aquí guardas el OBJETO
                        if par_conectado.transmited:
                            eto = c["to"]
                            if eto == "pinion":
                                Hc, Wc, Tc = par_conectado.pinion.H, par_conectado.pinion.Omega, par_conectado.pinion.T
                            elif eto == "engrane":
                                Hc, Wc, Tc = par_conectado.engrane.H, par_conectado.engrane.Omega, par_conectado.engrane.T
                            else:
                                raise ValueError(f"Lado 'to' inválido en conexión: {eto}")

                            par_obj.set_load_si(Hc, Wc, Tc, where=lado_my)
                            finish = False  # hubo progreso; seguir iterando
                            break  # pasamos al siguiente par



    def resumen_transmision(self, filename="resumen_transmision.txt"):
        """
        Reglas:
        - Par inicial (id 0):
            * si 'engrane' no tiene conexiones => m_g_total = 1 / m_g(0)
            * si 'pinion'  no tiene conexiones => m_g_total = m_g(0)
            * si ambos lados conectados o 0 no existe => m_g_total = m_g(inicio)
        - Cada salto u->v (por eje) es neutro; la operación se aplica en el PAR DESTINO:
            * entrar por 'pinion'  => × m_g(v)
            * entrar por 'engrane' => ÷ m_g(v)
        También imprime resumen local (m_g, m_v, ω, T).
        """
        import numpy as np

        def to_rpm(w):
            return None if w is None else (w * 60.0) / (2.0 * np.pi)

        def f2(x, suf=""):
            if x is None:
                return "-"
            try:
                return f"{float(x):.2f}" + (f" {suf}" if suf else "")
            except Exception:
                return f"{x}" + (f" {suf}" if suf else "")

        if not self.pares:
            with open(filename, "w", encoding="utf-8") as f:
                f.write("No hay pares cargados.\n")
            return

        # ---------- 1) elegir inicio ----------
        ids = sorted(self.pares.keys())
        ids_con_mg = [pid for pid in ids if getattr(self.pares[pid], "m_g", None)]
        if 0 in ids:
            start_id = 0
        elif ids_con_mg:
            start_id = ids_con_mg[0]
        else:
            start_id = ids[0]

        visitados = set()
        orden = []
        pasos = []  # (u_id, v_id, my, to)

        actual, previo = start_id, None

        # ---------- 2) construir cadena lineal (preferir salida por 'engrane' si hay opción) ----------
        while True:
            orden.append(actual)
            visitados.add(actual)

            siguiente, mejor_c = None, None
            for c in self.conexiones.get(actual, []):
                v_par = c.get("par"); v_id = getattr(v_par, "id", v_par)
                if v_id == previo or v_id in visitados:
                    continue
                # preferimos conexión que salga por 'engrane'
                if (mejor_c is None) or (c.get("my") == "engrane" and mejor_c.get("my") != "engrane"):
                    mejor_c, siguiente = c, v_id

            if siguiente is None:
                break

            pasos.append((actual, siguiente, mejor_c.get("my"), mejor_c.get("to")))
            previo, actual = actual, siguiente

        # ---------- 3) resumen local ----------
        lines = []
        lines.append("RESUMEN LOCAL POR PAR")
        for pid in orden:
            par = self.pares[pid]
            mg = getattr(par, "m_g", None); mv = getattr(par, "m_v", None)
            w_p = getattr(par.pinion, "Omega", None); t_p = getattr(par.pinion, "T", None)
            w_e = getattr(par.engrane, "Omega", None); t_e = getattr(par.engrane, "T", None)

            lines.append(f"- Par {pid}: m_g = {f2(mg)}   m_v = {f2(mv)}")
            lines.append(f"    Piñón   →  ω = {f2(w_p,'rad/s')}  ({f2(to_rpm(w_p),'rpm')})   T = {f2(t_p,'N·m')}")
            lines.append(f"    Engrane →  ω = {f2(w_e,'rad/s')}  ({f2(to_rpm(w_e),'rpm')})   T = {f2(t_e,'N·m')}")
        lines.append("")

        # ---------- 4) m_g_total inicial con la nueva condición para el par 0 ----------
        detalle = []
        def mg_par(pid):
            mg = getattr(self.pares[pid], "m_g", None)
            return float(mg) if (mg not in (None, 0)) else 1.0

        if 0 in self.pares:
            mg0 = getattr(self.pares[0], "m_g", None)
            mg0_val = float(mg0) if (mg0 not in (None, 0)) else 1.0
            conns0 = self.conexiones.get(0, [])
            has_p = any(c.get("my") == "pinion" for c in conns0)
            has_e = any(c.get("my") == "engrane" for c in conns0)

            if not has_e and has_p:
                mg_total = 1.0 / mg0_val
                detalle.append(f"Inicio en Par 0: engrane SIN conexión ⇒ m_g_total = 1 / m_g(0) = {mg_total:.4f}")
            elif not has_p and has_e:
                mg_total = mg0_val
                detalle.append(f"Inicio en Par 0: piñón SIN conexión  ⇒ m_g_total = m_g(0) = {mg_total:.4f}")
            else:
                # ambos conectados o aislado: usar m_g(start_id)
                mg_total = mg_par(start_id)
                detalle.append(f"Inicio en Par {start_id}: m_g_total = m_g({start_id}) = {mg_total:.4f}")
        else:
            mg_total = mg_par(start_id)
            detalle.append(f"Inicio en Par {start_id}: m_g_total = m_g({start_id}) = {mg_total:.4f}")

        # ---------- 5) aplicar regla en cada par destino ----------
        for (u_id, v_id, my, to) in pasos:
            mg_v = getattr(self.pares[v_id], "m_g", None)
            if mg_v in (None, 0):
                detalle.append(f"[{u_id} -> {v_id}] entro por {to} (sin m_g destino; no altera)")
                continue

            mg_v = float(mg_v)
            if to == "pinion":
                mg_total *= mg_v
                detalle.append(f"[{u_id} -> {v_id}:pinion]  × m_g({v_id})={mg_v:.4f}  ⇒ m_g_total={mg_total:.4f}")
            elif to == "engrane":
                mg_total /= mg_v
                detalle.append(f"[{u_id} -> {v_id}:engrane] ÷ m_g({v_id})={mg_v:.4f}  ⇒ m_g_total={mg_total:.4f}")
            else:
                detalle.append(f"[{u_id} -> {v_id}] lado destino '{to}' inválido; no altera")

        mv_total = None if mg_total in (None, 0) else (1.0 / mg_total)

        lines.append("TRANSMISIÓN TOTAL (saltos por eje neutros; operación en el par destino)")
        lines += [f"  {s}" for s in detalle]
        lines.append(f"\n  m_g_total = {f2(mg_total)}")
        lines.append(f"  m_v_total = {f2(mv_total)}  (= 1 / m_g_total)")
        lines.append("")

        # ---------- 6) guardar ----------
        with open(filename, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))





