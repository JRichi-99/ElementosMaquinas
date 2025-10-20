import sympy as sp
from .simbolico_utils import resolver, consultar_ecuaciones, resolver_auto

R, p_prom = sp.symbols('R p_prom', real=True)
mu, requiv = sp.symbols('mu requiv', real=True)
F, T = sp.symbols('F T', real=True)

SYMS = {s.name: s for s in [R, p_prom, mu, requiv, F, T]}

eq_fuerzafrenado = sp.Eq(F, sp.pi * R * p_prom)
eq_parfrenado = sp.Eq(T, mu * F * requiv)

ECUACIONES = {
    "fuerzafrenado": eq_fuerzafrenado,
    "parfrenado": eq_parfrenado,
}

def solve_eq(nombre_eq, objetivo=None, **kwargs):
    return resolver(nombre_eq, ECUACIONES, SYMS, objetivo, **kwargs)

def solve_auto(nombre_eq, objetivo, params):
    return resolver_auto(nombre_eq, objetivo, params, ECUACIONES=ECUACIONES, SYMS=SYMS)

def consultar():
    consultar_ecuaciones(ECUACIONES)