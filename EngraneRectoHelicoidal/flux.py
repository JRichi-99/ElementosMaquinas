from PER import ParEngranesResistencia as PER

def run_par_pipeline(
    par_obj : PER,
    geo_params: dict | None = None,
    tension_params: dict | None = None,
    resistance_params: dict | None = None,
    until: str = "resistencia",
):
    """
    Procesa un ParEngranesResistencia ya creado por el usuario.

    Parámetros
    ----------
    par_obj : PER
        Objeto ya instanciado de ParEngranesResistencia (ej: PER()).
    geo_params : dict | None
        Si se entrega, se pasa a par_obj.set_par(geo_params).
    trans_params : dict | None
        Si until >= 'transmision', se aplican cargas iniciales con:
            where, H, H_units, Omega, Omega_units, T, T_units
        mediante par_obj.set_first_load(...).
    tension_params : dict | None
        Si until >= 'esfuerzos', se usan con:
            par_obj.tension_params(...); par_obj.calc_esfuerzos(); par_obj.resumen_esfuerzos()
    resistance_params : dict | None
        Si until == 'resistencia', se usan con:
            par_obj.resistance_params(...); par_obj.calc_resistencia(); par_obj.resumen_resistencia()
    until : {'geometria','transmision','esfuerzos','resistencia'}
        Etapa máxima a ejecutar.

    Retorna
    -------
    par_obj : PER
        El mismo objeto, modificado con la información calculada.
    """
    order = {"g": 0, "t": 1, "e": 2, "r": 3}
    if until not in order:
        raise ValueError("until debe ser: 'g', 't', 'e' o 'r'")
    stage = order[until]

    # 1) Geometría
    if geo_params is not None and not par_obj.loaded:
        par_obj.set_par(**geo_params)
    par_obj.resumen_geometria()
    par_obj.resumen_compatibilidad()

    if stage == 0:
        return par_obj

    par_obj.resumen_transmision()

    if stage == 1:
        return par_obj

    # 3) Esfuerzos
    if tension_params is not None:
        par_obj.tension_params(tension_params)
        par_obj.calc_esfuerzos()
        par_obj.resumen_esfuerzos()

    if stage == 2:
        return par_obj

    # 4) Resistencia
    if resistance_params is not None:
        par_obj.resistance_params(resistance_params)
        par_obj.calc_resistencia()
        par_obj.resumen_resistencia()

    return par_obj
