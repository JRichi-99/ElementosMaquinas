from EE import EngranajeEsfuerzo as EE

class EngranajeResistencia(EE):
    def __init__(self):
        super().__init__()
        self.safe_c = None
        self.safe_f = None
        self.factor_c = None
        self.factor_f = None
        self.HB = None


    def calc_resistance(self, K_L, K_T, K_R, C_L, C_H, pSF, pSFC):
        self.safe_f = pSF*K_L/K_T/K_R

        self.safe_c = pSFC*C_L*C_H/K_T/K_R
        
        self.factor_c = (self.safe_c/self.sigma_c)**2
        self.factor_f = self.safe_f/self.sigma_f
    

    
    
    
