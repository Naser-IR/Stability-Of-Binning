from functools import lru_cache
from typing import Optional, List, Tuple, Dict
import numpy as np
import pandas as pd


# ============================================================
# Helpers
# ============================================================
# --- Helper Functions (assuming they exist in your stable_construction.py) ---
def _boundary_values_to_indices(edges: np.ndarray, b_vals: Optional[List[float]], m: int) -> set:
    if not b_vals: return set()
    return {np.searchsorted(edges, v) for v in b_vals if 0 < np.searchsorted(edges, v) < m}

def _min_width_to_cells(w: Optional[float], step: float) -> int:
    return int(np.ceil(w / step)) if w is not None else 1

def _max_width_to_cells(w: Optional[float], step: float) -> Optional[int]:
    return int(np.floor(w / step)) if w is not None else None
# ----------------------------------------------------------------------------

def build_grid(series: pd.Series, L: float, U: float, step: float) -> Tuple[np.ndarray, np.ndarray]:
    if step <= 0:
        raise ValueError("step must be > 0")
    if U <= L:
        raise ValueError("U must be > L")

    vals = pd.to_numeric(series, errors="coerce").dropna().to_numpy()

    m = int(np.ceil((U - L) / step))
    edges = (L + step * np.arange(m + 1)).astype(float)

    counts, _ = np.histogram(vals, bins=edges)

    pref = np.zeros(m + 1, dtype=int)
    pref[1:] = np.cumsum(counts, dtype=int)
    return edges, pref


def _boundary_values_to_indices(edges: np.ndarray, values, m: int) -> Optional[set]:
    """
    Convert real boundary values like [6.0, 12.0] to grid indices.
    Ignore 0 and m since they are outer boundaries, not internal cuts.
    """
    if values is None:
        return None

    edge_to_idx = {round(float(edges[i]), 12): i for i in range(len(edges))}
    out = set()

    for x in values:
        xf = round(float(x), 12)
        if xf not in edge_to_idx:
            raise ValueError(f"Boundary {x} is not on the grid. Grid values are {list(edges)}")

        idx = edge_to_idx[xf]
        if idx == 0 or idx == m:
            continue
        out.add(idx)

    return out


def _min_width_to_cells(min_width: Optional[float], step: float) -> Optional[int]:
    if min_width is None:
        return None
    return max(1, int(np.ceil(min_width / step)))


def _max_width_to_cells(max_width: Optional[float], step: float) -> Optional[int]:
    if max_width is None:
        return None
    return max(1, int(np.floor(max_width / step)))


def build_DEV_2d(pref: np.ndarray, s: int) -> np.ndarray:
    """
    Builds the 2D DEV matrix for the independent perturbation model.
    DEV[l, r] stores the MAXIMUM error over all valid (dL, dR) shifts.
    """
    m = len(pref) - 1
    INF = int(pref[m]) + 10**9
    DEV = np.full((m + 1, m + 1), INF, dtype=int)

    def cnt(a: int, b: int) -> int:
        return int(pref[b] - pref[a])

    for l in range(0, m):
        for r in range(l + 1, m + 1):
            base = cnt(l, r)
            max_err = -1
            valid_interval = False
            
            for dL in range(-s, s + 1):
                for dR in range(-s, s + 1):
                    Ls = l + dL
                    Rs = r + dR
                    
                    # Validation logic (prevent crossing or going out of bounds)
                    valid = True
                    if l == 0 and dL != 0: valid = False
                    if r == m and dR != 0: valid = False
                    if l != 0 and r != m:
                        if not (0 < Ls < m) or not (0 < Rs < m): valid = False
                    if not (0 <= Ls < m and 0 < Rs <= m): valid = False
                    if not (Ls < Rs): valid = False
                    
                    if valid:
                        shifted = cnt(Ls, Rs)
                        err = abs(base - shifted)
                        if err > max_err:
                            max_err = err
                        valid_interval = True
            
            if valid_interval:
                DEV[l, r] = max_err
                
    return DEV



# ============================================================
# Algorithm 2 — Naive exhaustive
# ============================================================

