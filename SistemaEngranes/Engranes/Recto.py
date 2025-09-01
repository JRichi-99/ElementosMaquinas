import numpy as np
from Engrane import Engrane

class Recto(Engrane):
    def __init__(self):
        self.d_p = 0
        self.r_p = 0
        self.d_b = 0
        self.r_b = 0
        self.d_r = 0
        self.r_r = 0
        self.d_a = 0
        self.r_a = 0
        self.a = 0
        self.b = 0
        self.w = 0
        self.T = 0
        self.p_c = 0
        self.p_b = 0
        self.p_d = 0
        self.N = 0
        self.m = 0
        self.tol = 0
        self.a_at = 0
        self.a_sa = 0
        self.a_ac = 0
        self.a_pr = 0
        self.F = 0
        self.solved = False
        
    @property
    def geometric(self):
        if not self.solved:
            raise ValueError("Los parámetros geométricos no han sido calculados aún.")
        return {'d_paso':self.d_p,
                         'r_paso':self.r_p,
                         'd_base':self.d_b,
                         'r_base':self.r_b,
                         'd_raiz':self.d_r,
                         'r_raiz':self.r_r,
                         'd_cabeza':self.d_a,
                         'r_cabeza':self.r_a,
                         'a':self.a,
                         'b':self.b,
                         'p_c':self.p_c,
                         'p_b':self.p_b,
                         'p_d':self.p_d,
                         'N':self.N,
                         'm':self.m,
                         'tolerancia':self.tol,
                         'a_at':self.a_at,
                         'a_sa':self.a_sa,
                         'a_ac':self.a_ac,
                         'a_pr':self.a_pr,
                          'F':self.F}
    @property
    def geometric_imp(self):
        if not self.solved:
            raise ValueError("Los parámetros geométricos no han sido calculados aún.")
        return {'d_paso':self.d_p/25.4,
                         'r_paso':self.r_p/25.4,
                         'd_base':self.d_b/25.4,
                         'r_base':self.r_b/25.4,
                         'd_raiz':self.d_r/25.4,
                         'r_raiz':self.r_r/ 25.4,
                         'd_cabeza':self.d_a/25.4,
                         'r_cabeza':self.r_a/25.4,
                         'a':self.a/25.4,
                         'b':self.b/25.4,
                         'p_c':self.p_c /25.4,
                         'p_b':self.p_b /25.4,
                         'p_d':self.p_d * 25.4,
                         'N':self.N,
                         'm':self.m,
                         'tolerancia':self.tol/25.4,
                         'a_at':self.a_at,
                         'a_sa':self.a_sa,
                         'a_ac':self.a_ac,
                         'a_pr':self.a_pr,
                         'F':self.F/25.4}
    
    def show_geometric(self, unit='metric'):
        length = ['d_paso', 'r_paso', 'd_base', 'r_base', 'd_raiz', 'r_raiz',
                  'd_cabeza', 'r_cabeza', 'a', 'b', 'p_c', 'p_b', 'tolerancia', 'F', 'm']
        angle = ['a_pr', 'a_at', 'a_sa', 'a_ac']
        dimensionless = ['N']
        
        if unit == 'metric':
            geom = self.geometric
            for key, value in geom.items():
                print(f"{key}: {value:.4f} mm" if key in length else
                        f"{key}: {np.rad2deg(value):.4f}°" if key in angle else
                        f"{key}: {value:.4f}" if key in dimensionless else
                        f"{key}: {value*25.4:.4f} inch -1" if key == 'p_d' else
                        f"{key}: {value:.4f}")
        elif unit == 'imperial':
            geom = self.geometric_imp
            for key, value in geom.items():
                print(f"{key}: {value:.4f} in" if key in length else
                        f"{key}: {np.rad2deg(value):.4f}°" if key in angle else
                        f"{key}: {value:.4f}" if key in dimensionless else
                        f"{key}: {value/25.4:.4f} inch -1" if key == 'p_d' else
                        f"{key}: {value:.4f}")
    
    def get(self, key):
        return self.geometric.get(key, None)
    
    def solve_geometric(self, parameters:dict):
        # Extract parameters
        modulo = parameters.get('m')
        paso_diametral = parameters.get('p_d')
        dientes = parameters.get('N')
        angulo_presion = parameters.get('a_pr')
        sistema_dientes = parameters.get('sistema_dientes', 'total')
        ancho_cara = parameters.get('F')


        if modulo is None and  paso_diametral is None:
            raise ValueError("Debe proporcionar el módulo o el paso diametral.")
        if paso_diametral is not None and modulo is not None:
            raise ValueError("Proporcione solo el módulo o el paso diametral, no ambos.")
        if paso_diametral is not None:
            modulo = 25.4 / paso_diametral
            paso_diametral = paso_diametral/25.4  # Convertir a mm^-1
        elif modulo is not None:
            paso_diametral = 25.4 / modulo
            paso_diametral = paso_diametral/25.4  # Convertir a mm^-1
        
        if any(param is None for param in [dientes, angulo_presion, ancho_cara]):
            raise ValueError("Faltan parámetros necesarios para los cálculos geométricos.")
        # Set in params
        self.m = modulo
        self.p_d = paso_diametral
        self.N = dientes
        self.a_pr = np.deg2rad(angulo_presion)

        # Geometric calculations
        # Diametro de paso y radio de paso
        self.d_p = self.m * self.N
        self.r_p = self.d_p / 2
        # Diametro de base y radio de base
        self.d_b = self.m*self.N * np.cos(self.a_pr)
        self.r_b = self.d_b / 2
        # Altura de cabeza y altura de raiz
        if sistema_dientes == 'total':
            self.a = self.m
            self.b = 1.25 * self.m
        if sistema_dientes == 'parcial':
            self.a = 0.8 * self.m
            self.b = 1.0 * self.m
        # Diametro de cabeza y radio de cabeza
        self.d_a = self.d_p + 2 * self.a
        self.r_a = self.d_a / 2
        # Diametro de raiz y radio de raiz
        self.d_r = self.d_p - 2 * self.b
        self.r_r = self.d_r / 2
        # Paso circular, paso base 
        self.p_c = np.pi * self.m
        self.p_b = self.p_c * np.cos(self.a_pr)
        # Ancho de cara
        self.F = ancho_cara 
        # Tolerancia
        self.tol = self.b-self.a

    

    



engrane = Recto()
parameters = {          
    'N': 37,              # Número de dientes
    'a_pr': 20,           # Ángulo de presión en grados
    'F': 20,              # Ancho de cara en mm
    'p_d': 6,             # Paso diametral en mm^-1
}




        
            







    

