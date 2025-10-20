import sympy as sp
import pint 

def despejar_auto(eq, objetivo=None, SYMS=None, **kwargs):
    """
    Resuelve una ecuación simbólica (sp.Eq) con sympy.solve().
    
    eq         : ecuación tipo sp.Eq(...)
    objetivo   : variable a despejar (str o Symbol). Si no se indica,
                 se detecta automáticamente si hay solo una incógnita.
    SYMS       : diccionario de símbolos (nombre -> Symbol)
    **kwargs   : valores conocidos (ej: R=0.2, p_prom=1e5)
    """
    if SYMS is None:
        raise ValueError("Debe pasarse el diccionario de símbolos SYMS.")

    conocidos = {SYMS[k]: v for k, v in kwargs.items() if k in SYMS}

    # Detectar variable a resolver
    if objetivo is None:
        desconocidos = [v for v in eq.free_symbols if v not in conocidos]
        if len(desconocidos) != 1:
            raise ValueError("Debe haber exactamente una incógnita o indicar 'objetivo'.")
        var = desconocidos[0]
    else:
        var = SYMS[objetivo] if isinstance(objetivo, str) else objetivo

    # Sustituir valores y resolver
    eq_sub = sp.Eq(eq.lhs.subs(conocidos), eq.rhs.subs(conocidos))
    soluciones = sp.solve(eq_sub, var)
    return soluciones

def resolver(nombre_eq, ECUACIONES, SYMS, objetivo=None, **kwargs):
    """
    Busca la ecuación por nombre en ECUACIONES y llama a despejar_auto().
    Valida que todos los parámetros requeridos (salvo el objetivo) tengan valor.
    """
    if nombre_eq not in ECUACIONES:
        raise KeyError(f"Ecuación '{nombre_eq}' no existe. Opciones: {list(ECUACIONES)}")

    # Recolectar símbolos usados en la ecuación
    eq = ECUACIONES[nombre_eq]
    symbols_in_eq = {s.name for s in eq.free_symbols}

    # Eliminar el objetivo del conjunto de símbolos requeridos
    if objetivo in symbols_in_eq:
        symbols_in_eq.remove(objetivo)

    # Detectar parámetros faltantes o None
    missing = [s for s in symbols_in_eq if s not in kwargs or kwargs[s] is None]
    if missing:
        raise ValueError(f"Faltan valores para los parámetros: {missing}")

    # Llamar al despeje simbólico
    return despejar_auto(eq, objetivo=objetivo, SYMS=SYMS, **kwargs)


def resolver_auto(nombre_eq, objetivo, params, ECUACIONES=None, SYMS=None):
    """
    Llama a resolver(nombre_eq, ...) usando todos los valores de params excepto el objetivo.
    Filtra automáticamente los None y muestra advertencias si hay faltantes.
    """
    # Filtra el objetivo y prepara argumentos
    kwargs = {k: v for k, v in params.items() if k != objetivo}

    # Detectar faltantes o None antes de llamar
    faltantes = [k for k, v in kwargs.items() if v is None]
    if faltantes:
        print(f"⚠️ Faltan parámetros o están en None: {faltantes}")
        return None

    # Resolver
    sol = resolver(nombre_eq, ECUACIONES, SYMS, objetivo=objetivo, **kwargs)
    print(f"→ Resolviendo '{nombre_eq}' para {objetivo}:")
    print(sol)
    return sol


def consultar_ecuaciones(ECUACIONES):
    """Muestra las ecuaciones disponibles con su nombre, ecuación y variables."""
    print("\nEcuaciones disponibles:\n")
    for nombre, eq in ECUACIONES.items():
        vars_eq = sorted([str(v) for v in eq.free_symbols])
        print(f"Nombre: {nombre}")
        print(f"Ecuación: {eq}")
        print(f"Variables: {', '.join(vars_eq)}\n")


def get_SI(variable):
    return variable.to_base_units().magnitude