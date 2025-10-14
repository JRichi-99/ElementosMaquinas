from .PER import ParEngranesResistencia as PER
import numpy as np
import os

def run_par_pipeline(
    par_obj : PER,
    geo_params: dict | None = None,
    tension_params: dict | None = None,
    resistance_params: dict | None = None,
    until: str = "r",
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
        return

    par_obj.resumen_transmision()

    if stage == 1:
        return 

    # 3) Esfuerzos
    if tension_params is not None:
        par_obj.tension_params(tension_params)
        par_obj.calc_esfuerzos()
        par_obj.resumen_esfuerzos()

    if stage == 2:
        return 

    # 4) Resistencia
    if resistance_params is not None:
        par_obj.resistance_params(resistance_params)
        par_obj.calc_resistencia()
        par_obj.resumen_resistencia()




def export_factibles(factible_modules: dict, filename: str = "factibles.txt"):
    """
    Escribe los resultados factibles en un archivo de texto.

    Parameters
    ----------
    factible_modules : dict
        Diccionario con clave (m, Np, Ng) y valor = data.
        data puede contener:
          - "pinion": dict con resultados (flexion, picadura)
          - "engrane": dict con resultados (flexion, picadura)
          - "C": float (distancia entre centros)
    filename : str
        Nombre del archivo de salida. Por defecto 'factibles.txt'.
    """
    if not factible_modules:
        raise ValueError("No hay soluciones factibles para exportar.")

    lines = []
    lines.append("========= RESULTADOS FACTIBLES =========\n")

    for (m, Np, Ng), data in factible_modules.items():
        lines.append(f"Módulo: {m:.2f} | Np: {Np} | Ng: {Ng}")

        if isinstance(data, dict):
            # Recorre solo pinion/engrane si son dict
            for elem in ("pinion", "engrane"):
                vals = data.get(elem, None)
                if isinstance(vals, dict):
                    lines.append(f"  [{elem.upper()}]")
                    for modo, tripleta in vals.items():  # 'flexion' / 'picadura'
                        esfuerzo    = tripleta.get("esfuerzo", "-")
                        resistencia = tripleta.get("resistencia", "-")
                        factor      = tripleta.get("factor", "-")
                        lines.append(
                            f"    {modo:<8} σ={esfuerzo} | σ_perm={resistencia} | FS={factor}"
                        )
            # Si existe la distancia entre centros
            if "C" in data:
                try:
                    C_val = float(data["C"])
                    lines.append(f"  Distancia entre centros: {C_val:.2f} mm")
                except Exception:
                    lines.append(f"  Distancia entre centros: {data['C']}")

        lines.append("")  # separador

    texto = "\n".join(lines)

    with open(filename, "w", encoding="utf-8") as f:
        f.write(texto)

    return filename




def iterate_over(
    par_obj : PER,                         # instancia PER
    relation: float = 2.5,           # m_g = Ng/Np
    psi: float = 22,                 # [deg]
    phi_n: float = 20,               # [deg]
    modules: list | None = None,     # lista de módulos [mm]
    tension_params: dict | None = None,
    resistance_params: dict | None = None,
    umbral_fs: float = 1.45,         # umbral factor de seguridad
    max_gear_teeth: int = 200        # LÍMITE EN EL ENGRANE (Ng máx)
):
    if not modules:
        raise ValueError("Debes proporcionar una lista 'modules' con al menos un módulo.")
    if relation <= 0:
        raise ValueError("La relación (Ng/Np) debe ser > 0.")
    if max_gear_teeth < 1:
        raise ValueError("max_gear_teeth debe ser ≥ 1.")

    # Ángulos a radianes
    psi_rad   = np.deg2rad(float(psi))
    phi_n_rad = np.deg2rad(float(phi_n))
    # φ_t = atan( tan(φ_n) / cos(ψ) )
    phi_t_rad = np.arctan(np.tan(phi_n_rad) / np.cos(psi_rad))

    factible_modules: dict = {}

    for m in modules:
        # 1) N mínimo del piñón
        Np_min, _ = par_obj.minimo_dientes(
            clase='heli',
            phi_t=phi_t_rad,     # rad
            psi=psi_rad,         # rad
            m_g=relation,
        )
        if Np_min is None or Np_min < 1:
            continue

        # 2) N máximo del piñón a partir de Ng_max
        #    Ng = ceil(m_g * Np) ≤ Ng_max  =>  Np ≤ floor(Ng_max / m_g)
        Np_max = int(np.floor(max_gear_teeth / float(relation)))
        if Np_max < Np_min:
            continue

        # Recomendación de ancho de cara
        F = 16.0 * float(m)

        # 3) Iteración acotada por Np_min..Np_max
        for dientes_pinion in range(int(Np_min), int(Np_max) + 1):
            Ng = int(np.ceil(relation * dientes_pinion))
            if Ng > max_gear_teeth:
                continue

            geo_params = {
                "pi_n": None,
                "m": float(m),
                "phi_n": float(phi_n),    # grados
                "psi": float(psi),        # grados
                "N_pinion": int(dientes_pinion),
                "N_engrane": int(Ng),
                "F_pinion": float(F),
                "F_engrane": float(F),
                "sistema_dientes": "total",
                "acople": "externos",
                "xp": 0.0,
            }

            # 4) Geometría
            par_obj.set_par(**geo_params)

            # 5) Compatibilidad
            if not par_obj.es_compatible():
                continue

            # 6) Carga inicial
            trans_params = {
                "where": "pinion",
                "H": 85, "H_units": "hp",
                "Omega": 2500, "Omega_units": "rpm",
                "T": None, "T_units": "si",
            }
            par_obj.set_first_load(**trans_params)
            par_obj.set_ciclos(horas=4,dias=260,years=4)

            # 7) Esfuerzos
            if tension_params is not None:
                par_obj.tension_params(tension_params)
                par_obj.calc_esfuerzos()

            # 8) Resistencia
            resiste = False
            data = None
            if resistance_params is not None:
                par_obj.resistance_params(resistance_params)
                par_obj.calc_resistencia()
                resiste, data = par_obj.evaluar_resistencia(umbral=umbral_fs)
    
            # 9) Guardar si cumple
            if resiste:
                data["C"] = par_obj.C
                factible_modules[(float(m), int(dientes_pinion), int(Ng))] = data

    export_factibles(factible_modules)


