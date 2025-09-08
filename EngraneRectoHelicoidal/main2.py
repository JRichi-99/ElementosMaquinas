from Tren import TrenEngrane
from PER import ParEngranesResistencia as PER
from Params.geo_params import *
from Params.trans_params import *
from Params.tension_params import *
from Params.resist_params import *
from flux import run_par_pipeline

"""geometria','transmision','esfuerzos','resistencia"""
Tren = TrenEngrane()

ParEngranes0=PER()
ParEngranes1=PER()
ParEngranes = [ParEngranes0,ParEngranes1]

run_par_pipeline(ParEngranes0, geo0_params, tension_params0, resistance_params0, "geometria")
run_par_pipeline(ParEngranes1, geo1_params, tension_params1, resistance_params1, "geometria")

for par in ParEngranes:
    Tren.add_pair(par)

Tren.connect(0,1,"engrane","pinion")
Tren.solve_transmision(**trans_params)
Tren.resumen_transmision()


run_par_pipeline(ParEngranes0, geo0_params, tension_params0, resistance_params0, "resistencia")
run_par_pipeline(ParEngranes1, geo1_params, tension_params1, resistance_params1, "resistencia")





