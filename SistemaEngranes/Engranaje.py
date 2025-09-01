from Engranes import Recto, Helicoidal, Engrane

class EngranajeRecto:
    def __init__(self, **kwargs):
        self.Z = 0
        self.C = 0
        self.m_p =0
        self.m_v = 0
        self.m_a = 0
        self.m = 0
        self.p_d = 0
        self.sistema = None
        self.interferencia = 0
        self.tolerancia_minima = 0
        self.pinion_min_N = 0
        self.engrane = Recto()
        self.engrane_params = ['N','a_pr', 'F', 'p_d']
        self.pinion = Recto()

    
    def engrane_geometric(self):
        self.engrane.solve_geometric()
        
parameters = {          
    'N': 37,              # Número de dientes
    'a_pr': 20,           # Ángulo de presión en grados
    'F': 20,              # Ancho de cara en mm
    'p_d': 6,             # Paso diametral en mm^-1
}
    