def algorithm2_independent_naive(
    series: pd.Series,
    L: float, U: float, step: float,
    k: int, epsilon: float, C: float,
    *,
    candidate_stride: int = 1,
    max_combinations: Optional[int] = None,
    min_width: Optional[float] = None,
    max_width: Optional[float] = None,
    excluded_boundaries: Optional[List[float]] = None,
) -> Optional[List[float]]:

    edges, pref = build_grid(series, L, U, step)
    m = len(edges) - 1
    s = int(np.floor(epsilon / step))

    if s < 0 or k < 1 or k > m:
        return None

    min_cells = _min_width_to_cells(min_width, step)
    max_cells = _max_width_to_cells(max_width, step)

    if min_cells is not None and k * min_cells > m:
        return None
    if min_cells is not None and max_cells is not None and min_cells > max_cells:
        return None

    excluded_idx = _boundary_values_to_indices(edges, excluded_boundaries, m)

    from itertools import combinations

    candidates = list(range(1, m, candidate_stride))

    tested = 0
    # Exhaustively try every combination of boundaries
    for combo in combinations(candidates, k - 1):
        if max_combinations is not None and tested >= max_combinations:
            break
        tested += 1

        if excluded_idx is not None and any(c in excluded_idx for c in combo):
            continue

        bounds = (0, *combo, m)
        widths = [b - a for a, b in zip(bounds[:-1], bounds[1:])]

        if min_cells is not None and any(w < min_cells for w in widths):
            continue
        if max_cells is not None and any(w > max_cells for w in widths):
            continue

        stable = True

        # In the independent model, we evaluate each bin completely on its own
        for t in range(k):
            l = bounds[t]
            r = bounds[t + 1]
            
            if l >= r:
                stable = False
                break
                
            base_count = int(pref[r] - pref[l])
            bin_stable = True
            
            # Test all independent valid shifts (dL and dR) just for this specific bin
            for dL in range(-s, s + 1):
                for dR in range(-s, s + 1):
                    Ls = l + dL
                    Rs = r + dR
                    
                    # Validation logic (prevent crossing or going out of bounds)
                    valid = True
                    if l == 0 and dL != 0: valid = False
                    if r == m and dR != 0: valid = False
                    if l != 0 and r != m:
                        if not (0 < Ls < m) or not (0 < Rs < m): valid = False
                    if not (0 <= Ls < m and 0 < Rs <= m): valid = False
                    if not (Ls < Rs): valid = False
                    
                    if not valid:
                        continue
                        
                    shifted_cnt = int(pref[Rs] - pref[Ls])
                    dev = abs(base_count - shifted_cnt)
                    
                    # If this bin fails the threshold under any shift, it fails immediately
                    if dev >= C:
                        bin_stable = False
                        break
                        
                if not bin_stable:
                    break
            
            # If one bin in the combination is unstable, the whole combination is rejected
            if not bin_stable:
                stable = False
                break 

        if stable:
            return [float(edges[c]) for c in combo]

    return None



### The dp algorithm 
def algorithm4_independent_dp(
    series: pd.Series,
    L: float, U: float, step: float,
    k: int, epsilon: float, C: float,
    *,
    min_width: Optional[float] = None,
    max_width: Optional[float] = None,
    excluded_boundaries: Optional[List[float]] = None,
) -> Tuple[Optional[List[float]], Optional[int]]:

    edges, pref = build_grid(series, L, U, step)
    m = len(edges) - 1
    s = int(np.floor(epsilon / step))

    if s < 0 or k < 1 or k > m: return (None, None)

    min_cells = _min_width_to_cells(min_width, step)
    max_cells = _max_width_to_cells(max_width, step)
    
    # Global impossibility checks
    if k * min_cells > m: return (None, None)
    if max_cells is not None and min_cells > max_cells: return (None, None)
    if max_cells is not None and k * max_cells < m: return (None, None)

    excluded_idx = _boundary_values_to_indices(edges, excluded_boundaries, m)
    def boundary_allowed(j: int) -> bool:
        return excluded_idx is None or j not in excluded_idx

    DEV = build_DEV_2d(pref, s)
    INF = int(pref[m]) + 10**9

    OPT = np.full((m + 1, k + 1), INF, dtype=int)
    parent = np.zeros((m + 1, k + 1), dtype=int)

    # Base case: j = 1 (A single bin from 0 to i)
    for i in range(1, m + 1):
        if i < min_cells: continue
        if max_cells is not None and i > max_cells: continue
        OPT[i, 1] = DEV[0, i]

    # DP Formula for j > 1
    for j in range(2, k + 1):
        # 'i' must be at least large enough to hold 'j' bins of min_cells
        for i in range(j * min_cells, m + 1):
            
            # MATH: Define the valid search window for the previous boundary 'l'
            # 1. l must leave enough room behind it for the previous j-1 bins
            lo = (j - 1) * min_cells
            # 2. the current bin (i - l) cannot exceed max_cells -> l >= i - max_cells
            if max_cells is not None:
                lo = max(lo, i - max_cells)
                
            # 3. the current bin (i - l) must be at least min_cells -> l <= i - min_cells
            hi = i - min_cells
            # 4. the previous bins cannot exceed their max_cells limit -> l <= (j - 1) * max_cells
            if max_cells is not None:
                hi = min(hi, (j - 1) * max_cells)

            best_val = INF
            best_l = -1

            # Only search within the mathematically valid window
            for l in range(lo, hi + 1):
                if not boundary_allowed(l): continue
                if OPT[l, j - 1] == INF or DEV[l, i] == INF: continue
                
                val = max(OPT[l, j - 1], DEV[l, i])
                
                if val < best_val:
                    best_val = val
                    best_l = l
            
            OPT[i, j] = best_val
            parent[i, j] = best_l

    best_T = OPT[m, k]
    if best_T >= C or best_T == INF:
        return (None, None if best_T == INF else int(best_T))

    cuts_idx = []
    curr = m
    for j in range(k, 1, -1):
        curr = parent[curr, j]
        cuts_idx.append(curr)

    cuts_idx.reverse()
    return ([float(edges[c]) for c in cuts_idx], int(best_T))





