"""
Módulo de RPAs do sistema
"""

from .rpa_base import RPABase
from .vivo_rpa import VivoRPA
from .oi_rpa import OiRPA
from .embratel_rpa import EmbratelRPA
from .sat_rpa import SatRPA
from .azuton_rpa import AzutonRPA
from .digitalnet_rpa import DigitalnetRPA

__all__ = [
    "RPABase",
    "VivoRPA",
    "OiRPA", 
    "EmbratelRPA",
    "SatRPA",
    "AzutonRPA",
    "DigitalnetRPA"
]