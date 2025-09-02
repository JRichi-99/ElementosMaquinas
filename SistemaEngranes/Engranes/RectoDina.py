import numpy as np
from Engranes.RectoGeo import RectoGeo

class RectoDina(RectoGeo):
    def __init__(self):
        super().__init__()

        # Dinamica
        self.T = None
        self.w = None
        self.Vt = None

        # Fuerzas
        self.Wt = None
        self.Wr = None
        self.Wres = None

        # Esfuerzos
        self.sigma = None
        self.sigma_c = None
        self.c_esfuerzos = {}

        # Resistencia
        self.Sf = None
        self.Sfc = None
        self.c_resist = None

        # Seguridad
        self.nFc = 0
        self.nF = 0

    def calc_dina(self, params_esfuerzo, params_resist):
        self.c_esfuerzos = params_esfuerzo
        self.c_resist = params_resist
        self.calc_fuerzas()
        self.get_constants()
        self.calc_esfuerzos()
        self.calc_resistencia()
        self.calc_seguridad()

    def calc_fuerzas(self):
        self.Wt = 2*self.T/(self.m*self.N)*1000
        self.Wr = self.Wt*np.tan(self.a_pr)
        self.Wres = self.Wt/(np.cos(self.a_pr))

    def calc_esfuerzos(self):
        self.sigma = (self.Wt*self.c_esfuerzos['K_a']*self.c_esfuerzos['K_m']*self.c_esfuerzos['K_s']*self.c_esfuerzos['K_B']*self.c_esfuerzos['K_I']
                      /(self.F*self.m*self.c_esfuerzos['J']*self.c_esfuerzos['K_v']))
        
        self.sigma_c = self.c_esfuerzos['C_p']*np.sqrt(self.Wt*self.c_esfuerzos['K_a']*self.c_esfuerzos['K_m']*self.c_esfuerzos['K_s']*self.c_esfuerzos['C_f']
                      /(self.F*self.d_p*self.c_esfuerzos['I']*self.c_esfuerzos['K_v']))

    def calc_resistencia(self):
        self.Sf = self.c_resist['Sf']*self.c_resist['K_L']/(self.c_resist['K_R']*self.c_resist['K_T'])
        self.Sfc = self.c_resist['Sfc']*self.c_resist['C_L']*self.c_resist['C_H']/(self.c_resist['K_R']*self.c_resist['K_T'])
    
    def calc_seguridad(self):
        self.nFc = (self.Sfc/self.sigma_c)**2
        self.nF = self.Sf/self.sigma

    def get_constants(self):
        if self.c_esfuerzos.get('K_v') is None:
            Q_v = self.c_esfuerzos.get('Q_v')
            if 6<=Q_v and Q_v<=12:
                B = 0.25*(12-Q_v)**(2/3)
            elif Q_v<6:
                B = 1
            else:
                print("Error con valor de Q_v")
            A = 50+56*(1-B)
            self.c_esfuerzos['K_v'] = (A/(A+np.sqrt(200*self.Vt)))**B

        if self.c_esfuerzos.get('K_B') is None:
            tr = self.c_esfuerzos.get('tr')
            mb = tr/self.ht
            K_B = None
            if 0.5<=mb and mb<=1.2:
                K_B = -2*mb+3.4
            elif mb > 1.2:
                K_B = 1.0
            else:
                print("El aro es demasiado delgado")
            self.c_esfuerzos['K_B'] = K_B

        if self.c_resist.get('K_T') is None:
            T = self.c_resist.get('Tf')
            if T <= 110:
                self.c_resist['K_T'] = 1
            else:
                self.c_resist['K_T'] = (220+T)/330

        if self.c_resist.get('K_R') is None:
            R = self.c_resist.get('R')
            if 0.9<=R and R <=0.99:
                self.c_resist['K_R'] = 0.7-0.15*np.log10(1-R)
            else:
                self.c_resist['K_R'] = 0.5-0.25*np.log10(1-R)
        
        if self.c_resist.get('C_H') is None:
            caso = self.c_resist['caso']
            if caso == 'pinion':
                self.c_resist['C_H'] = 1
                
            HBp = self.c_resist.get('HBp')
            HBg = self.c_resist.get('HBg')
            r1 = HBp / HBg
            if r1 <= 1.2:
                A2 = 0.0
            elif r1 <= 1.7:
                A2 = 8.98e-3 * r1 - 8.29e-3
            else:  # r > 1.7
                A2 = 6.98e-3
            if caso =='engrane,masa':
                self.c_resist['C_H'] = 1+A2*(self.c_resist.get('m_g')-1)
            if caso =='Engrane,sup':
                B2 = 0.75e-3*np.exp(-0.0112*self.c_resist.get('R_q'))
                self.c_resist['C_H'] = 1+B2*(450-HBg)

    def show(self):

        # Dinámica
        print("Dinámica:")
        print(f"  - Torque (T): {self.T}")
        print(f"  - Velocidad angular (w): {self.w}")
        print(f"  - Velocidad tangencial (Vt): {self.Vt}")

        # Fuerzas
        print("\nFuerzas:")
        print(f"  - Fuerza tangencial (Wt): {self.Wt}")
        print(f"  - Fuerza radial (Wr): {self.Wr}")
        print(f"  - Fuerza resultante (Wres): {self.Wres}")

        # Esfuerzos
        print("\nEsfuerzos:")
        print(f"  - Esfuerzo por flexión (σ): {self.sigma}")
        print(f"  - Esfuerzo por contacto (σc): {self.sigma_c}")
        print(f"  - Coeficiente de esfuerzos: {self.c_esfuerzos}")

        # Resistencia
        print("\nResistencia:")
        print(f"  - Resistencia a flexión (Sf): {self.Sf}")
        print(f"  - Resistencia a contacto (Sfc): {self.Sfc}")
        print(f"  - Coeficiente de resistencia: {self.c_resist}")

        # Seguridad
        print("\nSeguridad:")
        print(f"  - Factor de seguridad a contacto (nFc): {self.nFc}")
        print(f"  - Factor de seguridad a flexión (nF): {self.nF}")
                


        

