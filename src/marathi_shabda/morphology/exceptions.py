"""
Exceptions and irregular forms for Marathi morphology.
"""

from typing import Dict

# Dictionary mapping oblique/irregular stems to their base lemma
# Format: "oblique_stem": "lemma"
IRREGULAR_STEMS: Dict[str, str] = {
    "मुली": "मुलगी",  # mulgi (girl) -> muli (oblique)
    "मुला": "मुलगा",  # mulga (boy) -> muli (oblique)
    # Add more irregulars here as needed
}
