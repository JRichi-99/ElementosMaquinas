import sympy as sp
from .simbolico_utils import resolver, consultar_ecuaciones, resolver_auto

mu, theta = sp.symbols('mu theta', real=True)
P1, P2 = sp.symbols('P1 P2', real=True, positive=True)
D, b = sp.symbols('D b', real=True, positive=True)
T, p_adm = sp.symbols('T p_adm', real=True)

SYMS = {s.name: s for s in [mu, theta, P1, P2, D, b, T, p_adm]}

eq_relacionfuerzas = sp.Eq(P1, P2 * sp.exp(mu * theta))
eq_parfrenado = sp.Eq(T, (P1 - P2) * D / 2)
eq_presionadmisible = sp.Eq(p_adm, 2 * P1 / (b * D))

ECUACIONES = {
    "relacionfuerzas": eq_relacionfuerzas,
    "parfrenado": eq_parfrenado,
    "presionadmisible": eq_presionadmisible,
}

def solve_eq(nombre_eq, objetivo=None, **kwargs):
    return resolver(nombre_eq, ECUACIONES, SYMS, objetivo, **kwargs)

def solve_auto(nombre_eq, objetivo, params):
    return resolver_auto(nombre_eq, objetivo, params, ECUACIONES=ECUACIONES, SYMS=SYMS)

def consultar():
    consultar_ecuaciones(ECUACIONES)
