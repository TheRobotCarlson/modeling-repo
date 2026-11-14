"""Shared helpers for the modeling workspace.

    from modelkit import Assembly, save_series
"""

from .cad import MATERIALS, Assembly
from .paths import ROOT, data_dir
from .sim import save_series

__all__ = ["Assembly", "MATERIALS", "ROOT", "data_dir", "save_series"]
