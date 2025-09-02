import numpy as np

from Engranes.Recto import Recto


class EngranajeRectoGeo:
    def __init__(self):
        # Sistema
        self.sist_dientes = None
        self.a_pr = 0
        self.Z = 0
        self.C = 0
        self.m = 0
        self.p_d = 0
        self.F = 0
        self.Ng = 0
        self.Np = 0
        # Transmision
        self.m_v = 0
        self.m_g = 0
        # Compatibilidad
        self.m_p = None
        self.interferencia = None
        self.pinion_min_N = 0
        self.desplazamiento = None
        # Elementos
        self.engrane = Recto()
        self.pinion = Recto()

        # Parametros
        self.parametros = None


    def load_geometric(self, parameters:dict):
        self.parametros = parameters
        self.type = parameters.get('type','externos')
        self.sist_dientes = parameters.get('sistema_dientes', 'total')
        self.desplazamiento = parameters.get('desplazamiento',0)

        self.F = parameters.get('F')

        self.Np = parameters.get('pinion_N')
        self.Ng = parameters.get('engrane_N')

        self.a_pr = np.deg2rad(parameters.get('a_pr'))
        modulo = parameters.get('m')
        paso_diametral = parameters.get('p_d')

        if modulo is None and  paso_diametral is None:
            print()
            print("Debe proporcionar el módulo o el paso diametral.")
        if paso_diametral is not None and modulo is not None:
            print()
            print("Proporcione solo el módulo o el paso diametral, no ambos.")
        if paso_diametral is not None:
            modulo = 25.4 / paso_diametral
            paso_diametral = paso_diametral/25.4  # Convertir a mm^-1
        elif modulo is not None:
            paso_diametral = 25.4 / modulo
            paso_diametral = paso_diametral/25.4  # Convertir a mm^-1

        self.m = modulo
        self.p_d = paso_diametral

        if self.sist_dientes == 'total':
            pinion_min_N = 4*1*(1+np.sqrt(1+3*np.sin(self.a_pr)**2))/(6*np.sin(self.a_pr)**2)
        elif self.sist_dientes == 'parcial':
            pinion_min_N = 4*0.8*(1+np.sqrt(1+3*np.sin(self.a_pr)**2))/(6*np.sin(self.a_pr)**2)
            if self.desplazamiento != 0:
                print()
                print("Desplazamiento no va con profundidad parcial")
        else:
            print()
            print("Sistema incorrecto")
            return False
        self.pinion_min_N = np.ceil(pinion_min_N)
        print()
        print(f"Minimo dientes pinion {self.pinion_min_N} y hay {self.Np}")
        print()
        print(f"Ancho de cara recomendado {8*self.m} < {16*self.m} y hay {self.F}")
        print()
        print("Finish Loading")
        return True
 
    def solve_geometric(self):
        self.engrane.solve_geometric({'N': self.Ng, 'a_pr' : self.a_pr, 'F': self.F, 'p_d': self.p_d, 
                                      'm': self.m, 'sistema_dientes' : self.sist_dientes, 'desplazamiento': -self.desplazamiento})
        self.pinion.solve_geometric({'N': self.Np, 'a_pr' : self.a_pr, 'F': self.F, 'p_d': self.p_d, 
                                     'm': self.m, 'sistema_dientes' : self.sist_dientes, 'desplazamiento': self.desplazamiento})
        
        self.m = self.engrane.get('m')
        self.C = self.engrane.get('r_paso')+self.pinion.get('r_paso')
        self.Z = (
                    np.sqrt((self.engrane.get('r_paso') + self.engrane.get('a'))**2 - (self.engrane.get('r_paso') * np.cos(self.a_pr))**2)
                    + np.sqrt((self.pinion.get('r_paso') + self.pinion.get('a'))**2 - (self.pinion.get('r_paso') * np.cos(self.a_pr))**2)
                    - self.C * np.sin(self.a_pr))
        
        self.set_radio_curvatura()
        self.set_angs_engrane()
        self.set_angs_pinion()
        self.check_compatibility()

        self.m_v = self.pinion.get('N')/self.engrane.get('N')
        self.m_g = self.engrane.get('N')/self.pinion.get('N')
        

    def set_radio_curvatura(self):
        rho_pinion = np.sqrt((self.pinion.get('r_paso')+self.m*(1+self.pinion.xp))**2-(self.pinion.get('r_base'))**2)-np.pi*self.m*np.cos(self.a_pr)
        self.pinion.r_curvatura = rho_pinion
        if self.type == 'externos':
            rho_engrane = self.C*np.sin(self.a_pr)-rho_pinion
        elif self.type == 'internos':
            rho_engrane = self.C*np.sin(self.a_pr)+rho_pinion
        self.engrane.r_curvatura = rho_engrane

    def set_angs_pinion(self):
        gamma = np.atan((np.sqrt((self.engrane.get('r_paso') + self.engrane.get('a'))**2 - (self.engrane.get('r_paso') * np.cos(self.a_pr))**2)-self.C*np.sin(self.a_pr))
                        /(self.pinion.get('r_paso')*np.cos(self.a_pr)))
        a_at = gamma+self.a_pr
        a_sa = np.asin((self.engrane.get('r_paso')*np.sin(self.a_pr)
                - np.sqrt((self.engrane.get('r_paso') + self.engrane.get('a'))**2 - (self.engrane.get('r_paso') * np.cos(self.a_pr))**2) + self.Z)
                /((self.pinion.get('r_paso')+self.pinion.get('a'))*np.cos(self.a_pr)))
        a_ac = a_at+a_sa
        self.pinion.set_angs(a_at,a_sa,a_ac)
    
    def set_angs_engrane(self):
        a_at = np.asin((np.sqrt((self.engrane.get('r_paso') + self.engrane.get('a'))**2 - (self.engrane.get('r_paso') * np.cos(self.a_pr))**2)
                        -self.engrane.get('r_paso')*np.sin(self.a_pr))
                        /((self.engrane.get('r_paso')+self.engrane.get('a'))*np.cos(self.a_pr)))
        
        gamma = np.atan((np.sqrt((self.engrane.get('r_paso') + self.engrane.get('a'))**2 - (self.engrane.get('r_paso') * np.cos(self.a_pr))**2) - self.Z)
                        /(self.engrane.get('r_paso')*np.cos(self.a_pr)))
        a_sa = self.a_pr-gamma
        a_ac = a_at+a_sa
        self.engrane.set_angs(a_at,a_sa,a_ac)

    def check_compatibility(self):
        # Interferencia
        criterio_1 = self.engrane.get('r_base')-self.engrane.get('r_raiz') < 0.25*self.engrane.get('a')
        if not criterio_1:
            print()
            print("Criterio 1, no se cumple r_b - r_raiz < 0.25*a para engrane")
            print(self.engrane.get('r_base')-self.engrane.get('r_raiz') ,  0.25*self.engrane.get('a'))
        criterio_2 = self.pinion.get('r_base')-self.pinion.get('r_raiz') < 0.25*self.pinion.get('a')
        if not criterio_2:
            print()
            print("Criterio 2, no se cumple r_b - r_raiz < 0.25*a para pinion")
            print(self.pinion.get('r_base')-self.pinion.get('r_raiz'), 0.25*self.pinion.get('a'))
        criterio_3 = self.pinion.get('r_base')-self.pinion.get('r_raiz') < self.pinion.get('b')-self.engrane.get('a')
        if not criterio_3:
            print()
            print("Criterio 3, no se cumple r_b-p - r_raiz-p < b-p - a_g")
            print(self.pinion.get('r_base')-self.pinion.get('r_raiz'), self.pinion.get('b')-self.engrane.get('a'))
        if not all([criterio_1,criterio_2,criterio_3]):
            self.interferencia = True
        
        self.m_p = self.Z/(np.pi*self.m)
        if self.m_p <= 1.4 or self.m_p >= 2.0:
            print(f"Razón de contacto requiere revision 1.4 < {self.m_p} < 2.0")     
            
    def show_geo(self):
        print()
        print("===== Resumen del Sistema =====")

        print(f"Sistema:\n"
            f"  - Número de dientes: Piñón {self.pinion.get('N')} | Engrane {self.engrane.get('N')}\n"
            f"  - Ángulo de presión (a_pr): {np.rad2deg(self.a_pr)}°\n"
            f"  - Z: {self.Z}\n"
            f"  - C: {self.C}\n"
            f"  - Módulo (m): {self.m}")

        print(f"Transmisión:\n"
            f"  - m_v: {self.m_v}\n"
            f"  - m_a: {self.m_g}")

        print(f"Compatibilidad:\n"
            f"  - Razón de contacto (m_p): {self.m_p}\n"
            f"  - Interferencia: {self.interferencia}\n"
            f"  - Piñón mínimo (N): {self.pinion_min_N}")

        print("=" * 30)
        print("===== Geometría del Engrane =====")
        self.engrane.show_geometric()

        print("=" * 30)
        print("===== Geometría del Piñón =====")
        self.pinion.show_geometric()





    