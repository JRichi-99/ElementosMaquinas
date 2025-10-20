import sympy as sp
import numpy as np
from .simbolico_utils import resolver, consultar_ecuaciones, resolver_auto

Fn, pmax, theta1, theta2, r, w = sp.symbols('Fn pmax theta1 theta2 r w', real=True)
T, Ff, mu, Fa = sp.symbols('T Ff mu Fa', real=True)
b, a, c = sp.symbols('b a c', real=True)
p, thetaMax = sp.symbols('p thetaMax', real=True)
TFn, TFf = sp.symbols('TFn TFf', real=True)
Rx, Ry = sp.symbols('Rx Ry', real=True)

SYMS = {s.name: s for s in [Fn, pmax, theta1, theta2, r, w, T, Ff, mu, Fa, b, a, c, p, thetaMax, TFn, TFf, Rx, Ry]}

eq_fuerzanormal_corta = sp.Eq(Fn, pmax*r*(theta2-theta1)*w)
eq_fuerzaaplicacion = sp.Eq(Fa, Fn*b*mu*c/a)
eq_fuerzafriccion_corta = sp.Eq(Ff, mu*Fn)
eq_parfrenado_corta = sp.Eq(T, mu*Fn*r)
eq_presion_corta = sp.Eq(p, pmax)
eq_rx_corta = sp.Eq(Rx, Ff)
eq_ry_corta = sp.Eq(Ry, Fn-Fa)

eq_presion_larga = sp.Eq(p, pmax*sp.sin(theta2-theta1)/sp.sin(thetaMax))
eq_parnormal_larga = sp.Eq(T, w*r*b*pmax/sp.sin(thetaMax)*(sp.Rational(1,2)*(theta2-theta1)-sp.Rational(1,4)*(sp.sin(2*theta2)-sp.sin(2*theta1))))
eq_parfriccion_larga = sp.Eq(T, w*r*b*pmax/sp.sin(thetaMax)*(-r*(sp.cos(theta2)-sp.cos(theta1))-b/2*(sp.sin(theta2)**2-sp.sin(theta1)**2)))
eq_fuerzaaplicacion_energizante_larga = sp.Eq(Fa, TFn/a - TFf/a)
eq_fuerzaaplicacion_desenergizante_larga = sp.Eq(Fa, TFn/a + TFf/a)
eq_parfrenado_larga = sp.Eq(T, mu*w*r**2*pmax/sp.sin(thetaMax)*(sp.cos(theta1)-sp.cos(theta2)))
eq_rx_larga = sp.Eq(Rx, w*r*pmax*sp.Rational(1,2)/sp.sin(thetaMax)*(-sp.sin(theta2)**2+mu*theta2-sp.Rational(1,2)*sp.sin(2*theta2)-(-sp.sin(theta1)**2+mu*theta1-sp.Rational(1,2)*sp.sin(2*theta1))))
eq_ry_larga = sp.Eq(Ry, w*r*pmax*sp.Rational(1,2)/sp.sin(thetaMax)*(-mu*sp.sin(theta2)**2+theta2-sp.Rational(1,2)*sp.sin(2*theta2)-(-mu*sp.sin(theta1)**2+theta1-sp.Rational(1,2)*sp.sin(2*theta1))) - Fa)

ECUACIONES = {
    "fuerzanormal_corta": eq_fuerzanormal_corta,
    "fuerzaaplicacion": eq_fuerzaaplicacion,
    "fuerzafriccion_corta": eq_fuerzafriccion_corta,
    "parfrenado_corta": eq_parfrenado_corta,
    "presion_corta": eq_presion_corta,
    "rx_corta": eq_rx_corta,
    "ry_corta": eq_ry_corta,
    "presion_larga": eq_presion_larga,
    "parnormal_larga": eq_parnormal_larga,
    "parfriccion_larga": eq_parfriccion_larga,
    "fuerzaaplicacion_energizante_larga": eq_fuerzaaplicacion_energizante_larga,
    "fuerzaaplicacion_desenergizante_larga": eq_fuerzaaplicacion_desenergizante_larga,
    "parfrenado_larga": eq_parfrenado_larga,
    "rx_larga": eq_rx_larga,
    "ry_larga": eq_ry_larga,
}

def solve_eq(nombre_eq, objetivo=None, **kwargs):
    return resolver(nombre_eq, ECUACIONES, SYMS, objetivo, **kwargs)

def solve_auto(nombre_eq, objetivo, params):
    return resolver_auto(nombre_eq, objetivo, params, ECUACIONES=ECUACIONES, SYMS=SYMS)

def consultar():
    consultar_ecuaciones(ECUACIONES)

def comprobar_autobloqueo(Fa):
    if Fa <= 0:
        print("Autobloqueo")
        return True
    print("no Autobloqueo")
    return False

def factible_autodesenergizante(r,b,theta):
    if r < b*np.cos(theta):
        print("Puede ser autodesenergizante")
        return True
    print("No puede ser autodesenergizante")
    return False