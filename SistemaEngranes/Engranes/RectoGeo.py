import numpy as np


class RectoGeo():
    def __init__(self):
        # Geometria
        self.sist_dientes = None
        self.d_p = None
        self.r_p = None
        self.d_b = None
        self.r_b = None
        self.d_r = None
        self.r_r = None
        self.d_a = None
        self.r_a = None
        self.a = None
        self.b = None
        self.p_c = None
        self.p_b = None
        self.p_d = None
        self.N = None
        self.m = None
        self.tol = None
        self.a_at = None
        self.a_sa = None
        self.a_ac = None
        self.a_pr = None
        self.F = None
        self.m_p = None
        self.ht = None
        self.holgura_minima = None
        self.xp = None
        self.r_curvatura = None
        
    @property
    def geometric(self):
        return {
                'sistema dientes': self.sist_dientes,
                'd_paso': self.d_p,
                'r_paso': self.r_p,
                'd_base': self.d_b,
                'r_base': self.r_b,
                'd_raiz': self.d_r,
                'r_raiz': self.r_r,
                'd_cabeza': self.d_a,
                'r_cabeza': self.r_a,
                'a': self.a,
                'b': self.b,
                'p_c': self.p_c,
                'p_b': self.p_b,
                'p_d': self.p_d,
                'N': self.N,
                'm': self.m,
                'tolerancia': self.tol,
                'a_at': self.a_at,
                'a_sa': self.a_sa,
                'a_ac': self.a_ac,
                'a_pr': self.a_pr,
                'F': self.F,
                'm_p': self.m_p,
                'ht': self.ht,
                'holgura_minima': self.holgura_minima,
                'xp': self.xp,
                'r_curvatura': self.r_curvatura
            }
    @property
    def geometric_imp(self):
        return {        'sistema dientes': self.sist_dientes,
                        'd_paso':self.d_p/25.4,
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
                        'F':self.F/25.4,
                        'ht': self.ht / 25.4 ,
                        'holgura_minima': self.holgura_minima / 25.4 ,
                        'xp': self.xp ,
                        'r_curvatura': self.r_curvatura / 25.4}
    
    def get(self, key):
        return self.geometric.get(key, None)
    
    def solve_geometric(self, parameters:dict):
        # Extract parameters
        modulo = parameters.get('m')
        paso_diametral = parameters.get('p_d')
        dientes = parameters.get('N')
        angulo_presion = parameters.get('a_pr')
        sistema_dientes = parameters.get('sistema_dientes')
        ancho_cara = parameters.get('F')
        self.xp = parameters.get('desplazamiento')

        if any(param is None for param in [dientes, angulo_presion, ancho_cara]):
            print("Faltan parámetros necesarios para los cálculos geométricos.")
        
        if sistema_dientes == 'total':
            if paso_diametral*25.4 < 20:
                paso = 'grueso'
            else:
                paso = 'fino'
                if angulo_presion != 20:
                    print("El angulo de presión debe ser 20 para paso fino")

        # Set in params
        self.m = modulo
        self.p_d = paso_diametral
        self.N = dientes
        self.a_pr = angulo_presion
        self.sist_dientes = sistema_dientes

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
            self.a += self.a*self.xp
            self.b = 1.25 * self.m
        if sistema_dientes == 'parcial':
            self.a = 0.8 * self.m
            self.b = 1.0 * self.m
        self.ht = self.a+self.b
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
        if sistema_dientes == 'total':
            if paso == 'grueso':
                self.holgura_minima = 0.25 / self.p_d
              
            elif paso == 'fino':
                self.holgura_minima = 0.2 / self.p_d +0.002*25.4

            if self.tol < self.holgura_minima: 
                print()
                print("Tolerancia menor que holgura minima")
        else:
            print()
            print("Buscar Holgura minima para diente parcial")
            self.holgura_minima = -1
    
    def set_angs(self, a_at, a_sa, a_ac):
        self.a_ac = a_ac
        self.a_at = a_at
        self.a_sa = a_sa

    def show_geometric(self, unit='metric'):
        length = ['d_paso', 'r_paso', 'd_base', 'r_base', 'd_raiz', 'r_raiz',
                  'd_cabeza', 'r_cabeza', 'a', 'b', 'p_c', 'p_b', 'tolerancia', 'F', 'm', 'ht', 'holgura_minima', 'r_curvatura']
        angle = ['a_pr', 'a_at', 'a_sa', 'a_ac']
        dimensionless = ['N', 'xp', 'mp']
        
        if unit == 'metric':
            geom = self.geometric
            for key, value in geom.items():
                print(f"{key}: {value:.4f} mm" if key in length else
                        f"{key}: {np.rad2deg(value):.4f}°" if key in angle else
                        f"{key}: {value:.4f}" if key in dimensionless else
                        f"{key}: {value*25.4:.4f} inch -1" if key == 'p_d' else
                        f"{key}: {value}")
        elif unit == 'imperial':
            geom = self.geometric_imp
            for key, value in geom.items():
                print(f"{key}: {value:.4f} in" if key in length else
                        f"{key}: {np.rad2deg(value):.4f}°" if key in angle else
                        f"{key}: {value:.4f}" if key in dimensionless else
                        f"{key}: {value/25.4:.4f} inch -1" if key == 'p_d' else
                        f"{key}: {value}")
    

    


        
            







    