###The filtered graph algorithm


def algorithm5_independent_graph(
    series: pd.Series,
    L: float, U: float, step: float,
    k: int, epsilon: float, C: float,
    *,
    use_boundary_prefilter: bool = True,
    min_width: Optional[float] = None,
    max_width: Optional[float] = None,
    excluded_boundaries: Optional[List[float]] = None,
    required_boundaries: Optional[List[float]] = None,
) -> Optional[List[float]]:

    edges, pref = build_grid(series, L, U, step)
    m = len(edges) - 1
    s = int(np.floor(epsilon / step))

    if s < 0 or k < 1 or k > m: return None

    # --- 1. Width Constraints ---
    min_cells = _min_width_to_cells(min_width, step)
    max_cells = _max_width_to_cells(max_width, step)
    
    if k * min_cells > m: return None
    if max_cells is not None and min_cells > max_cells: return None

    # --- 2. Boundary Constraints (I and F) ---
    excluded_idx = _boundary_values_to_indices(edges, excluded_boundaries, m)
    if excluded_idx is None: 
        excluded_idx = set()
        
    required_idx = _boundary_values_to_indices(edges, required_boundaries, m)
    if required_idx is None: 
        required_idx = set()
    
    # Validation: Cannot require more points than we have internal cuts (k - 1)
    if len(required_idx) > k - 1: return None
    # Validation: A point cannot be both required and forbidden
    if excluded_idx and required_idx.intersection(excluded_idx): return None

    required_list = sorted(required_idx) # Sorted in domain order: p_1 < ... < p_r

    DEV = build_DEV_2d(pref, s)
    INF = int(pref[m]) + 10**9

    def boundary_allowed(j: int) -> bool:
        return j not in excluded_idx

    # Pre-filtering: Removes Forbidden points before graph search begins
    if use_boundary_prefilter:
        cand_interval = (DEV < C) & (DEV < INF)
        P = [0, m]
        for j in range(1, m):
            if not boundary_allowed(j): continue
            if cand_interval[:j, j].any() and cand_interval[j, j + 1:].any():
                P.append(j)
        P = np.array(sorted(set(P)), dtype=int)

    # --- The Layered Graph Equivalent ---
    # Finds the next required point p_{l+1} based on current position i
    def get_next_required(i: int) -> int:
        for p in required_list:
            if p > i: return p
        return m + 1 # No more required points left

    # Simplified DFS: The Bitmask is completely removed!
    @lru_cache(maxsize=None)
    def dfs(i: int, bins_left: int) -> Optional[Tuple[int, ...]]:
        if bins_left == 1:
            # We must be in layer 'r' (all required points visited) to finish
            if get_next_required(i) <= m: 
                return None
            
            last_w = m - i
            if last_w < min_cells: return None
            if max_cells is not None and last_w > max_cells: return None

            if DEV[i, m] < C:
                return (i, m)
            return None

        # Determine the window of legal next boundaries
        lo = i + min_cells
        hi = m - (bins_left - 1) * min_cells
        if max_cells is not None: 
            hi = min(hi, i + max_cells)
            
        # ENFORCE REQUIRED BOUNDARY (Layer Constraint)
        # "Edges cannot pass over the next required point" -> v <= p_{l+1}
        next_req = get_next_required(i)
        hi = min(hi, next_req)

        # Loop through valid edges
        if use_boundary_prefilter:
            valid_js = P[(P >= lo) & (P <= hi)]
        else:
            valid_js = range(lo, hi + 1)
            
        for j in valid_js:
            if not use_boundary_prefilter and not boundary_allowed(j): 
                continue

            # Check if this edge is valid under threshold C
            if DEV[i, j] >= C:
                continue
            
            # Step forward
            tail = dfs(j, bins_left - 1)
            if tail is not None:
                return (i,) + tail

        return None

    path = dfs(0, k)
    
    if path is None: return None
    bnds = list(path)
    cuts_idx = bnds[1:-1]
    
    return [float(edges[c]) for c in cuts_idx]