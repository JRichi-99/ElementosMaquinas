import sympy as sp
from .simbolico_utils import resolver, consultar_ecuaciones, resolver_auto

lp, a, d_grande, d_pequena = sp.symbols('lp a d_grande d_pequena', real=True)
t1, t2, tc, phi_menor, mu = sp.symbols('t1 t2 tc phi_menor mu', real=True)
m, r, w, v, b, t, gamma = sp.symbols('m r w v b t gamma', real=True)
h_nom, k_serv, h_dem, n_seg = sp.symbols('h_nom k_serv h_dem n_seg', real=True)
h_adm, t_adm, t_adm_real, c_p, c_v = sp.symbols('h_adm t_adm t_adm_real c_p c_v', real=True)
t_inicial, f_adm, m_adm = sp.symbols('t_inicial f_adm m_adm', real=True)
theta_menor, theta_mayor, theta_cruzada = sp.symbols('theta_menor theta_mayor theta_cruzada', real=True)

SYMS = {s.name: s for s in [
    lp, a, d_grande, d_pequena,
    t1, t2, tc, phi_menor, mu,
    m, r, w, v, b, t, gamma,
    h_nom, k_serv, h_dem, n_seg,
    h_adm, t_adm, t_adm_real, c_p, c_v,
    t_inicial, f_adm, m_adm,
    theta_menor, theta_mayor, theta_cruzada
]}

eq_ang_envoltura_menor = sp.Eq(theta_menor, sp.pi - 2*sp.asin((d_grande - d_pequena)/(2*a)))
eq_ang_envoltura_mayor = sp.Eq(theta_mayor, sp.pi + 2*sp.asin((d_grande - d_pequena)/(2*a)))
eq_ang_cruzada = sp.Eq(theta_cruzada, sp.pi + 2*sp.asin((d_grande + d_pequena)/(2*a)))

eq_longitud_no_inversora = sp.Eq(lp, sp.pi*(d_grande + d_pequena)/2 + (d_grande - d_pequena)**2/(4*a) + 2*a)
eq_longitud_inversora = sp.Eq(lp, sp.sqrt(4*a**2 - (d_grande + d_pequena)**2) + sp.Rational(1, 2)*(d_grande + d_pequena)*theta_cruzada)

eq_velocidad_tangencial = sp.Eq(v, r*w)
eq_relacion_tensiones = sp.Eq((t1 - tc)/(t2 - tc), sp.exp(mu*phi_menor))
eq_tension_centrifuga = sp.Eq(tc, gamma/9.81 * b * t * v**2)

eq_potencia_transmitida = sp.Eq(h_nom, (t1 - t2)*v)
eq_momento_admisible = sp.Eq(m_adm, h_adm/w)
eq_tension_admisible = sp.Eq(t_adm, m_adm * 2 / d_grande)

eq_tension_admisible_real = sp.Eq(t_adm_real, b*t_adm*c_p*c_v)
eq_tension_inicial = sp.Eq(t_inicial, (t_adm_real + t2)/2 - tc)

eq_potencia_demanda = sp.Eq(h_dem, h_nom*k_serv)
eq_factor_seguridad = sp.Eq(n_seg, h_adm/h_dem)

ECUACIONES = {
    'angulo_envoltura_menor': eq_ang_envoltura_menor,
    'angulo_envoltura_mayor': eq_ang_envoltura_mayor,
    'angulo_cruzada': eq_ang_cruzada,
    'longitud_no_inversora': eq_longitud_no_inversora,
    'longitud_inversora': eq_longitud_inversora,
    'velocidad_tangencial': eq_velocidad_tangencial,
    'relacion_tensiones': eq_relacion_tensiones,
    'tension_centrifuga': eq_tension_centrifuga,
    'potencia_transmitida': eq_potencia_transmitida,
    'momento_admisible': eq_momento_admisible,
    'tension_admisible': eq_tension_admisible,
    'tension_admisible_real': eq_tension_admisible_real,
    'tension_inicial': eq_tension_inicial,
    'potencia_demanda': eq_potencia_demanda,
    'factor_seguridad': eq_factor_seguridad,
}

def solve_eq(nombre_eq, objetivo=None, **kwargs):
    return resolver(nombre_eq, ECUACIONES, SYMS, objetivo, **kwargs)

def solve_auto(nombre_eq, objetivo, params):
    return resolver_auto(nombre_eq, objetivo, params, ECUACIONES=ECUACIONES, SYMS=SYMS)

def consultar():
    consultar_ecuaciones(ECUACIONES)
