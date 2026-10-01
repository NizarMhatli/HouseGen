"""Deterministic seeding for the generator's random passes.

Several stages of the pipeline place things randomly — obstacle patterns and
asset selection (:mod:`modules.obstacles`), kiriha rock scatter
(:mod:`modules.kiriha`), riprap scatter (:mod:`modules.floor`). Historically
none of them were seeded, so no two runs produced the same tunnel and a bug
seen in the viewport could not be reproduced after a regenerate.

Why reseed the global :mod:`random` rather than thread a ``random.Random``
instance through the call graph: every one of those consumers already calls
bare ``random.uniform`` / ``random.choices`` / ``random.randint``, and
threading an instance would mean widening already-large signatures such as
``modules.obstacles.rules._select_asset``. Generation is single-threaded and
deterministically ordered, so global reseeding is genuinely reproducible.

Why *per stage* rather than one seed at the top: with a single seed, adding one
obstacle pattern shifts every subsequent draw and reshuffles the 100 kiriha
rocks too. Deriving an independent sub-seed per stage keeps a change local to
the stage that caused it, which is what makes a seed useful while iterating
rather than merely reproducible.
"""

import random
import zlib

# Knuth's multiplicative constant (2**32 / phi). Spreads adjacent seed values
# across the whole 32-bit range so seeds 1 and 2 give unrelated sequences.
_GOLDEN_RATIO_32 = 0x9E3779B1


def stage_seed(seed: int | None, stage: str) -> int | None:
    """Derive this stage's sub-seed without applying it.

    Exposed separately from :func:`seed_stage` for callers that own a local
    ``random.Random`` or need to hash the value into their own scheme — for
    example :mod:`modules.wall_pimples`, which uses a hand-rolled per-bolt hash
    rather than the global generator.

    Parameters
    ----------
    seed : int or None
        The scene's master seed. ``None`` means "unseeded".
    stage : str
        Short stable identifier for the pipeline stage, e.g. ``"obstacles"``.

    Returns
    -------
    int or None
        A 32-bit sub-seed, or ``None`` when ``seed`` is ``None``.
    """
    if seed is None:
        return None
    return ((int(seed) * _GOLDEN_RATIO_32) ^ (zlib.crc32(stage.encode()) & 0xFFFFFFFF)) & 0xFFFFFFFF


def seed_stage(seed: int | None, stage: str) -> None:
    """Reseed the global :mod:`random` generator for one pipeline stage.

    Call immediately before the stage runs. A ``None`` seed is a no-op, which
    leaves the previous unseeded behaviour intact for any scene that has not
    opted in.

    Parameters
    ----------
    seed : int or None
        The scene's master seed.
    stage : str
        Short stable identifier for the pipeline stage. Changing this string
        changes that stage's output, so treat it as part of the scene's
        reproducibility contract.

    Returns
    -------
    None
    """
    sub = stage_seed(seed, stage)
    if sub is not None:
        random.seed(sub)
