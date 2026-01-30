"""Inference package."""

from marathi_shabda.inference.pos_inference import infer_pos
from marathi_shabda.inference.kaal_inference import infer_kaal

__all__ = [
    "infer_pos",
    "infer_kaal",
]
