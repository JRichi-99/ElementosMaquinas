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
        Recorre la transmisión y escribe:
        - Por PAR: m_g (local) y m_v (local), con 2 decimales.
        - Por NODO (piñón/engrane): ω [rad/s, rpm] y T [N·m], 2 decimales.
        - Relación TOTAL siguiendo la regla:
            * salto engrane -> piñón  => multiplicar por m_g del par destino
            * cualquier otro salto    => dividir por m_g (si aplica)
            m_v_total = 1 / m_g_total.
        """
        import numpy as np
        from collections import deque, defaultdict

        # ---------- helpers ----------
        def to_rpm(w):
            return None if w is None else (w * 60.0) / (2.0 * np.pi)

        def f2(x, suf=""):
            if x is None:
                return "-"
            try:
                return f"{float(x):.2f}" + (f" {suf}" if suf else "")
            except Exception:
                return f"{x}" + (f" {suf}" if suf else "")

        pad  = " " * 2
        pad2 = " " * 6

        # ---------- 1) elegir nodo de referencia (primer lado con ω válido) ----------
        ref = None  # (par_id, 'pinion'|'engrane')
        for par_id in sorted(self.pares.keys()):
            p = self.pares[par_id]
            if getattr(p.pinion, "Omega", None) not in (None, 0):
                ref = (par_id, "pinion"); break
            if getattr(p.engrane, "Omega", None) not in (None, 0):
                ref = (par_id, "engrane"); break
        if ref is None:
            # si no hay ω válidas, escogemos cualquiera para armar el grafo
            any_id = next(iter(self.pares.keys()))
            ref = (any_id, "pinion")

        # ---------- 2) grafo por nodos (par_id, lado) ----------
        # Aristas de malla (dentro del mismo par) y vía eje (entre pares).
        adj = defaultdict(list)  # (par_id, side) -> list of neighbor (par_id, side)

        # malla dentro de cada par (bidireccional)
        for pid, par in self.pares.items():
            adj[(pid, "pinion")].append((pid, "engrane"))
            adj[(pid, "engrane")].append((pid, "pinion"))

        # conexiones vía eje (bidireccional)
        for u_id, edges in self.conexiones.items():
            for e in edges:
                v_par = e.get("par")           # guardaste el OBJETO
                v_id  = getattr(v_par, "id", v_par)
                my    = e.get("my")            # 'pinion' o 'engrane' en u_id
                to    = e.get("to")            # 'pinion' o 'engrane' en v_id
                if my in ("pinion", "engrane") and to in ("pinion", "engrane"):
                    adj[(u_id, my)].append((v_id, to))

        # ---------- 3) BFS para obtener un camino ref -> final ----------
        parent = {}
        dq = deque([ref])
        parent[ref] = None

        while dq:
            node = dq.popleft()
            for nbr in adj[node]:
                if nbr not in parent:
                    parent[nbr] = node
                    dq.append(nbr)

        # elegir un "final": hoja alcanzable (grado 1) o el último visitado
        reachable = set(parent.keys())
        degrees = {n: 0 for n in reachable}
        for u in reachable:
            for v in adj[u]:
                if v in reachable:
                    degrees[u] += 1
        hojas = [n for n, d in degrees.items() if d <= 1]
        final_node = hojas[-1] if hojas else list(reachable)[-1]

        # reconstruir camino ref -> final
        path = []
        cur = final_node
        while cur is not None:
            path.append(cur)
            cur = parent[cur]
        path.reverse()  # desde ref a final

        # ---------- 4) calcular m_g_total según TU REGLA ----------
        mg_total = 1.0
        for i in range(len(path) - 1):
            (par_a, side_a) = path[i]
            (par_b, side_b) = path[i + 1]
            # m_g del par relevante (cuando multiplicamos usamos el del destino;
            # cuando dividimos, el del origen; si falta, se salta)
            if side_a == "engrane" and side_b == "pinion":
                # MULTIPLICA por m_g del par destino
                mg_b = getattr(self.pares[par_b], "m_g", None)
                if mg_b not in (None, 0):
                    mg_total *= mg_b
            else:
                # DIVIDE por m_g del par del paso (origen si viene de piñón a engrane)
                mg_a = getattr(self.pares[par_a], "m_g", None)
                if mg_a not in (None, 0):
                    mg_total /= mg_a

        mv_total = None if (mg_total is None or mg_total == 0) else (1.0 / mg_total)

        # ---------- 5) armar líneas del reporte ----------
        lines = []
        ref_par_id, ref_side = ref
        ref_par = self.pares[ref_par_id]
        w_ref = getattr(ref_par.pinion if ref_side == "pinion" else ref_par.engrane, "Omega", None)
        lines.append(f"Referencia  :  Par {ref_par_id}  —  {ref_side}    ω_ref = {f2(w_ref,'rad/s')}   ({f2(to_rpm(w_ref),'rpm')})")
        lines.append(f"Camino      :  " + "  →  ".join([f"{pid}.{('p' if s=='pinion' else 'e')}" for pid, s in path]))
        lines.append("")

        # Mostrar m_g y m_v locales una sola vez por PAR (en orden de aparición en el camino)
        vistos = set()
        lines.append("RELACIONES LOCALES POR PAR")
        for pid, s in path:
            if pid in vistos:
                continue
            vistos.add(pid)
            par = self.pares[pid]
            lines.append(pad + f"Par {pid}   m_g = {f2(getattr(par, 'm_g', None))}     m_v = {f2(getattr(par, 'm_v', None))}")
        lines.append("")

        # Mostrar nodos con ω y T (orden del camino)
        lines.append("NODOS (ω y T)")
        for pid, s in path:
            par = self.pares[pid]
            if s == "pinion":
                w = getattr(par.pinion, "Omega", None)
                t = getattr(par.pinion, "T", None)
                label = "Piñón"
            else:
                w = getattr(par.engrane, "Omega", None)
                t = getattr(par.engrane, "T", None)
                label = "Engrane"
            lines.append(pad + f"Par {pid}  —  {label:<7}  ω = {f2(w,'rad/s')}   ({f2(to_rpm(w),'rpm')})   T = {f2(t,'N·m')}")

        lines.append("")
        lines.append("RELACIÓN TOTAL DEL TREN")
        lines.append(pad + f"m_g_total  = {f2(mg_total)}   (≈ N_final / N_inicial)")
        lines.append(pad + f"m_v_total  = {f2(mv_total)}   (= 1 / m_g_total)")
        lines.append("")

        # ---------- 6) escribir archivo ----------
        with open(filename, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

