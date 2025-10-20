import sympy as sp
from .simbolico_utils import resolver, consultar_ecuaciones, resolver_auto

Lp, a, d_big, d_small, d,  = sp.symbols('Lp a D d', real=True)
T1, T2, Tc, Tb,  phi_d, f, f_efectiva = sp.symbols('T1 T2 Tc Tb phi_d f f_efectiva', real=True)
m, r, w, V, b, t, gamma = sp.symbols('m r w V b t gamma', real=True)
Hnom, Ks, Hd, nd = sp.symbols('Hnom Ks Hd nd', real=True)
Hadm, Hadmreal, Tadm, Tamdreal, Cp, Cv = sp.symbols('Hadm Hamdreal Tadm Tamdreal Cp Cv', real=True)
Tinicial, fadm, Madm = sp.symbols('Tinicial fadm Madm', real=True)
theta_d, theta_D, theta_x, beta = sp.symbols('theta_d, theta_D, theta_x, beta', real=True)
Kc, Kb, K1, K2, Nb = sp.symbols('Kc Kb K1 K2 Nb', real=True)
P1, P2 = sp.symbols('P1 P2', real=True)

SYMS = {s.name: s for s in [
    Lp, a, d_big, d,
    T1, T2, Tc, phi_d, f,
    m, r, w, V, b, t, gamma,
    Hnom, Ks, Hd, nd,
    Hadm, Tadm, Tamdreal, Cp, Cv,
    Tinicial, fadm, Madm
]}


eq_longitudcorrea_no_inversora = sp.Eq(Lp, sp.pi*(d + d_big)*sp.Rational(1, 2) + (d_big - d)**2/(4*a) + 2*a)
eq_theta_d_small = sp.Eq(theta_d, sp.pi-2*sp.asin((d_big-d)/(2*a)))
eq_theta_d_big = sp.Eq(theta_d, sp.pi+2*sp.asin((d_big-d)/(2*a)))
eq_theta_x = sp.Eq(theta_x, sp.Eq(theta_d, sp.pi+2*sp.asin((d_big+d)/(2*a))))

eq_longitudcorrea_inversora = sp.Eq(Lp,sp.sqrt(4*a**2-(d_big+d)**2)+0.5*(d_big+d)*theta_x)
eq_friccionefectiva = sp.Eq(f_efectiva, f/sp.sin(beta))

eq_tensioncentrifuga = sp.Eq(Tc, Kc*(V/1000)**2)
eq_tensionflexion_small = sp.Eq(Tb, Kb/d_small)
eq_tensionflexion_big = sp.Eq(Tb, Kb/d_big)

eq_potenciaadmisiblereal = sp.Eq(Hadmreal, Hadm*K1*K2)

eq_bandas = sp.Eq((T1 - Tc)/(T2 - Tc), sp.exp(f_efectiva * phi_d))
eq_velocidadtangencial = sp.Eq(V, r * w)

eq_potenciatransmitida = sp.Eq(Hnom, (T1 - T2) * V)
eq_tensiontransmitida = sp.Eq(Tadm, Madm * 2 / d)
eq_momentotransmitido = sp.Eq(Madm, Hadm / w)

eq_tensioninicial = sp.Eq(Tinicial, (Tamdreal + T2)/2 - Tc)
eq_P1 = sp.Eq(ten)

eq_Hd = sp.Eq(Hd, Hnom * Ks)
eq_factorseguridad = sp.Eq(nd, Nb *Hadmreal / Hd)





ECUACIONES = {
}

def solve_eq(nombre_eq, objetivo=None, **kwargs):
    return resolver(nombre_eq, ECUACIONES, SYMS, objetivo, **kwargs)

def solve_auto(nombre_eq, objetivo, params):
    return resolver_auto(nombre_eq, objetivo, params, ECUACIONES=ECUACIONES, SYMS=SYMS)

def consultar():
    consultar_ecuaciones(ECUACIONES)
