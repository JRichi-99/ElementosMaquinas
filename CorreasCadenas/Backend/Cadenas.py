import numpy as np
from .tablascadenas import h_tab_B, h_tab_A, h_tab_C, dientes_catarina

K2_torones = {
    1: 1.0,
    2: 1.7,
    3: 2.5,
    4: 3.3,
    5: 3.9,
    6: 4.6,
    8: 6.0
}

ansi_paso_pulg = {
    25: 0.250,
    35: 0.375,
    41: 0.500,
    40: 0.500,
    50: 0.625,
    60: 0.750,
    80: 1.000,
    100: 1.250,
    120: 1.500,
    140: 1.750,
    160: 2.000,
    180: 2.250,
    200: 2.500,
    240: 3.000
}

def h_adm_real(h_adm, k1, k2):
    return h_adm * k1 * k2

def potencia_demanda(h_nom, k_serv):
    return h_nom * k_serv

def velocidad_tangencial_d(d, wd):
    return np.pi * d * wd / 12.0

def k1(n_ansi, N1):
    if n_ansi < 80:
        return (N1/17)**1.08
    return (N1/17)**1.5

def _expandir_disponibles(entrada):
    """Convierte una lista con enteros y tuplas (a,b) en una lista ordenada de enteros."""
    out = set()
    for x in entrada:
        if isinstance(x, tuple):
            a, b = x
            out.update(range(int(a), int(b) + 1))
        else:
            out.add(int(x))
    return sorted(out)

def get_catarinas_factibles(mg, ansi_cadenas, n_min=17, tol=0):
    """
    Devuelve {ansi: [(N1, N2, mg), ...]} con N1,N2 factibles.
    tol = 0 usa N2 redondeado exacto; si >0 se permiten vecinos alrededor del redondeo.
    """
    factibles = {}
    for n_ansi in ansi_cadenas:
        disponibles = _expandir_disponibles(dientes_catarina[n_ansi])
        disponibles = [n for n in disponibles if n >= n_min]
        disp_set = set(disponibles)

        pares = []
        for N1 in disponibles:
            N2_teorico = mg * N1
            if tol > 0:
                cand = int(round(N2_teorico))
                candidatos = [cand - 1, cand, cand + 1]
                for N2 in candidatos:
                    if N2 >= N1 and N2 in disp_set and abs(N2 - N2_teorico) <= tol * N2_teorico:
                        pares.append((N1, N2, mg))
                        break
            else:
                N2 = int(round(N2_teorico))
                if N2 >= N1 and N2 in disp_set:
                    pares.append((N1, N2, mg))

        factibles[n_ansi] = pares

    return factibles

def get_ansi_for_rpm(wd, lubricaciones_posibles):
    tablas = {
        "A": h_tab_A,
        "B": h_tab_B,
        "C": h_tab_C,
    }
    resultado = {}
    for tipo in lubricaciones_posibles:
        tabla = tablas.get(tipo)
        if not tabla:
            continue
        rpms = sorted(tabla.keys())
        rpm_valida = None
        for rpm in rpms:
            if rpm >= wd:
                rpm_valida = rpm
                break
        if rpm_valida is None:
            continue
        fila = tabla[rpm_valida]  # {ansi: valor}
        for ansi in fila.keys():
            if ansi not in resultado:
                resultado[ansi] = []
            if tipo not in resultado[ansi]:
                resultado[ansi].append(tipo)
    for ansi in resultado:
        resultado[ansi].sort()
    resultado = dict(sorted(resultado.items(), key=lambda kv: kv[0]))
    return resultado

def catarinas_factibles_por_rpm_y_mg(wd, lubricaciones_posibles, mg, n_min=17, tol=0):
    numeros_ansi_factibles = get_ansi_for_rpm(wd, lubricaciones_posibles)  # {ansi: [tipos]}
    ansi_lista = sorted(numeros_ansi_factibles.keys())
    if not ansi_lista:
        return {}
    pares_por_ansi = get_catarinas_factibles(mg, ansi_lista, n_min=n_min, tol=tol)
    resultado = {}
    for ansi in ansi_lista:
        pares = pares_por_ansi.get(ansi, [])
        if pares:
            resultado[ansi] = {
                "lubricaciones": numeros_ansi_factibles[ansi],
                "pares": pares
            }
    return resultado

def _h_series_por_tipo(wd, ansi, tipo):
    tablas = {"A": h_tab_A, "B": h_tab_B, "C": h_tab_C}
    tabla = tablas.get(tipo, {})
    for rpm in sorted(tabla.keys()):
        if rpm >= wd:
            h = tabla[rpm].get(ansi)
            if h is not None:
                return [(rpm, h)]  # solo la primera coincidencia
    return []  # si no se encuentra nada


