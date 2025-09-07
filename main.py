from PER import ParEngranesResistencia

ParEngranes=ParEngranesResistencia()
ParEngranes.set_par(m=2.5, 
                    phi_n=20,
                    psi=22,
                    N_pinion=30,
                    N_engrane=60,
                    F_pinion=30,
                    F_engrane=30,
                    sistema_dientes='total',
                    acople='externos',
                    xp=0.0)

ParEngranes.resumen_geometria()
ParEngranes.resumen_compatibilidad()
ParEngranes.set_first_load(
    where="pinion",         # "pinion" o "engrane"
    H=2900, H_units="si",   # H puede ser HP o si(watts)
    Omega=200, Omega_units="rpm" # omega puede ser rpm o si
)



tension_params = {
    "K_A": 1.25,
    "K_M": 1.5,
    "K_S": 1.00,
    "K_B": 1.05,
    "K_I": 1.00,
    "K_V": None,

    "Jp_pin": 0.53,
    "Jmod_pin": 0.96,
    "Jp_eng": 0.59,
    "Jmod_eng": 0.98,

    "C_p": 191.0,   # √MPa
    "C_F": 1.00,
    "Q_v": 5,

    "I": None,
    "Jp": None,     # (opcional) J efectivo pinión si quieres forzar
    "Jg": None,     # (opcional) J efectivo engrane si quieres forzar
}

ParEngranes.tension_params(tension_params)
ParEngranes.calc_esfuerzos()
ParEngranes.resumen_esfuerzos()

resistance_params = {
    "K_L_p": 1.18,
    "C_L_p": 1,
    "HB_p": 400,

    "K_L_g": 1.25,
    "C_L_g": 1.1,
    "HB_g":240,

    "temperatura": 80.0,    # °C
    "R": 0.99,              # confiabilidad objetivo (0–1)

    "caso_engrane": "masa",  # "masa" | "superficie"
    "Rq": 0.8,              # µm

    "pSF_g": 280.0,  # MPa (contacto engrane permisible)
    "pSFC_g": 790.0,       # MPa (flexión engrane permisible)
    "pSF_p": 390.0,         # MPa (flexión piñón permisible)           
    "pSFC_p": 1200.0,      # MPa (contacto piñón permisible)

    "K_T": None,
    "K_R": None,
    "C_H_g": None     # si no lo conoces aún, puedes dejar None
}


ParEngranes.resistance_params(resistance_params)
ParEngranes.calc_resistencia()
ParEngranes.resumen_resistencia()


