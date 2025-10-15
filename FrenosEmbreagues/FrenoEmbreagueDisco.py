import numpy as np


class PresionUniforme:
    @staticmethod
    def ParFrenado(N, theta1, theta2, mu, pA, rE, rI):
        """
        Par transmitido (T) en un FRENO DE DISCO con PRESIÓN UNIFORME.

        Parámetros:
        N      : número de superficies de fricción en contacto [-]
        theta1 : ángulo inicial de contacto [rad]
        theta2 : ángulo final de contacto [rad]
        mu     : coeficiente de fricción [-]
        pA     : presión axial aplicada [Pa]
        rE     : radio exterior del disco [m]
        rI     : radio interior del disco [m]

        Retorna:
        T [N·m] : par transmitido por fricción
        """
        return N * (theta2 - theta1) * mu * pA * (rE**3 - rI**3) / 3

    @staticmethod
    def FuerzaFrenado(theta1, theta2, pA, rE, rI):
        """
        Fuerza axial total (F) en FRENO DE DISCO con PRESIÓN UNIFORME.

        Parámetros:
        theta1 : ángulo inicial de contacto [rad]
        theta2 : ángulo final de contacto [rad]
        pA     : presión axial aplicada [Pa]
        rE     : radio exterior del disco [m]
        rI     : radio interior del disco [m]

        Retorna:
        F [N]
        """
        return (theta2 - theta1) * pA * (rE**2 - rI**2) / 2

    @staticmethod
    def Presion(pA):
        """
        Presión efectiva en FRENO DE DISCO con PRESIÓN UNIFORME.

        Parámetros:
        pA : presión axial aplicada [Pa]

        Retorna:
        p [Pa] : presión constante
        """
        return pA
    
    @staticmethod
    def RadioEquivalente(rE, rI):
        """
        Calcula el RADIO EQUIVALENTE (r_e) para un freno de disco.

        Fórmula:
            r_e = (2/3) * (rE³ - rI³) / (rE² - rI²)

        Parámetros:
        rE : radio exterior del disco [m]
        rI : radio interior del disco [m]

        Retorna:
        r_e [m] : radio equivalente
        """
        return (2 / 3) * (rE**3 - rI**3) / (rE**2 - rI**2)

    @staticmethod
    def RadioFuerza(theta1, theta2, rE, rI):
        """
        Calcula la COORDENADA DE UBICACIÓN DE LA FUERZA (r̄) en un freno de disco.

        Fórmula:
            r̄ = ((cosθ₁ - cosθ₂) / (θ₂ - θ₁)) * r_e

        Parámetros:
        theta1 : ángulo inicial de contacto [rad]
        theta2 : ángulo final de contacto [rad]
        rE     : radio exterior del disco [m]
        rI     : radio interior del disco [m]

        Retorna:
        r̄ [m] : coordenada del punto de aplicación de la fuerza resultante
        """
        re = PresionUniforme.RadioEquivalente(rE, rI)
        return ((np.cos(theta1) - np.cos(theta2)) / (theta2 - theta1)) * re

    @staticmethod
    def ParMaxrI():
        """
        Parámetros:
        rE     : radio exterior del disco [m]

        Retorna:
        rI [m] : radio interior del disco para que el par de frenado sea máximo
        """
        return 0


class DesgasteUniforme:
    @staticmethod
    def ParFrenado(N, theta1, theta2, mu, pA, ri, rE, rI):
        """
        Par transmitido (T) en FRENO DE DISCO con DESGASTE UNIFORME.

        Parámetros:
        N      : número de superficies en contacto [-]
        theta1 : ángulo inicial [rad]
        theta2 : ángulo final [rad]
        mu     : coeficiente de fricción [-]
        pA     : presión axial aplicada [Pa]
        ri     : radio medio característico [m]
        rE     : radio exterior [m]
        rI     : radio interior [m]

        Retorna:
        T [N·m]
        """
        return N * (theta2 - theta1) * mu * pA * ri * (rE**2 - rI**2) / 2

    @staticmethod
    def FuerzaFrenado(theta1, theta2, pA, ri, rE, rI):
        """
        Fuerza axial total (F) en FRENO DE DISCO con DESGASTE UNIFORME.

        Parámetros:
        theta1, theta2, pA, ri, rE, rI  (ver ParFrenado)

        Retorna:
        F [N]
        """
        return (theta2 - theta1) * pA * ri * (rE - rI)

    @staticmethod
    def Presion(pA, rI, r):
        """
        Presión local p(r) en FRENO DE DISCO con DESGASTE UNIFORME.

        Parámetros:
        pA : presión axial aplicada [Pa]
        rI : radio interior [m]
        r  : radio de evaluación [m]

        Retorna:
        p(r) [Pa]
        """
        return pA * rI / r

    @staticmethod
    def RadioEquivalente(rE, rI):
        """
        Calcula el RADIO EQUIVALENTE (r_e) como promedio aritmético
        entre los radios exterior e interior de un freno de disco.

        Fórmula:
            r_e = 0.5 * (rE + rI)

        Parámetros:
        rE : radio exterior del disco [m]
        rI : radio interior del disco [m]

        Retorna:
        r_e [m] : radio equivalente
        """
        return 0.5 * (rE + rI)

    @staticmethod
    def RadioFuerza(theta1, theta2, rE, rI):
        """
        Calcula la COORDENADA DE UBICACIÓN DE LA FUERZA RESULTANTE (r̄)
        para un freno de disco.

        Fórmula:
            r̄ = ((cosθ₁ - cosθ₂) / (θ₂ - θ₁)) * r_e

        Parámetros:
        theta1 : ángulo inicial de contacto [rad]
        theta2 : ángulo final de contacto [rad]
        rE     : radio exterior del disco [m]
        rI     : radio interior del disco [m]

        Retorna:
        r̄ [m] : coordenada de aplicación de la fuerza
        """
        re = DesgasteUniforme.RadioEquivalente(rE, rI)
        return ((np.cos(theta1) - np.cos(theta2)) / (theta2 - theta1)) * re
    
    @staticmethod
    def ParMaxrI(rE):
        """
        Parámetros:
        rE     : radio exterior del disco [m]

        Retorna:
        rI [m] : radio interior del disco para que el par de frenado sea máximo
        """
        return np.sqrt(3)/3*rE


class ZapataCircular:
    @staticmethod
    def FuerzaFrenado(R, p_prom):
        """
        Parámetros:
        R     : radio de la zapata circular
        p_prom : presión promedio se calcula con tabla
        
        """
        return np.pi*R*p_prom

    @staticmethod
    def ParFrenado(mu, r_equiv, R, p_prom):
        """
        Parámetros:
        mu     : coeficiente de fricción
        r_equiv : radio equivalente se calcula con tabla
        R     : radio de la zapata circular
        p_prom : presión promedio se calcula con tabla

        """
        return mu*ZapataCircular.FuerzaFrenado(R,p_prom)*r_equiv


