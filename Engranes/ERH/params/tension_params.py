#Solo el J depende de los dientes aca
C_F = 1                               #  PAG 31 GENERALMENTE 1 NORMAL, O MAYOR QUE 1 SI ES ASPERO
K_A = 1                               # PAG 32 TABLA 17
K_B = 1                               # PAG 32 ABAJO TABLA 17
K_M = 1                               # PAG 32 TABLA 18
K_S = 1                               # PAG 33 TABLA 20
Q_v = 10
C_p = 191
I = None

tension_params0 = {
    "K_A": K_A, # PAG 32 TABLA 17
    "K_M": K_M, # PAG 32 TABLA 18
    "K_S": K_S, # PAG 33 TABLA 20
    "K_B": K_B, # PAG 32 ABAJO TABLA 17
    "K_V": None,  # CALCULA

    "K_I_pin": 1.00,   # 1 SI ES EXTERNO 1.4 SI ES INTERMEDIO
    "K_I_eng": 1.00,   
    "Jp_pin": 0.42,       # PAG 35 GRAFICO 27 PARA RECTO 28 HELI
    "Jmod_pin": 1,     # 1 SI ES RECTO PAG 36 GRAFICO 29
    "Jp_eng": 0.44,
    "Jmod_eng": 1,

    "C_p": C_p,   # √MPa       # PAG 31 TABLA 15
    "C_F": C_F,                  #  PAG 31 GENERALMENTE 1 NORMAL, O MAYOR QUE 1 SI ES ASPERO
    "Q_v": Q_v,         # DATO

    "I": I,      # CALCULA
    "Jp": None,     # (opcional) J efectivo pinión si quieres forzar # elegir el mas pequeño 
    "Jg": None,     # (opcional) J efectivo engrane si quieres forzar
}

tension_params1 = {
    "K_A": K_A,
    "K_M": K_M,
    "K_S": K_S,
    "K_B": K_B,
    "K_V": None,

    "K_I_pin": 1.00,
    "K_I_eng": 1.00,
    "Jp_pin": 0.42,
    "Jmod_pin": 1,
    "Jp_eng": 0.44,
    "Jmod_eng": 1,

    "C_p": C_p,   # √MPa
    "C_F": C_F,
    "Q_v": Q_v,

    "I": I,
    "Jp": None,     # (opcional) J efectivo pinión si quieres forzar
    "Jg": None,     # (opcional) J efectivo engrane si quieres forzar
}

tension_params2 = {
    "K_A": K_A,
    "K_M": K_M,
    "K_S": K_S,
    "K_B": K_B,
    "K_V": None,

    "K_I_pin": 1.00,
    "K_I_eng": 1.00,
    "Jp_pin": 0.42,
    "Jmod_pin": 1,
    "Jp_eng": 0.46,
    "Jmod_eng": 1,

    "C_p": C_p,   # √MPa
    "C_F": C_F,
    "Q_v": Q_v,

    "I": I,
    "Jp": None,     # (opcional) J efectivo pinión si quieres forzar
    "Jg": None,     # (opcional) J efectivo engrane si quieres forzar
}