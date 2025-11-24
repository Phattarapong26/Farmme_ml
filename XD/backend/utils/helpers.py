# -*- coding: utf-8 -*-
"""
Helper functions for the application
"""

from .constants import CROP_MAP

def get_crop_name_from_id(crop_id: int) -> str:
    """Convert crop_id to crop name using CROP_MAP"""
    # Create reverse mapping from id to name
    id_to_crop = {v: k for k, v in CROP_MAP.items()}
    return id_to_crop.get(crop_id, f"พืชรหัส {crop_id}")

def get_crop_id_from_name(crop_name: str) -> int:
    """Convert crop name to crop_id using CROP_MAP"""
    return CROP_MAP.get(crop_name, 0)