pinion_resistance = {
    # Resistencia básica
    "Sf": 137,      # Resistencia a flexión
    "Sfc": 492,     # Resistencia a contacto

    # Factores AGMA
    "K_L": 0.978,     # Factor de vida
    "K_R": 1,     # Factor de confiabilidad
    "K_T": 1,     # Factor de temperatura

    # Factores de contacto
    "C_L": 0.962,     # Factor de lubricación
    "C_H": 1,     # Relación de dureza

    # Parámetros auxiliares
    "Tf": None,      # Temperatura (para calcular K_T)
    "R": None,       # Confiabilidad (para calcular K_R)
    "caso": None,    # 'pinion', 'engrane,masa', 'Engrane,sup'
    "HBp": None,     # Dureza Brinell del piñón
    "HBg": None,     # Dureza Brinell del engrane
    "m_g": None,     # Relación de transmisión
    "R_q": None      # Rugosidad superficial (para engrane sup.)
}

engrane_resistance = {
    # Resistencia básica
    "Sf": None,      # Resistencia a flexión
    "Sfc": None,     # Resistencia a contacto

    # Factores AGMA
    "K_L": None,     # Factor de vida
    "K_R": None,     # Factor de confiabilidad
    "K_T": None,     # Factor de temperatura

    # Factores de contacto
    "C_L": None,     # Factor de lubricación
    "C_H": None,     # Relación de dureza

    # Parámetros auxiliares
    "Tf": None,      # Temperatura (para calcular K_T)
    "R": None,       # Confiabilidad (para calcular K_R)
    "caso": None,    # 'pinion', 'engrane,masa', 'Engrane,sup'
    "HBp": None,     # Dureza Brinell del piñón
    "HBg": None,     # Dureza Brinell del engrane
    "m_g": None,     # Relación de transmisión
    "R_q": None      # Rugosidad superficial (para engrane sup.)
}

resistance_params = {"pinion_resistance": pinion_resistance, "engrane_resistance":engrane_resistance}