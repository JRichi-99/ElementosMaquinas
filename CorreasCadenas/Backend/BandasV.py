import numpy as np

kb_kc = {
    "A": {"kb": 220, "kc": 0.561},
    "B": {"kb": 576, "kc": 0.965},
    "C": {"kb": 1600, "kc": 1.716},
    "D": {"kb": 5680, "kc": 3.498},
    "E": {"kb": 10850, "kc": 5.041},
    "3V": {"kb": 230, "kc": 0.425},
    "5V": {"kb": 1098, "kc": 1.217},
    "8V": {"kb": 4830, "kc": 3.288},
}

cantidad_a_sumar = {
    "A": 1.3,
    "B": 1.8,
    "C": 2.9,
    "D": 3.3,
    "E": 4.5
}

def ang_envoltura_menor(D, d, a):
    x = np.clip((D - d) / (2.0 * a), -1.0, 1.0)
    return np.pi - 2.0 * np.arcsin(x)

def ang_cruzada(D, d, a):
    x = np.clip((D + d) / (2.0 * a), -1.0, 1.0)
    return np.pi + 2.0 * np.arcsin(x)

def longitud_no_inversora(D, d, a, seccion):
    return np.pi * (D + d) / 2.0 + (D - d) ** 2 / (4.0 * a) + 2.0 * a + cantidad_a_sumar[seccion]

def a_desde_longitud_no_inversora(L, D, d, seccion):
    Lp = L-cantidad_a_sumar[seccion]
    T = Lp - np.pi * (D + d) / 2
    rad = T**2 - 2 * (D - d)**2
    a = 0.25 * (T + np.sqrt(rad))
    return a

def tension_centrifuga(seccion, v):
    return kb_kc[seccion]["kc"]*(v/1000)**2

def tension_flexion(seccion, d):
    return kb_kc[seccion]["kb"]/d

def h_adm_real(h_adm, k1, k2):
    return h_adm*k1*k2

def potencia_demanda(h_nom, k_serv):
    return h_nom * k_serv

def momento_d(h, wd):
    return 63025.0 * h / wd

def velocidad_tangencial_d(d, wd):
    return np.pi * d * wd / 12.0

def numero_bandas(h_dem, h_adm_real):
    n = np.ceil(h_dem / h_adm_real)
    return int(np.maximum(1, n))

def t1_adm(tc, m_adm, d, f, theta_d):
    return tc + (m_adm / d) * (2 * np.exp(f * theta_d)) / (np.exp(f * theta_d) - 1)

def t2(t1_adm, m_adm, d):
    return t1_adm - 2 * m_adm / d

def ti(t1_adm, t2, tc):
    return (t1_adm+t2)/2-tc


def V_verificar_diseño_no_inversora(D, d, a, lp, h_nom, k_serv, n_seg, t, f, gamma, b, wd, t1_adm, write=False):
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
    
    t1_adm_real = tension_admisible_real(b, t1_adm, c_p, c_v)

    t2 = t2_por_momento(t1_adm_real, m_adm, d)
    ti = tension_inicial_tensiones(t1_adm_real, t2, tc)
    f_adm = mu_desde_relacion_tensiones(t1_adm_real, t2, tc, theta_d)

