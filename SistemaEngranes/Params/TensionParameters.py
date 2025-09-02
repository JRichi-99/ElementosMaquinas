K_a = 1
K_m = 1
K_s = 1


pinion_tension = {
    # Factores de corrección AGMA
    "K_a": K_a,   # Factor de aplicación
    "K_m": K_m,   # Factor de distribución de carga
    "K_s": K_s,   # Factor de tamaño
    "K_B": 1,   # Factor de espesor del aro
    "K_I": 1,   # Factor de engrane intermedio
    "K_v": None,   # Factor dinámico

    # Parámetro de calidad (usado para calcular K_v si falta)
    "Q_v": 6,

    # Geometría
    "J": 0.31,     # Factor geométrico de flexión
    "I": None,     # Factor geométrico de contacto

    # Materiales
    "C_p": 191,   # Coeficiente elástico
    "C_f": 1,   # Factor de acabado superficial

    # Parámetros extra (para K_B)
    "tr": None     # Espesor del aro (para calcular mb = tr/ht)
}

engrane_tension = {
    # Factores de corrección AGMA
    "K_a": K_a,   # Factor de aplicación
    "K_m": K_m,   # Factor de distribución de carga
    "K_s": K_s,   # Factor de tamaño
    
    "K_B": None,   # Factor de espesor del aro
    "K_I": None,   # Factor de engrane intermedio
    "K_v": None,   # Factor dinámico

    # Parámetro de calidad (usado para calcular K_v si falta)
    "Q_v": None,

    # Geometría
    "J": None,     # Factor geométrico de flexión
    "I": None,     # Factor geométrico de contacto

    # Materiales
    "C_p": None,   # Coeficiente elástico
    "C_f": None,   # Factor de acabado superficial

    # Parámetros extra (para K_B)
    "tr": None     # Espesor del aro (para calcular mb = tr/ht)
}

tension_params = {"pinion_tension": pinion_tension, "engrane_tension":engrane_tension}