def filtrar_resistencia(lubricaciones_posibles, n_ansi, n_torones, mg, wd, ks, h_nom, n_seg):

    factibles_por_ansi = catarinas_factibles_por_rpm_y_mg(wd, lubricaciones_posibles, mg)
    if not factibles_por_ansi:
        print("No se encontraron combinaciones geométricamente factibles.")
        return {}

    # Acumulador global por tipo (lo que espera el siguiente filtro)
    acumulado_por_tipo = {t: [] for t in lubricaciones_posibles}

    for ansi_num in n_ansi:
        info_ansi = factibles_por_ansi.get(ansi_num)
        if not info_ansi:
            # ANSI no factible a las rpm pedidas
            continue

        tipos_disponibles = sorted(set(info_ansi["lubricaciones"]) & set(lubricaciones_posibles))
        pares = info_ansi["pares"]  # [(N1, N2, mg), ...]

        for n_t in n_torones:
            h_dem = ks * h_nom / n_t * n_seg
            K2_val = K2_torones[n_t]

            for (N1, N2, mg_par) in pares:
                k1_val = k1(ansi_num, N1)
                for tipo in tipos_disponibles:
                    series = _h_series_por_tipo(wd, ansi_num, tipo)  # [(rpm, h_tabla), ...]
                    if not series:
                        continue
                    for rpm_usada, h_tabla in series:
                        h_real = h_tabla * k1_val * K2_val
                        if h_real >= h_dem:
                            acumulado_por_tipo[tipo].append({
                                "ansi": ansi_num,
                                "N1": N1,
                                "N2": N2,
                                "mg": mg_par,
                                "n_t": n_t,
                                "rpm": rpm_usada,
                                "h_tabla": h_tabla,
                                "k1": k1_val,
                                "K2": K2_val,
                                "h_real": float(h_real),
                                "h_dem": float(h_dem),
                            })

    # Limpieza de tipos vacíos
    acumulado_por_tipo = {t: v for t, v in acumulado_por_tipo.items() if v}
    return acumulado_por_tipo

def look_chain(lubricaciones_posibles, n_ansi, n_torones, mg, wd, ks, h_nom, n_seg):
    """
    Azúcar para ejecutar sólo el filtro de resistencia.
    """
    return filtrar_resistencia(lubricaciones_posibles, n_ansi, n_torones, mg, wd, ks, h_nom, n_seg)

# --- Bloque geométrico de longitudes (versión única y coherente) ---

def eq_L_sobre_p(C, p, C_p, N1, N2, tol):
    """
    Devuelve (L_p_entero, rinde_bool, L_p_real) para la ecuación de longitud sobre paso.
    Si C_p es None, se calcula como C/p.
    """
    if C_p is None:
        C_p = C / p
    term1 = 2 * C_p
    term2 = (N1 + N2) / 2
    term3 = (N2 - N1)**2 / (4 * (np.pi**2) * C_p)
    Lp_real = term1 + term2 + term3
    Lp_int = int(round(Lp_real))
    rinde = abs((Lp_real - Lp_int) / Lp_real) <= tol
    return Lp_int, rinde, Lp_real

def eq_C_p(L, p, L_p, N1, N2):
    """
    Resuelve C/p a partir de L/p (= L_p), N1, N2.
    Si L_p es None, se calcula como L/p.
    Retorna C_p (adimensional).
    """
    if L_p is None:
        L_p = L / p
    A = (N1 + N2)/2 - L_p
    C_p = 0.25 * (-A + np.sqrt(A**2 - 8 * ((N2 - N1)/(2*np.pi))**2))
    return C_p

def obtener_distancias(C=None, p=None, C_p=None, L_p=None, L=None, N1=None, N2=None, tol=0.02):
    """
    Devuelve un dict con caso usado y magnitudes consistentes: {C, p, C_p, L_p, rinde}
    """
    resultado = {}
    if C is not None and p is not None:
        C_p = C / p
        L_p_calc, rinde, _ = eq_L_sobre_p(C, p, C_p, N1, N2, tol)
        resultado.update({
            "caso": "C y p conocidos",
            "C": C,
            "p": p,
            "C_p": C_p,
            "L_p": L_p_calc,
            "rinde": rinde
        })
    elif C_p is not None and p is not None:
        C = C_p * p
        L_p_calc, rinde, _ = eq_L_sobre_p(C, p, C_p, N1, N2, tol)
        resultado.update({
            "caso": "C_p y p conocidos",
            "C": C,
            "p": p,
            "C_p": C_p,
            "L_p": L_p_calc,
            "rinde": rinde
        })
    elif L_p is not None and p is not None:
        C_p_calc = eq_C_p(None, p, L_p, N1, N2)
        C = C_p_calc * p
        resultado.update({
            "caso": "L_p y p conocidos",
            "p": p,
            "C": C,
            "C_p": C_p_calc,
            "L_p": L_p,
            "rinde": True
        })
    elif L is not None and p is not None:
        L_p_calc = L / p
        C_p_calc = eq_C_p(L, p, L_p_calc, N1, N2)
        C = C_p_calc * p
        resultado.update({
            "caso": "L y p conocidos",
            "p": p,
            "L": L,
            "L_p": L_p_calc,
            "C": C,
            "C_p": C_p_calc,
            "rinde": True
        })
    else:
        raise ValueError("Faltan datos suficientes: se necesita al menos p y una distancia (C, C_p, L o L_p).")
    return resultado

def filtrar_por_longitud_entera(filtrado_resistencia, C_p, C, tol=0.02):
    """
    filtrado_resistencia: {tipo: [casos...]} tal como retorna filtrar_resistencia()
    Devuelve {tipo: [casos...]} sólo con aquellos que cumplen entero/rendimiento en L/p.
    """
    resultado_entero = {}
    for tipo, lista in filtrado_resistencia.items():
        elegidos = []
        for caso in lista:
            n_ansi = caso["ansi"]
            N1 = caso["N1"]
            N2 = caso["N2"]
            p = ansi_paso_pulg.get(n_ansi)
            if p is None:
                continue
            datos = obtener_distancias(C=C, C_p=C_p, p=p, N1=N1, N2=N2, tol=tol)
            if datos.get("rinde", False):
                caso_filtrado = dict(caso)
                caso_filtrado.update({
                    "L_p": datos["L_p"],
                    "C_p": datos["C_p"],
                    "p": p,
                    "rinde": True
                })
                elegidos.append(caso_filtrado)
        if elegidos:
            resultado_entero[tipo] = elegidos
    return resultado_entero


