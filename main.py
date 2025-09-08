from ERH.elements.Tren import TrenEngrane
from ERH.elements.PER import ParEngranesResistencia as PER
from ERH.params.geo_params import geo0_params,geo1_params,geo2_params
from ERH.params.trans_params import trans_params
from ERH.params.tension_params import tension_params0,tension_params1,tension_params2
from ERH.params.resist_params import resistance_params0,resistance_params1,resistance_params2
from ERH.elements.flux import run_par_pipeline

"""geometria','transmision','esfuerzos','resistencia"""
Tren = TrenEngrane()

ParEngranes0=PER()
ParEngranes1=PER()
ParEngranes2=PER()
#ParEngranes = [ParEngranes0,ParEngranes1]

ParEngranes = [ParEngranes0,ParEngranes1, ParEngranes2]

run_par_pipeline(ParEngranes0, geo0_params, tension_params0, resistance_params0, "g")
run_par_pipeline(ParEngranes1, geo1_params, tension_params1, resistance_params1, "g")
run_par_pipeline(ParEngranes2, geo2_params, tension_params2, resistance_params2, "g")

for par in ParEngranes:
    Tren.add_pair(par)

Tren.connect(0,1,"engrane","pinion")
Tren.connect(1,2,"engrane", "pinion")
Tren.solve_transmision(**trans_params)
Tren.resumen_transmision()

for par in ParEngranes:
    par.print_ciclos(24,365,10)

run_par_pipeline(ParEngranes0, geo0_params, tension_params0, resistance_params0, "r")
run_par_pipeline(ParEngranes1, geo1_params, tension_params1, resistance_params1, "r")
run_par_pipeline(ParEngranes2, geo2_params, tension_params2, resistance_params2, "r")





