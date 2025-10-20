import sympy as sp
from .simbolico_utils import resolver, consultar_ecuaciones, resolver_auto

N, theta1, theta2, mu = sp.symbols('N theta1 theta2 mu', real=True)
pmax = sp.symbols('pmax', real=True)
re, ri = sp.symbols('re ri', real=True)
r = sp.symbols('r', real=True)
T, F, p = sp.symbols('T F p', real=True)
requiv, rbar = sp.symbols('requiv rbar', real=True)

SYMS = {s.name: s for s in [N, theta1, theta2, mu, pmax, ri, re, r, T, F, p, requiv, rbar]}

eq_parfrenado = sp.Eq(T, N*(theta2 - theta1)*mu*pmax*ri*(re**2 - ri**2)/2)
eq_fuerzafrenado = sp.Eq(F, (theta2 - theta1)*pmax*ri*(re - ri))
eq_presion = sp.Eq(p, pmax*ri/r)
eq_radioequivalente = sp.Eq(requiv, (re + ri)/2)
eq_radiofuerza = sp.Eq(rbar, ((sp.cos(theta1) - sp.cos(theta2))/(theta2 - theta1))*requiv)
eq_parmaxri = sp.Eq(ri, sp.sqrt(3)/3 * re)

ECUACIONES = {
    "parfrenado": eq_parfrenado,
    "fuerzafrenado": eq_fuerzafrenado,
    "presion": eq_presion,
    "radioequivalente": eq_radioequivalente,
    "radiofuerza": eq_radiofuerza,
    "parmaxri": eq_parmaxri,
}

def solve_eq(nombre_eq, objetivo=None, **kwargs):
    return resolver(nombre_eq, ECUACIONES, SYMS, objetivo, **kwargs)

def solve_auto(nombre_eq, objetivo, params):
    return resolver_auto(nombre_eq, objetivo, params, ECUACIONES=ECUACIONES, SYMS=SYMS)

def consultar():
    consultar_ecuaciones(ECUACIONES)

