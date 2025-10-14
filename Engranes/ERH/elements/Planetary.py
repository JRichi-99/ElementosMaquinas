from .PER import ParEngranesResistencia as PER
import numpy as np

class Planetary:
    def __init__(self):
        self.ctd_planetas = None
        self.sol_planeta = PER()
        self.planeta_corona = PER()
        self.w_pp = None
        self.w_p = None
        self.w_s = None
        self.w_c = None
    
    def get_np_from(self,npp,ns):
        Ns = self.sol_planeta.pinion.N
        Np = self.sol_planeta.engrane.N
        my_np = Ns/Np*(npp-ns)+npp
        print(f"Resultado para la velocidad angular del planeta {my_np:.2f}")
        print()

    def calc_esfuerzos(self, sol_planeta, planeta_corona):
        self.sol_planeta.tension_params(sol_planeta)
        self.sol_planeta.calc_esfuerzos()
        self.sol_planeta.resumen_esfuerzos(name="1")
        #self.planeta_corona.tension_params(planeta_corona)
        #self.planeta_corona.calc_esfuerzos(engrane=False)
        #self.planeta_corona.resumen_esfuerzos()
        
    def calc_resistencia(self, sol_planeta, planeta_corona):
        self.sol_planeta.resistance_params(sol_planeta)
        self.sol_planeta.calc_resistencia()
        self.sol_planeta.resumen_resistencia(name="1")
        #self.planeta_corona.resistance_params(planeta_corona)
        #self.planeta_corona.calc_resistencia(engrane=False)
        #self.planeta_corona.resumen_resistencia()


    def create_planetary_sistem(self, ctd_planetas, phi_n, N_s, N_p, N_c, F, m=None, pi_n=None, psi= 0.0):

        self.ctd_planetas = ctd_planetas
        self.sol_planeta.set_par(m=m, 
                                 pi_n=pi_n, 
                                 phi_n=phi_n,
                                   psi=psi,
                                   N_pinion=N_s,
                                   N_engrane=N_p,
                                   F_engrane=F, 
                                   F_pinion=F)

        self.planeta_corona.set_par(m=m, 
                                 pi_n=pi_n, 
                                 phi_n=phi_n,
                                   psi=psi,
                                   N_pinion=N_p,
                                   N_engrane=N_c,
                                   F_engrane=F, 
                                   F_pinion=F, acople="internos")
        
        self.sol_planeta.resumen_geometria(name="1")
        self.sol_planeta.resumen_compatibilidad(name="1")
        self.planeta_corona.resumen_geometria(name="1")
        self.planeta_corona.resumen_compatibilidad(name="1")

    def set_load_sol(self, w=None,h=None,t=None):
        w,h,t = self.get_load(w,h,t)
        self.sol_planeta.pinion.set_load(T=t,H=h,Omega=w)
        self.w_s = w

        
    def set_load_planeta(self,w=None,h=None,t=None):
        w,h,t = self.get_load(w,h,t)
        self.sol_planeta.engrane.set_load(T=t,H=h,Omega=w)

        self.planeta_corona.pinion.set_load(T=t,H=h,Omega=w)

        self.w_p = w
    
    def set_load_corona(self,w=None,h=None,t=None):
        w,h,t = self.get_load(w,h,t)
        self.planeta_corona.engrane.set_load(T=t,H=h,Omega=w)
        self.w_c = w
    
    def set_Wt(self):
        Wt = self.sol_planeta.pinion.Wt/self.ctd_planetas
        print(f"Esfuerzo del sol tangencial {self.sol_planeta.pinion.Wt}")
        print(f"Esfuerzo percibido por los elementos {Wt:.2f}")
        print()
        self.sol_planeta.pinion.Wt=Wt
        self.sol_planeta.engrane.Wt=Wt
        self.planeta_corona.pinion.Wt=Wt
        self.planeta_corona.engrane.Wt=Wt

    def set_ciclos(self, horas, dias, years):
        Ns = self.sol_planeta.pinion.N
        Np = self.sol_planeta.engrane.N
        self.w_pp = (self.w_p + Ns/Np * self.w_s) / (1 + Ns/Np)
        self.print_ciclos(horas, dias, years)

    def print_ciclos(self, horas, dias, years):
        # segundos totales de operación
        segundos = horas * dias * years * 3600

        # ciclos relativos al portador
        ciclos_sol = ((self.w_s - self.w_pp) / (2*np.pi)) * segundos
        ciclos_planeta = ((self.w_p - self.w_pp) / (2*np.pi)) * segundos
        ciclos_corona = ((self.w_c - self.w_pp) / (2*np.pi)) * segundos

        # impresión en notación científica (orden de magnitud)
        print("=== Ciclos acumulados ===")
        print(f"Sol     : {ciclos_sol:.2e} ciclos, para calculo {self.ctd_planetas*ciclos_sol:.2e} ")
        print(f"Planeta : {ciclos_planeta:.2e} ciclos, para calculo {ciclos_planeta:.2e}")
        print(f"Corona  : {ciclos_corona:.2e} ciclos, para calculo {self.ctd_planetas*ciclos_corona:.2e}" )
        print()



    #(n_c - n_pp) / (n_pp - n_s) = N_s / N_c       #Relacion de velocidades
    # (n_p - n_pp) / (n_pp - n_s) = N_s / N_p
    # N_c = N_s + 2*N_p

    # Luego, Wt_planeta = sol 

    def get_load(self, w=None,h=None,t=None):
        if h is None:
            h = t*w
        if t is None:
            t = h/w if w != 0.0 else 0
        if w is None:
            w = h/t
        return w,h,t






        
        