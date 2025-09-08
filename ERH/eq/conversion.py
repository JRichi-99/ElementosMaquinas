import numpy as np

# ==========================
# VELOCIDAD ANGULAR
# ==========================
def rpm_a_rad_s(rpm):
    """Convierte de rpm a rad/s (aprox 2 decimales)."""
    valor = round((2 * np.pi * rpm) / 60.0, 2)
    print(f"rpm_a_rad_s({rpm}) = {valor} rad/s")
    return valor

def rad_s_a_rpm(rad_s):
    """Convierte de rad/s a rpm (aprox 2 decimales)."""
    valor = round((rad_s * 60.0) / (2 * np.pi), 2)
    print(f"rad_s_a_rpm({rad_s}) = {valor} rpm")
    return valor

# ==========================
# POTENCIA
# ==========================
def hp_a_w(hp: float) -> float:
    """Convierte potencia de HP a W (aprox 2 decimales)."""
    valor = round(hp * 745.7, 2)
    print(f"hp_a_w({hp}) = {valor} W")
    return valor

def w_a_hp(w: float) -> float:
    """Convierte potencia de W a HP (aprox 2 decimales)."""
    valor = round(w / 745.7, 2)
    print(f"w_a_hp({w}) = {valor} HP")
    return valor

# ==========================
# TORQUE
# ==========================
def nm_a_lb_in(torque_nm: float) -> float:
    """Convierte torque de N·m a lbf·in (aprox 2 decimales)."""
    valor = round(torque_nm * 8.8507, 2)
    print(f"nm_a_lb_in({torque_nm}) = {valor} lbf·in")
    return valor

def nm_a_lb_ft(torque_nm: float) -> float:
    """Convierte torque de N·m a lbf·ft (aprox 2 decimales)."""
    valor = round(torque_nm * 0.73756, 2)
    print(f"nm_a_lb_ft({torque_nm}) = {valor} lbf·ft")
    return valor

def lb_in_a_nm(torque_lb_in: float) -> float:
    """Convierte torque de lbf·in a N·m (aprox 2 decimales)."""
    valor = round(torque_lb_in / 8.8507, 2)
    print(f"lb_in_a_nm({torque_lb_in}) = {valor} N·m")
    return valor

def lb_ft_a_nm(torque_lb_ft: float) -> float:
    """Convierte torque de lbf·ft a N·m (aprox 2 decimales)."""
    valor = round(torque_lb_ft / 0.73756, 2)
    print(f"lb_ft_a_nm({torque_lb_ft}) = {valor} N·m")
    return valor
