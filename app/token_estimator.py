import math


def estimate_tokens(text: str) -> int:
    """
    Grobe Token-Schätzung für GPT-ähnliche Modelle.

    Sehr vereinfachte Heuristik:
    - ca. 4 Zeichen pro Token im Durchschnitt
    """
    if not text:
        return 0
    char_count = len(text)
    return int(math.ceil(char_count / 4))


