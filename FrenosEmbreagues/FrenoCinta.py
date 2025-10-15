import numpy as np

def RelacionFuerzas(mu, theta, P1=None, P2=None):
    """
        Parámetros:
        mu     : coeficiente de fricción
        theta : distancia en radianes de lo que alcanza a cubrir la cinta
        P1 : fuerza de reacción
        P2 : fuerza de tiro
    """
    if P1 is None and P2 is None:
        print("Se requiere P1 fuerza de reacción o P2 fuerza tirante")
        return
    if P1 is None:
        print("Calculada P1 reacción")
        return P2*np.exp(mu*theta)
    if P2 is None:
        print("Calculada P2 tirante")
        return P1/np.exp(mu*theta)

def ParFrenado(P1, P2, D):
    """
    P1 : fuerza de reacción
    P2 : fuerza de tiro
    D : diametro del disco a frenar
    """
    return (P1-P2)*D/2

def PresionAdmisible(P1, b, D):
    """
    P1 : fuerza de reacción
    b : ancho de la cinta
    D : diametro del disco a frenar
    """
    return 2*P1/b/D
