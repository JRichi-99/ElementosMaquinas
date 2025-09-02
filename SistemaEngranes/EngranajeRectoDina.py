import numpy as np

from EngranajeRectoGeo import EngranajeRectoGeo

class EngranajeRectoDina(EngranajeRectoGeo):
    def __init__(self):
        super().__init__()
        
    def solve_dinamics(self, resistance, tension):
        # Obtener parámetros del diccionario
        pinion_tension    = tension.get("pinion_tension")
        pinion_resistance = resistance.get("pinion_resistance")
        engrane_tension   = tension.get("engrane_tension")
        engrane_resistance= resistance.get("engrane_resistance")

        # Calcular dinámicas y esfuerzos para piñón y engrane
        # Agregar I
        if pinion_tension['I'] is None and engrane_tension['I'] is None:
            if self.type == 'externos':
                pinion_tension["I"]  = np.cos(self.a_pr)/(1/self.pinion.r_curvatura + 1/self.engrane.r_curvatura)/self.pinion.get('d_paso')/1
                engrane_tension["I"] = np.cos(self.a_pr)/(1/self.pinion.r_curvatura + 1/self.engrane.r_curvatura)/self.engrane.get('d_paso')/1

            elif self.type == 'internos':
                pinion_tension["I"]  = np.cos(self.a_pr)/(1/self.pinion.r_curvatura - 1/self.engrane.r_curvatura)/self.pinion.get('d_paso')/1
                engrane_tension["I"] = np.cos(self.a_pr)/(1/self.pinion.r_curvatura - 1/self.engrane.r_curvatura)/self.engrane.get('d_paso')/1
        
        self.pinion.calc_dina(pinion_tension, pinion_resistance)
        self.engrane.calc_dina(engrane_tension, engrane_resistance)

    def show_dina(self):
        print("===== Resumen del Pinion =====")
        print()
        self.pinion.show()
        print()
        print("===== Resumen del Engranaje =====")
        self.engrane.show()

    def load_dinamics(self,params):
        H     = params.get("H")
        W     = params.get("W")
        T     = params.get("T")
        where = params.get("where")
        units = params.get("units")

        known = sum(v is not None for v in [H,W,T])
        if known < 2:
            print("Debe especificar al menos 2 variables conocidas (H, W, T o where).")
            return
        H,W,T = self.fix_dinamics(H,W,T,units)
        
        if where.lower() == 'pinion':
            self.pinion.T = T
            self.pinion.w = W
            self.engrane.T = self.m_g*T
            self.engrane.w = self.m_v*W
        elif where.lower() == 'engrane':
            self.engrane.T = T
            self.engrane.w = W
            self.pinion.T = T/self.m_g
            self.pinion.w = W/self.m_v
        
        self.pinion.Vt = self.pinion.w*self.pinion.r_p/1000
        self.engrane.Vt = self.engrane.w*self.engrane.r_p/1000

    def fix_dinamics(self, H, W, T, units='metric'):
        # lista de variable
        if units == 'imp':
            # convertir torque a N·m
            T = T * 1.3558 if T is not None else T
            # convertir W (RPM → rad/s)
            W = W * (2*np.pi/60) if W is not None else W
            # convertir H (HP → W)
            H = H * 745.7 if H is not None else H

        # Caso: potencia y torque conocidos → calcular W
        if H is not None and T is not None and W is None:
            W = H / T

        # Caso: potencia y velocidad conocidos → calcular T
        elif H is not None and W is not None and T is None:
            T = H / W

        # Caso: torque y velocidad conocidos → calcular H
        elif T is not None and W is not None and H is None:
            H = T * W

        return H,W,T


   

        

        

