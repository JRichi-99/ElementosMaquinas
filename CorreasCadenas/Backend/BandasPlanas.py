import numpy as np

# -------- helpers numéricos --------
def ang_envoltura_menor(D, d, a):
    x = np.clip((D - d) / (2.0 * a), -1.0, 1.0)
    return np.pi - 2.0 * np.arcsin(x)

def ang_cruzada(D, d, a):
    x = np.clip((D + d) / (2.0 * a), -1.0, 1.0)
    return np.pi + 2.0 * np.arcsin(x)

def longitud_no_inversora(D, d, a):
    return np.pi * (D + d) / 2.0 + (D - d) ** 2 / (4.0 * a) + 2.0 * a

def a_desde_longitud_no_inversora(Lp, D, d):
    T = Lp - np.pi * (D + d) / 2
    rad = T**2 - 2 * (D - d)**2
    a = 0.25 * (T + np.sqrt(rad))
    return a

def longitud_inversora(D, d, a):
    theta_x = ang_cruzada(D, d, a)
    return np.sqrt(4.0 * a ** 2 - (D + d) ** 2) + 0.5 * (D + d) * theta_x

def velocidad_tangencial_d(d, wd):
    # v = pi * d * wd / 12  (según tu fórmula)
    return np.pi * d * wd / 12.0

def tension_centrifuga(gamma, b, t, v):
    # tc = 12*gamma/32.17 * b * t * (v/60)^2
    return 12.0 * gamma / 32.17 * b * t * (v / 60.0) ** 2

def potencia_demanda(h_nom, k_serv):
    return h_nom * k_serv

def h_admisible(h_dem, n_seg):
    # n_seg = h_adm / h_dem  =>  h_adm = n_seg * h_dem
    return n_seg * h_dem

def momento_d(h, wd):
    # md = 63025 * h / wd
    return 63025.0 * h / wd

def tension_admisible_real(b, t_adm, c_p, c_v):
    return b * t_adm * c_p * c_v

def t2_por_momento(t1, m, d):
    # t2 = t1 - 2*m/d
    return t1 - 2.0 * m / d

def tension_inicial_tensiones(t1, t2, tc):
    # ti = (t1 + t2)/2 - tc
    return (t1 + t2) / 2.0 - tc

def mu_desde_relacion_tensiones(t1, t2, tc, theta):
    # (t1 - tc)/(t2 - tc) = exp(mu * theta)  =>  mu = ln((t1 - tc)/(t2 - tc)) / theta
    ratio = (t1 - tc) / (t2 - tc)
    return np.log(ratio) / theta

def formato_fraccion(valor, base=64):
    # denominador fijo: redondea al múltiplo más cercano de 1/base
    num = round(valor * base)
    return num

def plana_verificar_diseño_no_inversora(D, d, a, lp, h_nom, k_serv, n_seg, t, f, gamma, b, wd, t1_adm, write=False):
    if a is None and lp is None:
        raise ValueError("Entregar a o lp como valor")
    if a is not None and lp is not None:
        raise ValueError("Entregar solo a o solo lp como valor")
    if a is not None:
        lp = longitud_no_inversora(D, d, a)
    if lp is not None:
        a = a_desde_longitud_no_inversora(D,d,lp)

    theta_d = ang_envoltura_menor(D, d, a)

    v = velocidad_tangencial_d(d, wd)
    tc = tension_centrifuga(gamma, b, t, v)

    h_dem = potencia_demanda(h_nom, k_serv)
    h_adm = h_admisible(h_dem, n_seg)
    m_adm = momento_d(h_adm, wd)

    c_p = float(input(f"Ingrese c_p | considerar d = {d}: "))
    c_v = float(input(f"Ingrese c_v | considerar v = {v*1e-3} y t = {formato_fraccion(t)}: "))
    t1_adm_real = tension_admisible_real(b, t1_adm, c_p, c_v)

    t2 = t2_por_momento(t1_adm_real, m_adm, d)
    ti = tension_inicial_tensiones(t1_adm_real, t2, tc)
    f_adm = mu_desde_relacion_tensiones(t1_adm_real, t2, tc, theta_d)

    ok = (f_adm <= f)
    if not write:
        return ok

    fname = "verificar_diseno_no_inversora.txt"
    with open(fname, "w", encoding="utf-8") as ftxt:
        ftxt.write("Verificar DISEÑO BANDA PLANA (No inversora)\n\n")
        ftxt.write("PARÁMETROS DE ENTRADA:\n")
        ftxt.write(f"D = {D}\n")
        ftxt.write(f"d = {d}\n")
        ftxt.write(f"a = {a}\n")
        ftxt.write(f"h_nom = {h_nom}\n")
        ftxt.write(f"k_serv = {k_serv}\n")
        ftxt.write(f"n_seg = {n_seg}\n")
        ftxt.write(f"t(ref) = {t}\n")
        ftxt.write(f"mu_max = {f}\n")
        ftxt.write(f"gamma(ref) = {gamma}\n\n")

        ftxt.write("ENTRADAS (interactivas):\n")
        ftxt.write(f"wd = {wd}\n")
        ftxt.write(f"gamma = {gamma}\n")
        ftxt.write(f"b = {b}\n")
        ftxt.write(f"t = {t}\n")
        ftxt.write(f"t_adm = {t1_adm}\n")
        ftxt.write(f"c_p = {c_p}\n")
        ftxt.write(f"c_v = {c_v}\n\n")

        ftxt.write("RESULTADOS:\n")
        ftxt.write(f"theta_d = {theta_d}\n")
        ftxt.write(f"lp = {lp}\n")
        ftxt.write(f"v = {v}\n")
        ftxt.write(f"tc = {tc}\n")
        ftxt.write(f"h_dem = {h_dem}\n")
        ftxt.write(f"h_adm = {h_adm}\n")
        ftxt.write(f"m_adm_d = {m_adm}\n")
        ftxt.write(f"t1_adm = {t1_adm}\n")
        ftxt.write(f"t1_adm_real = {t1_adm_real}\n")
        ftxt.write(f"t2 = {t2}\n")
        ftxt.write(f"ti = {ti}\n")
        ftxt.write(f"mu_admisible = {f_adm}\n\n")

        ftxt.write("VEREDICTO:\n")
        ftxt.write("CUMPLE\n" if ok else "NO CUMPLE\n")

    print(f"Archivo generado: {fname}")
    print("CUMPLE" if ok else "NO CUMPLE")
    return ok

