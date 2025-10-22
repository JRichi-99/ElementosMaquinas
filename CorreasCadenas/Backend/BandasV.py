import numpy as np

kb_kc = {
    "A": {"kb": 220, "kc": 0.561},
    "B": {"kb": 576, "kc": 0.965},
    "C": {"kb": 1600, "kc": 1.716},
    "D": {"kb": 5680, "kc": 3.498},
    "E": {"kb": 10850, "kc": 5.041}
}

cantidad_a_sumar = {"A": 1.3, "B": 1.8, "C": 2.9, "D": 3.3, "E": 4.5}

K_banda = {
    "A": {"K": 674,  "b": 11.089},
    "B": {"K": 1193, "b": 10.926},
    "C": {"K": 2038, "b": 11.173},
    "D": {"K": 4208, "b": 11.105},
    "E": {"K": 6061, "b": 11.100},
}

def ang_envoltura_menor(D, d, a):
    x = np.clip((D - d) / (2.0 * a), -1.0, 1.0)
    return np.pi - 2.0 * np.arcsin(x)

def ang_cruzada(D, d, a):
    x = np.clip((D + d) / (2.0 * a), -1.0, 1.0)
    return np.pi + 2.0 * np.arcsin(x)

def longitud_no_inversora(D, d, a):
    return np.pi * (D + d) / 2.0 + (D - d)**2 / (4.0 * a) + 2.0 * a 

def a_desde_longitud_no_inversora(Lp, D, d):
    T = Lp - np.pi * (D + d) / 2.0
    rad = T*T - 2.0 * (D - d)**2
    if rad < 0:
        raise ValueError("Raíz negativa: revisa Lp, D, d.")
    return 0.25 * (T + np.sqrt(rad))

def tension_centrifuga(seccion, v):
    return kb_kc[seccion]["kc"] * (v/1000.0)**2

def tension_flexion(seccion, diam):
    return kb_kc[seccion]["kb"] / diam

def h_adm_real(h_adm, k1, k2):
    return h_adm * k1 * k2

def potencia_demanda(h_nom, k_serv):
    return h_nom * k_serv

def momento_d(h, wd):
    return 63025.0 * h / wd

def velocidad_tangencial_d(d, wd):
    return np.pi * d * wd / 12.0

def numero_bandas(h_dem, h_adm_real):
    n = np.ceil(h_dem / h_adm_real)
    return int(np.maximum(1, n))

def eq_t1_adm(tc, m_adm, d, f, theta_d):
    e = np.exp(f * theta_d)
    print(e)
    return tc + (m_adm / d) * (2.0 * e) / (e - 1.0)

def eq_t2(t1_adm, m_adm, d):
    return t1_adm - 2.0 * m_adm / d

def eq_ti(t1_adm, t2, tc):
    return 0.5 * (t1_adm + t2) - tc

def eq_p1(t1, tbd):
    return t1 + tbd

def eq_p2(t2, tbD):
    return t2 + tbD

def eq_N(b, K, p):
    return (K / p) ** b   

