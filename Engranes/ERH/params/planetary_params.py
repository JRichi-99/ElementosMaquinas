
K_A = 1                               # PAG 32 TABLA 17
K_B = 1                               # PAG 32 ABAJO TABLA 17
K_M = 1.6                               # PAG 32 TABLA 18
K_S = 1                               # PAG 33 TABLA 20
C_F = 1                               #  PAG 31 GENERALMENTE 1 NORMAL, O MAYOR QUE 1 SI ES ASPERO
Q_v = 10
C_p = 229.06                             # PAG 31 TABLA 15
I = 0.07

# resistencia
Temp = 20
R = 0.99




tension_sol_planeta = {
    "K_A": K_A, # PAG 32 TABLA 17
    "K_M": K_M, # PAG 32 TABLA 18
    "K_S": K_S, # PAG 33 TABLA 20
    "K_B": K_B, # PAG 32 ABAJO TABLA 17
    "K_V": None,  # CALCULA

    "K_I_pin": 1.00,   # 1 SI ES EXTERNO 1.4 SI ES INTERMEDIO
    "K_I_eng": 1.42,   

    "Jp_pin": 0.35,       # PAG 35 GRAFICO 27 PARA RECTO 28 HELI
    "Jmod_pin": 1,     # 1 SI ES RECTO PAG 36 GRAFICO 29
    "Jp_eng": 0.38,
    "Jmod_eng": 1,

    "C_p": C_p,   # √MPa       # PAG 31 TABLA 15
    "C_F": C_F,                  #  PAG 31 GENERALMENTE 1 NORMAL, O MAYOR QUE 1 SI ES ASPERO
    "Q_v": Q_v,         # DATO

    "I": I,      # CALCULA
    "Jp": None,     # (opcional) J efectivo pinión si quieres forzar # elegir el mas pequeño 
    "Jg": None,     # (opcional) J efectivo engrane si quieres forzar
}

resistance_sol_planeta = {
    "K_L_p": 0.85, # PAGINA 27 D.6 # PAGINA 28 TABLA 10 # depende de los ciclos
    "C_L_p": 0.75, # PAGINA 27 D.6 
    "HB_p": 235, # PAGINA 30

    "K_L_g": 0.91, # PAGINA 27 D.6 
    "C_L_g": 0.85, # PAGINA 27 D.6 
    "HB_g":235, # PAGINA 30 Tabla 12

    "temperatura": Temp,    # °C
    "R": R,              # confiabilidad objetivo (0–1)

    "caso_engrane": "masa",  # "masa" | "superficie"
    "Rq": 0.8,              # µm

    "pSF_g":  210.26,  # MPa (contacto engrane permisible)          Tabla 12 Pagina 30 
    "pSFC_g": 707.75,       # MPa (flexión engrane permisible)     PAGINA 29
    "pSF_p": 210.26,         # MPa (flexión piñón permisible)            
    "pSFC_p": 707.75,      # MPa (contacto piñón permisible)

    "K_T": None, 
    "K_R": None,
    "C_H_p": None,     # si no lo conoces aún, puedes dejar None Generalmente None
    "C_H_g": None     # si no lo conoces aún, puedes dejar None
}

tension_planeta_corona = {
    "K_A": K_A, # PAG 32 TABLA 17
    "K_M": K_M, # PAG 32 TABLA 18
    "K_S": K_S, # PAG 33 TABLA 20
    "K_B": K_B, # PAG 32 ABAJO TABLA 17
    "K_V": None,  # CALCULA

    "K_I_pin": 1.42,   # 1 SI ES EXTERNO 1.4 SI ES INTERMEDIO
    "K_I_eng": 1.00,   
    "Jp_pin": tension_sol_planeta.get("Jp_eng"),       # PAG 35 GRAFICO 27 PARA RECTO 28 HELI
    "Jmod_pin": tension_sol_planeta.get("Jmod_eng"),     # 1 SI ES RECTO PAG 36 GRAFICO 29
    "Jp_eng": 0.44,
    "Jmod_eng": 1,

    "C_p": C_p,   # √MPa       # PAG 31 TABLA 15
    "C_F": C_F,                  #  PAG 31 GENERALMENTE 1 NORMAL, O MAYOR QUE 1 SI ES ASPERO
    "Q_v": Q_v,         # DATO

    "I": I,      # CALCULA
    "Jp": None,     # (opcional) J efectivo pinión si quieres forzar # elegir el mas pequeño 
    "Jg": None,     # (opcional) J efectivo engrane si quieres forzar
}


resistance_planeta_corona = {
    "K_L_p": resistance_sol_planeta.get("K_L_g"), # PAGINA 27 D.6 # PAGINA 28 TABLA 10 # depende de los ciclos
    "C_L_p": resistance_sol_planeta.get("C_L_g"), # PAGINA 27 D.6 
    "HB_p": resistance_sol_planeta.get("HB_eng"), # PAGINA 30

    "K_L_g": 1, # PAGINA 27 D.6 
    "C_L_g": 1, # PAGINA 27 D.6 
    "HB_g":300, # PAGINA 30 Tabla 12

    "temperatura": Temp,    # °C
    "R": R,              # confiabilidad objetivo (0–1)

    "caso_engrane": "masa",  # "masa" | "superficie"
    "Rq": 0.8,              # µm

    "pSF_g": 324,  # MPa (contacto engrane permisible)          Tabla 12 Pagina 30 
    "pSFC_g": 942,       # MPa (flexión engrane permisible)     PAGINA 29
    "pSF_p": resistance_sol_planeta.get("pSF_g"),         # MPa (flexión piñón permisible)            
    "pSFC_p": resistance_sol_planeta.get("pSFC_g"),      # MPa (contacto piñón permisible)

    "K_T": None, 
    "K_R": None,
    "C_H_p": None,     # si no lo conoces aún, puedes dejar None generalmente None
    "C_H_g": None     # si no lo conoces aún, puedes dejar None
}
