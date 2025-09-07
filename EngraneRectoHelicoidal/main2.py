from Tren import TrenEngrane
from PER import ParEngranesResistencia as PER


Tren = TrenEngrane()

ParEngranes0=PER()
ParEngranes0.set_par(m=2.5, 
                    phi_n=20,
                    psi=22,
                    N_pinion=30,
                    N_engrane=60,
                    F_pinion=30,
                    F_engrane=30,
                    sistema_dientes='total',
                    acople='externos',
                    xp=0.0)

ParEngranes0.resumen_geometria()
ParEngranes0.resumen_compatibilidad()

ParEngranes1=PER()
ParEngranes1.set_par(m=2.5, 
                    phi_n=20,
                    psi=22,
                    N_pinion=30,
                    N_engrane=60,
                    F_pinion=30,
                    F_engrane=30,
                    sistema_dientes='total',
                    acople='externos',
                    xp=0.0)

ParEngranes2=PER()
ParEngranes2.set_par(m=2.5, 
                    phi_n=20,
                    psi=22,
                    N_pinion=30,
                    N_engrane=60,
                    F_pinion=30,
                    F_engrane=30,
                    sistema_dientes='total',
                    acople='externos',
                    xp=0.0)

ParEngranes1.resumen_geometria()
ParEngranes1.resumen_compatibilidad()

ParEngranes = [ParEngranes0,ParEngranes1, ParEngranes2]

for par in ParEngranes:
    Tren.add_pair(par)

Tren.connect(0,1,"engrane","pinion")
Tren.connect(1,2,"engrane","pinion")
Tren.solve_transmision(start_id=0, 
                       where="engrane",
                       H=2900,
                       H_units='si', 
                       Omega=200, 
                       Omega_units='rpm', 
                       T=None, 
                       T_units='si')

ParEngranes0.resumen_transmision()
ParEngranes1.resumen_transmision()
ParEngranes2.resumen_transmision()
Tren.resumen_transmision()