def V_verificar_diseño_no_inversora(
    seccion, D, d,
    a=None, l=None,
    h_nom=0.0, k_serv=1.0,
    wd=0.0, f=0.0,
    h_adm=None, N_b_in=None,
    write=False
):
    if (a is None) and (l is None):
        raise ValueError("Entregar a o lp como valor")
    if (a is not None) and (l is not None):
        raise ValueError("Entregar solo a o solo lp como valor")

    if a is None:
        lp = l + cantidad_a_sumar[seccion]
        a = a_desde_longitud_no_inversora(lp, D, d)
    else:
        lp = longitud_no_inversora(D, d, a)

    theta_d = ang_envoltura_menor(D, d, a)
    v = velocidad_tangencial_d(d, wd)
    tc = tension_centrifuga(seccion, v)
    h_dem = potencia_demanda(h_nom, k_serv)

    k1 = float(input(f"Ingrese k1 (considerar ángulo {theta_d*180/np.pi:.2f}°): "))
    k2 = float(input(f"Ingrese k2 (considerar Lp {lp}): "))

    if h_adm is None:
        h_adm = float(input(f"Ingrese H_adm por banda (v = {v:.3f}) (d = {d}): "))

    h_adm_r = h_adm_real(h_adm, k1, k2)
    N_b = numero_bandas(h_dem, h_adm_r)
    print(f"Requiere Nb bandas")

    cumple_Nb = False
    if N_b_in is not None:
        cumple_Nb = (N_b <= N_b_in)
        print("No cumple Nb porque son muy pocas")
    if N_b <= 4:
        cumple_Nb  = True
        print("Cumple con 4 o menos bandas")
    

    m_adm = momento_d(h_dem / N_b, wd)
    t1a = eq_t1_adm(tc, m_adm, d, f, theta_d)
    t2v = eq_t2(t1a, m_adm, d)
    ti0 = eq_ti(t1a, t2v, tc)

    tbd = tension_flexion(seccion, d)
    tbD = tension_flexion(seccion, D)
    p1 = eq_p1(t1a, tbd)
    p2 = eq_p2(t2v, tbD)

    n1 = eq_N(K_banda[seccion]["b"], K_banda[seccion]["K"], p1)
    n2 = eq_N(K_banda[seccion]["b"], K_banda[seccion]["K"], p2)
    n_parallel = 1.0 / (1.0/n1 + 1.0/n2)
    if n_parallel > 1e9:
        n_parallel = 1e9
    horas = lp * n_parallel / (720.0 * v)

    if write:
        fname = "V_verificar_diseno_no_inversora.txt"
        with open(fname, "w", encoding="utf-8") as ftxt:
            ftxt.write("=== VERIFICACIÓN DISEÑO BANDA PLANA — NO INVERSORA ===\n\n")
            ftxt.write(">> ENTRADAS\n")
            ftxt.write(f"Sección: {seccion}\nD: {D}\nd: {d}\na: {a}\nl: {l}\nLp: {lp}\n")
            ftxt.write(f"h_nom: {h_nom}\nk_serv: {k_serv}\nwd: {wd}\nf: {f}\n")
            ftxt.write(f"h_adm: {h_adm}\nk1: {k1}\nk2: {k2}\nN_b_in: {N_b_in}\n\n")

            ftxt.write(">> RESULTADOS INTERMEDIOS\n")
            ftxt.write(f"θ_d (rad): {theta_d}\nθ_d (deg): {np.degrees(theta_d)}\n")
            ftxt.write(f"v: {v}\nTc: {tc}\nH_dem: {h_dem}\nH_adm_real: {h_adm_r}\n")
            ftxt.write(f"N_b mínimo: {N_b}\n")
            if cumple_Nb is not None:
                ftxt.write(f"¿Cumple N_b_in? {'SÍ' if cumple_Nb else 'NO'}\n")
            ftxt.write(f"m_adm: {m_adm}\nT1_adm: {t1a}\nT2: {t2v}\nT_inicial: {ti0}\n")
            ftxt.write(f"tbd: {tbd}\ntbD: {tbD}\nP1: {p1}\nP2: {p2}\n")
            ftxt.write(f"n1: {n1}\nn2: {n2}\nn_parallel: {n_parallel}\n")
            ftxt.write(f"Duración estimada: {horas:.2f} horas\n\n")

            ftxt.write(">> RESUMEN FINAL\n")
            ftxt.write(f"a: {a}\nLp: {lp}\nN_b: {N_b}\n")
            ftxt.write(f"Duración (horas): {horas:.2f}\n")

        print(f"Archivo generado: {fname}")
    else:
        print("\n=== RESULTADOS DEL DISEÑO NO INVERSORA ===")
        print(f"a: {a:.3f}\nLp: {lp:.3f}\nθ_d: {np.degrees(theta_d):.2f}°\n"
              f"v: {v:.3f}\nTc: {tc:.3f}\nH_dem: {h_dem:.3f}\n"
              f"H_adm_real: {h_adm_r:.3f}\nN_b: {N_b}\n"
              f"T1_adm: {t1a:.3f}\nT2: {t2v:.3f}\nTi: {ti0:.3f}\n"
              f"P1: {p1:.3f}\nP2: {p2:.3f}\nDuración: {horas:.2f} horas\n"
              "==========================================\n")

    return cumple_Nb

print(longitud_no_inversora(33,11,45))