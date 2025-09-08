#Solo el J depende de los dientes aca

tension_params0 = {
    "K_A": 1, # PAG 32 TABLA 17
    "K_M": 1.6, # PAG 32 TABLA 18
    "K_S": 1.00, # PAG 33 TABLA 20
    "K_B": 1.00, # PAG 32 ABAJO TABLA 17
    "K_V": None,  # CALCULA

    "K_I_pin": 1.00,   # 1 SI ES EXTERNO 1.4 SI ES INTERMEDIO
    "K_I_eng": 1.00,   
    "Jp_pin": 0.42,       # PAG 35 GRAFICO 27 PARA RECTO 28 HELI
    "Jmod_pin": 1,     # 1 SI ES RECTO PAG 36 GRAFICO 29
    "Jp_eng": 0.46,
    "Jmod_eng": 1,

    "C_p": 191.0,   # √MPa       # PAG 31 TABLA 15
    "C_F": 1.00,                  #  PAG 31 GENERALMENTE 1 NORMAL, O MAYOR QUE 1 SI ES ASPERO
    "Q_v": 10,         # DATO

    "I": 0.1,      # CALCULA
    "Jp": None,     # (opcional) J efectivo pinión si quieres forzar
    "Jg": None,     # (opcional) J efectivo engrane si quieres forzar
}

tension_params1 = {
    "K_A": 1.25,
    "K_M": 1.6,
    "K_S": 1.00,
    "K_B": 1.00,
    "K_V": None,

    "K_I_pin": 1.00,
    "K_I_eng": 1.00,
    "Jp_pin": 0.42,
    "Jmod_pin": 1,
    "Jp_eng": 0.46,
    "Jmod_eng": 1,

    "C_p": 191.0,   # √MPa
    "C_F": 1.00,
    "Q_v": 10,

    "I": 0.1,
    "Jp": None,     # (opcional) J efectivo pinión si quieres forzar
    "Jg": None,     # (opcional) J efectivo engrane si quieres forzar
}

tension_params2 = {
    "K_A": 1.25,
    "K_M": 1.6,
    "K_S": 1.00,
    "K_B": 1.00,
    "K_V": None,

    "K_I_pin": 1.00,
    "K_I_eng": 1.00,
    "Jp_pin": 0.42,
    "Jmod_pin": 1,
    "Jp_eng": 0.46,
    "Jmod_eng": 1,

    "C_p": 191.0,   # √MPa
    "C_F": 1.00,
    "Q_v": 10,

    "I": 0.1,
    "Jp": None,     # (opcional) J efectivo pinión si quieres forzar
    "Jg": None,     # (opcional) J efectivo engrane si quieres forzar
}