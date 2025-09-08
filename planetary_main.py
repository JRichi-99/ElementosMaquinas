from ERH.elements.Planetary import Planetary
from ERH.params.planetary_params import tension_planeta_corona,tension_sol_planeta,resistance_planeta_corona,resistance_sol_planeta
from ERH.eq.conversion import *

EngranePlanetario=Planetary()

#(n_c - n_pp) / (n_pp - n_s) = N_s / N_c       #Relacion de velocidades
# (n_p - n_pp) / (n_pp - n_s) = N_s / N_p
# N_c = N_s + 2*N_p

EngranePlanetario.create_planetary_sistem(m=1,phi_n=20,F=5,N_c=96,N_s=24,N_p=36,ctd_planetas=3)

EngranePlanetario.get_np_from(npp=200,ns=1000)
H = 150
EngranePlanetario.set_load_corona(w=rpm_a_rad_s(0),h=H,t=None)
EngranePlanetario.set_load_planeta(w=rpm_a_rad_s(333.333),h=H,t=None)
EngranePlanetario.set_load_sol(w=rpm_a_rad_s(1000),h=H,t=None)

EngranePlanetario.set_Wt()
EngranePlanetario.set_ciclos(horas=24,dias=365,years=1)

EngranePlanetario.calc_esfuerzos(tension_sol_planeta, tension_planeta_corona)

EngranePlanetario.calc_resistencia(resistance_sol_planeta,resistance_planeta_corona)

