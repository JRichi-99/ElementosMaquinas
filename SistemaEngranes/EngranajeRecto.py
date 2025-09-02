from EngranajeRectoDina import EngranajeRectoDina
from Params.Params import params as mp

class EngranajeRecto(EngranajeRectoDina):
    def __init__(self):
        super().__init__()

    def solve(self, params:dict):
        self.load_geometric(params.get('geometric'))
        self.solve_geometric()
        self.show_geo() 
        input()
        self.load_dinamics(params.get('dinamics'))
        self.solve_dinamics(resistance=params.get('resistance_params'), tension=params.get('tension_params'))
        self.show_dina()


MyEngranaje =EngranajeRecto()
MyEngranaje.solve(params=mp)