# --------- verificador inversora (NumPy) ----------
def plana_verificar_diseño_inversora(D, d, a, h_nom, k_serv, n_seg, t, f, gamma, b, wd, t1_adm, write=False):
    # Nota: el ángulo para correas cruzadas (inversora) es theta_x
    theta_x = ang_cruzada(D, d, a)
    lp = longitud_inversora(D, d, a)

    v = velocidad_tangencial_d(d, wd)
    tc = tension_centrifuga(gamma, b, t, v)

    h_dem = potencia_demanda(h_nom, k_serv)
    h_adm = h_admisible(h_dem, n_seg)
    m_adm = momento_d(h_adm, wd)

    c_p = float(input(f"Ingrese c_p | considerar d = {d}: "))
    c_v = float(input(f"Ingrese c_v | considerar v = {v*1e-3} y t = {formato_fraccion(t)}: "))
    t1_adm_real = tension_admisible_real(b, t1_adm, c_p, c_v)

    t2 = t2_por_momento(t1_adm_real, m_adm, d)
    ti = tension_inicial_tensiones(t1_adm_real, t2, tc)
    # Para consistencia con tu código anterior, usa theta_x para la relación de tensiones en inversora
    f_adm = mu_desde_relacion_tensiones(t1_adm_real, t2, tc, theta_x)

    ok = (f_adm <= f)
    if not write:
        return ok

    fname = "verificar_diseno_inversora.txt"
    with open(fname, "w", encoding="utf-8") as ftxt:
        ftxt.write("Verificar DISEÑO BANDA PLANA (Inversora)\n\n")
        ftxt.write("PARÁMETROS DE ENTRADA:\n")
        ftxt.write(f"D = {D}\n")
        ftxt.write(f"d = {d}\n")
        ftxt.write(f"a = {a}\n")
        ftxt.write(f"h_nom = {h_nom}\n")
        ftxt.write(f"k_serv = {k_serv}\n")
        ftxt.write(f"n_seg = {n_seg}\n")
        ftxt.write(f"t(ref) = {t}\n")
        ftxt.write(f"mu_max = {f}\n")
        ftxt.write(f"gamma(ref) = {gamma}\n\n")

        ftxt.write("ENTRADAS (interactivas):\n")
        ftxt.write(f"wd = {wd}\n")
        ftxt.write(f"gamma = {gamma}\n")
        ftxt.write(f"b = {b}\n")
        ftxt.write(f"t = {t}\n")
        ftxt.write(f"t_adm = {t1_adm}\n")
        ftxt.write(f"c_p = {c_p}\n")
        ftxt.write(f"c_v = {c_v}\n\n")

        ftxt.write("RESULTADOS:\n")
        ftxt.write(f"theta_x = {theta_x}\n")
        ftxt.write(f"lp = {lp}\n")
        ftxt.write(f"v = {v}\n")
        ftxt.write(f"tc = {tc}\n")
        ftxt.write(f"h_dem = {h_dem}\n")
        ftxt.write(f"h_adm = {h_adm}\n")
        ftxt.write(f"m_adm_d = {m_adm}\n")
        ftxt.write(f"t1_adm = {t1_adm}\n")
        ftxt.write(f"t1_adm_real = {t1_adm_real}\n")
        ftxt.write(f"t2 = {t2}\n")
        ftxt.write(f"ti = {ti}\n")
        ftxt.write(f"mu_admisible = {f_adm}\n\n")

        ftxt.write("VEREDICTO:\n")
        ftxt.write("CUMPLE\n" if ok else "NO CUMPLE\n")

    print(f"Archivo generado: {fname}")
    print("CUMPLE" if ok else "NO CUMPLE")
    return ok
