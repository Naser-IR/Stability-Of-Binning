from functools import lru_cache
from typing import Optional, List, Tuple, Dict
import numpy as np
import pandas as pd


# ============================================================
# Helpers
# ============================================================

def build_universal_DEV_2d(
    x_series: pd.Series,
    y_series: Optional[pd.Series], 
    L: float, U: float, step: float, s: int, 
    agg_func: str = 'COUNT'
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Universal builder for the DEV matrix supporting COUNT, SUM, AVG, MIN, MAX.
    """
    edges = np.arange(L, U + step, step)
    m = len(edges) - 1
    
    # Map each data point to its base cell (0 to m-1)
    cell_idx = np.digitize(x_series, edges) - 1
    valid_mask = (cell_idx >= 0) & (cell_idx < m)
    
    cells_valid = cell_idx[valid_mask]
    y_valid = y_series[valid_mask] if y_series is not None else np.ones(len(cells_valid))
    
    df_cells = pd.DataFrame({'cell': cells_valid, 'y': y_valid})
    
    # 1. Precompute the exact aggregate for every possible interval [l, r)
    VAL = np.zeros((m + 1, m + 1), dtype=float)
    agg = agg_func.upper()
    
    if agg in ['COUNT', 'SUM']:
        base_vals = df_cells.groupby('cell')['y'].sum().reindex(range(m), fill_value=0).values
        pref = np.zeros(m + 1)
        pref[1:] = np.cumsum(base_vals)
        for l in range(m):
            for r in range(l + 1, m + 1):
                VAL[l, r] = pref[r] - pref[l]
                
    elif agg == 'AVG':
        base_sums = df_cells.groupby('cell')['y'].sum().reindex(range(m), fill_value=0).values
        base_counts = df_cells.groupby('cell')['y'].count().reindex(range(m), fill_value=0).values
        pref_sum = np.zeros(m + 1)
        pref_sum[1:] = np.cumsum(base_sums)
        pref_count = np.zeros(m + 1)
        pref_count[1:] = np.cumsum(base_counts)
        for l in range(m):
            for r in range(l + 1, m + 1):
                c = pref_count[r] - pref_count[l]
                VAL[l, r] = (pref_sum[r] - pref_sum[l]) / c if c > 0 else 0.0
                
    elif agg == 'MAX':
        base_max = df_cells.groupby('cell')['y'].max().reindex(range(m), fill_value=-np.inf).values
        for l in range(m):
            curr_max = -np.inf
            for r in range(l + 1, m + 1):
                curr_max = max(curr_max, base_max[r - 1])
                VAL[l, r] = curr_max
                
    elif agg == 'MIN':
        base_min = df_cells.groupby('cell')['y'].min().reindex(range(m), fill_value=np.inf).values
        for l in range(m):
            curr_min = np.inf
            for r in range(l + 1, m + 1):
                curr_min = min(curr_min, base_min[r - 1])
                VAL[l, r] = curr_min
    else:
        raise ValueError(f"Unsupported aggregation: {agg}")

    # 2. Build the DEV matrix by checking epsilon shifts
    INF = 10**12
    DEV = np.full((m + 1, m + 1), INF, dtype=float)
    
    for l in range(m):
        for r in range(l + 1, m + 1):
            base_val = VAL[l, r]
            max_err = -1.0
            valid_interval = False
            
            for dL in range(-s, s + 1):
                for dR in range(-s, s + 1):
                    Ls, Rs = l + dL, r + dR
                    
                    # Prevent out-of-bounds or crossing boundaries
                    if l == 0 and dL != 0: continue
                    if r == m and dR != 0: continue
                    if l != 0 and not (0 < Ls < m): continue
                    if r != m and not (0 < Rs < m): continue
                    if Ls >= Rs: continue
                    
                    shifted_val = VAL[Ls, Rs]
                    
                    # Handle empty bins for Min/Max
                    if np.isinf(base_val) or np.isinf(shifted_val):
                        err = 0.0 if (np.isinf(base_val) and np.isinf(shifted_val)) else INF
                    else:
                        err = abs(base_val - shifted_val)
                        
                    if err > max_err:
                        max_err = err
                    valid_interval = True
            
            if valid_interval:
                DEV[l, r] = max_err
                
    return DEV, edges



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
# Algorithm 2 — Naive exhaustive (Updated for all Aggregations)
# ============================================================

def algorithm2_independent_naive(
    x_series: pd.Series,                 # <--- Changed to match 4 and 5
    y_series: Optional[pd.Series],       # <--- Changed to match 4 and 5
    L: float, U: float, step: float,
    k: int, epsilon: float, C: float,
    agg_func: str = 'COUNT',             # <--- Changed to match 4 and 5
    *,
    candidate_stride: int = 1,
    max_combinations: Optional[int] = None,
    min_width: Optional[float] = None,
    max_width: Optional[float] = None,
    excluded_boundaries: Optional[List[float]] = None,
) -> Optional[List[float]]:

    s = int(np.floor(epsilon / step))
    # Build the universal DEV matrix first
    DEV, edges = build_universal_DEV_2d(x_series, y_series, L, U, step, s, agg_func)
    m = len(edges) - 1

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

        # Check Excluded Boundaries
        if excluded_idx is not None and any(c in excluded_idx for c in combo):
            continue

        bounds = (0, *combo, m)
        widths = [b - a for a, b in zip(bounds[:-1], bounds[1:])]

        # Check Width constraints
        if min_cells is not None and any(w < min_cells for w in widths):
            continue
        if max_cells is not None and any(w > max_cells for w in widths):
            continue

        stable = True

        # Check stability using the pre-calculated DEV matrix
        for t in range(k):
            l = bounds[t]
            r = bounds[t + 1]
            
            # If the bin is invalid or its pre-computed worst-case error breaks the threshold
            if l >= r or DEV[l, r] >= C:
                stable = False
                break 

        if stable:
            return [float(edges[c]) for c in combo]

    return None



### The dp algorithm 

def algorithm4_independent_dp(
    # series: pd.Series,
    x_series: pd.Series,                 # <--- Changed
    y_series: Optional[pd.Series],
    L: float, U: float, step: float,
    k: int, epsilon: float, C: float,
    agg_func: str = 'COUNT',
    *,
    min_width: Optional[float] = None,
    max_width: Optional[float] = None,
    excluded_boundaries: Optional[List[float]] = None,
) -> Tuple[Optional[List[float]], Optional[int]]:
    s = int(np.floor(epsilon / step))
    # edges, pref = build_grid(series, L, U, step)
    DEV, edges = build_universal_DEV_2d(x_series, y_series, L, U, step, s, agg_func)
    m = len(edges) - 1
    # s = int(np.floor(epsilon / step))

    if s < 0 or k < 1 or k > m: return (None, None)

    min_cells = _min_width_to_cells(min_width, step)
    max_cells = _max_width_to_cells(max_width, step)
    excluded_idx = _boundary_values_to_indices(edges, excluded_boundaries, m)

    def boundary_allowed(j: int) -> bool:
        return excluded_idx is None or j not in excluded_idx

    # DEV = build_DEV_2d(pref, s)
    INF = int(DEV[m, m]) + 10**9

    # OPT[i, j] tracks the min-max error for partitioning [0, i) into j bins
    OPT = np.full((m + 1, k + 1), INF, dtype=int)
    parent = np.zeros((m + 1, k + 1), dtype=int)

    # Base case: j = 1 (Using exactly 1 bin from 0 to i)
    for i in range(1, m + 1):
        OPT[i, 1] = DEV[0, i]

    # DP Formula for j > 1
    for j in range(2, k + 1):
        for i in range(j, m + 1):
            
            lo = j - 1
            hi = i - 1
            if min_cells is not None: lo = max(lo, i - max_cells if max_cells else lo)
            if max_cells is not None: hi = min(hi, i - min_cells)

            best_val = INF
            best_l = -1

            for l in range(lo, hi + 1):
                if not boundary_allowed(l): continue
                if OPT[l, j - 1] == INF or DEV[l, i] == INF: continue
                
                # The core minimax formula from the paper
                val = max(OPT[l, j - 1], DEV[l, i])
                
                if val < best_val:
                    best_val = val
                    best_l = l
            
            OPT[i, j] = best_val
            parent[i, j] = best_l

    best_T = OPT[m, k]
    if best_T >= C or best_T == INF:
        return (None, None if best_T == INF else int(best_T))

    # Trace back the pointers to recover the boundaries
    cuts_idx = []
    curr = m
    for j in range(k, 1, -1):
        curr = parent[curr, j]
        cuts_idx.append(curr)

    cuts_idx.reverse()
    return ([float(edges[c]) for c in cuts_idx], int(best_T))





###The filtered graph algorithm


def algorithm5_independent_graph(
    # series: pd.Series,
    x_series: pd.Series,                 # <--- Changed
    y_series: Optional[pd.Series],
    L: float, U: float, step: float,
    k: int, epsilon: float, C: float,
    agg_func: str = 'COUNT', 
    *,
    use_boundary_prefilter: bool = True,
    min_width: Optional[float] = None,
    max_width: Optional[float] = None,
    excluded_boundaries: Optional[List[float]] = None,
    required_boundaries: Optional[List[float]] = None,
) -> Optional[List[float]]:
    s = int(np.floor(epsilon / step))
    # edges, pref = build_grid(series, L, U, step)
    DEV, edges = build_universal_DEV_2d(x_series, y_series, L, U, step, s, agg_func)
    m = len(edges) - 1
    # s = int(np.floor(epsilon / step))

    if s < 0 or k < 1 or k > m: return None

    min_cells = _min_width_to_cells(min_width, step)
    max_cells = _max_width_to_cells(max_width, step)
    
    excluded_idx = _boundary_values_to_indices(edges, excluded_boundaries, m)
    required_idx = _boundary_values_to_indices(edges, required_boundaries, m)
    if required_idx is None: required_idx = set()
    if len(required_idx) > k - 1 or (excluded_idx and required_idx.intersection(excluded_idx)):
        return None

    required_list = sorted(required_idx)
    req_to_bit = {r: i for i, r in enumerate(required_list)}
    full_required_mask = (1 << len(required_list)) - 1

    # DEV = build_DEV_2d(pref, s)
    INF = int(DEV[m, m]) + 10**9

    def boundary_allowed(j: int) -> bool:
        return excluded_idx is None or j not in excluded_idx

    # Pre-filtering based strictly on the 2D DEV matrix
    if use_boundary_prefilter:
        cand_interval = (DEV < C) & (DEV < INF)
        P = [0, m]
        for j in range(1, m):
            if not boundary_allowed(j): continue
            if cand_interval[:j, j].any() and cand_interval[j, j + 1:].any():
                P.append(j)
        P = np.array(sorted(set(P)), dtype=int)

        def iter_boundaries(i: int, bins_left: int):
            lo = i + (min_cells or 1)
            hi = m - (bins_left - 1) * (min_cells or 1)
            if max_cells is not None: hi = min(hi, i + max_cells)
            for j in P[(P >= lo) & (P <= hi)]:
                yield int(j)
    else:
        def iter_boundaries(i: int, bins_left: int):
            lo = i + (min_cells or 1)
            hi = m - (bins_left - 1) * (min_cells or 1)
            if max_cells is not None: hi = min(hi, i + max_cells)
            for j in range(lo, hi + 1):
                if boundary_allowed(j): yield j

    # Simplified DFS: No more tracking edge states!
    @lru_cache(maxsize=None)
    def dfs(i: int, bins_left: int, req_mask: int) -> Optional[Tuple[int, ...]]:
        missing_required = len(required_list) - bin(req_mask).count("1")
        if missing_required > bins_left - 1: return None

        if bins_left == 1:
            if req_mask != full_required_mask: return None
            last_w = m - i
            if min_cells is not None and last_w < min_cells: return None
            if max_cells is not None and last_w > max_cells: return None

            if DEV[i, m] < C:
                return (i, m)
            return None

        for j in iter_boundaries(i, bins_left):
            # A simple 2D lookup is all we need now
            if DEV[i, j] >= C:
                continue

            new_mask = req_mask | (1 << req_to_bit[j]) if j in req_to_bit else req_mask
            
            tail = dfs(j, bins_left - 1, new_mask)
            if tail is not None:
                return (i,) + tail

        return None

    path = dfs(0, k, 0)
    
    if path is None: return None
    bnds = list(path)
    if bnds[0] != 0: bnds = [0] + bnds
    cuts_idx = bnds[1:-1]
    
    if required_idx and not required_idx.issubset(set(cuts_idx)): return None
    return [float(edges[c]) for c in cuts_idx]
