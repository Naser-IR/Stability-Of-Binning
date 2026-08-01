# # from functools import lru_cache
# # from typing import Optional, List, Tuple
# # import numpy as np
# # import pandas as pd




# # def build_grid(series: pd.Series, L: float, U: float, step: float) -> Tuple[np.ndarray, np.ndarray]:
# #     """
# #     Build the base grid and prefix counts.
# #     - Grid cells are half-open: [edges[i], edges[i+1]).
# #     - Returns:
# #         edges: float array of length m+1
# #         pref : int prefix counts of length m+1, where pref[i] = sum(counts[:i])
# #     """
# #     if step <= 0:
# #         raise ValueError("step must be > 0")
# #     if U <= L:
# #         raise ValueError("U must be > L")

# #     vals = pd.to_numeric(series, errors="coerce").dropna().to_numpy()

# #     # Build edges to cover [L, U) in steps of `step` (ensure U is included as the final edge)
# #     m = int(np.ceil((U - L) / step))
# #     edges = (L + step * np.arange(m + 1)).astype(float)
# #     if edges[-1] < U - 1e-12:  # ensure last edge reaches/exceeds U
# #         edges = np.append(edges, edges[-1] + step)
# #         m = len(edges) - 1

# #     # Histogram on this grid (np.histogram is half-open except the rightmost bin)
# #     counts, _ = np.histogram(vals, bins=edges)
# #     # Prefix: pref[i] = sum(counts[:i])
# #     pref = np.zeros(m + 1, dtype=int)
# #     pref[1:] = np.cumsum(counts, dtype=int)
# #     return edges, pref

# # def count_interval(pref: np.ndarray, l: int, r: int) -> int:
# #     """
# #     Count elements in grid cells [l, r) using prefix sums.
# #     Clamps to valid range; returns 0 if r <= l.
# #     """
# #     m = len(pref) - 1
# #     l = max(0, min(m, l))
# #     r = max(0, min(m, r))
# #     if r <= l:
# #         return 0
# #     return int(pref[r] - pref[l])



# # #precompute worst-case bin deviations under shifts

# # def build_E_4d(pref: np.ndarray, s: int) -> np.ndarray:
# #     """
# #     E[l, r, dL_idx, dR_idx] for half-open [l, r) with integer shifts dL, dR ∈ [-s..s].
# #     INVALID shifted intervals are set to INF so downstream algorithms can ignore them.

# #     Validity (edge-consistent outer edges):
# #       • First bin  (l == 0):     dL must be 0; 0 < r + dR <= m; and (l+dL) < (r+dR).
# #       • Last bin   (r == m):     dR must be 0; 0 <= l + dL < m; and (l+dL) < (r+dR).
# #       • Internal   (0<l and r<m): 0 < l + dL < m, 0 < r + dR < m; and (l+dL) < (r+dR).

# #     NOTE: No clamping here. Invalid cases are left as INF.
# #     """
# #     m = len(pref) - 1
# #     INF = int(pref[m]) + 10**9  # large sentinel
# #     E = np.full((m + 1, m + 1, 2 * s + 1, 2 * s + 1), INF, dtype=int)

# #     def cnt(a: int, b: int) -> int:
# #         # caller guarantees 0 <= a < b <= m
# #         return int(pref[b] - pref[a])

# #     for l in range(0, m):
# #         for r in range(l + 1, m + 1):
# #             base = cnt(l, r)

# #             for dL in range(-s, s + 1):
# #                 for dR in range(-s, s + 1):
# #                     Ls = l + dL
# #                     Rs = r + dR

# #                     valid = True
# #                     if l == 0:
# #                         if dL != 0: valid = False
# #                         if not (0 < Rs <= m): valid = False
# #                     elif r == m:
# #                         if dR != 0: valid = False
# #                         if not (0 <= Ls < m): valid = False
# #                     else:
# #                         if not (0 < Ls < m): valid = False
# #                         if not (0 < Rs < m): valid = False

# #                     if not (Ls < Rs): valid = False
# #                     if not valid:
# #                         continue

# #                     shifted = cnt(Ls, Rs)
# #                     E[l, r, dL + s, dR + s] = abs(base - shifted)
# #     return E






# # # ──────────────────────────────────────────────────────────────────────────────
# # # Algorithm 2 — Naive exhaustive search (edge-consistent)
# # # ──────────────────────────────────────────────────────────────────────────────

# # def algorithm2_edge_consistent_naive(
# #     series: pd.Series,
# #     L: float, U: float, step: float,
# #     k: int, epsilon: float, C: float,
# #     *,
# #     candidate_stride: int = 1,
# #     max_combinations: Optional[int] = None,
# # ) -> Optional[List[float]]:
# #     """
# #     Find any ε-stable k-bin partition by enumerating all (k−1)-cut combinations.
# #     The stability check enforces *edge consistency*:
# #       the right-edge shift of bin t equals the left-edge shift of bin t+1.

# #     Conventions
# #     -----------
# #     • Bins are half-open on the base grid: [l, r) with integer cell indices.
# #     • Integer shift radius: s = floor(epsilon / step).
# #     • Strict threshold: deviation < C for *all* allowed shared-edge shifts.

# #     Returns
# #     -------
# #     list[float] | None
# #         Real cut positions if a stable partition is found, else None.
# #     """
# #     # Build histogram grid and prefix sums
# #     edges, pref = build_grid(series, L, U, step)
# #     m = len(edges) - 1
# #     s = int(np.floor(epsilon / step))
# #     if s < 0 or k < 1 or k > m:
# #         return None

# #     # Candidate internal boundaries (grid indices)
# #     from itertools import combinations, product
# #     candidates = list(range(1, m, candidate_stride))

# #     tested = 0
# #     for combo in combinations(candidates, k - 1):
# #         if max_combinations is not None and tested >= max_combinations:
# #             break
# #         tested += 1

# #         # Boundaries (indices): [0, c1, c2, ..., m]
# #         bounds = (0, *combo, m)

# #         # Precompute base bin counts once (O(k))
# #         base_counts = []
# #         ok = True
# #         for a, b in zip(bounds[:-1], bounds[1:]):
# #             if a >= b:
# #                 ok = False
# #                 break
# #             base_counts.append(int(pref[b] - pref[a]))
# #         if not ok:
# #             continue

# #         # Enumerate *edge-consistent* internal shifts δ_1..δ_{k-1} ∈ [-s..s]
# #         # Outer edges fixed at δ_0 = δ_k = 0. Also enforce shifted boundaries stay
# #         # inside (0, m) and remain strictly increasing.
# #         stable = True
# #         for deltas in product(range(-s, s + 1), repeat=k - 1):
# #             shifted = [0]  # δ_0
# #             shifted += list(deltas)
# #             shifted += [0]  # δ_k

# #             # Check monotone increasing and in-range for interior boundaries
# #             prev = 0
# #             valid = True
# #             for t, c in enumerate(bounds[1:-1], start=1):  # interior cuts only
# #                 x = c + shifted[t]
# #                 if not (0 < x < m) or x <= prev:
# #                     valid = False
# #                     break
# #                 prev = x
# #             if not valid:
# #                 # This δ-assignment is not admissible; skip.
# #                 continue

# #             # Compute worst per-bin deviation under this δ-assignment
# #             worst = 0
# #             for t in range(k):
# #                 l = bounds[t] + shifted[t]
# #                 r = bounds[t + 1] + shifted[t + 1]
# #                 # clamp in case of edge touch (defensive)
# #                 l = max(0, min(m, l))
# #                 r = max(0, min(m, r))
# #                 shifted_cnt = 0 if r <= l else int(pref[r] - pref[l])
# #                 dev = abs(base_counts[t] - shifted_cnt)
# #                 if dev > worst:
# #                     worst = dev
# #                     if worst >= C:
# #                         break

# #             if worst >= C:
# #                 # Found an adversarial δ making partition unstable
# #                 stable = False
# #                 break

# #         if stable:
# #             # Convert grid indices to real cut values
# #             return [float(edges[c]) for c in combo]

# #     return None


# # # ──────────────────────────────────────────────────────────────────────────────
# # # Algorithm 4 — DP minimax with parametric search (edge-consistent)
# # # ──────────────────────────────────────────────────────────────────────────────

# # def algorithm4_edge_consistent_dp(
# #     series: pd.Series,
# #     L: float, U: float, step: float,
# #     k: int, epsilon: float, C: float
# # ) -> Tuple[Optional[List[float]], Optional[int]]:
# #     """
# #     Algorithm 4 (final): edge-consistent minimax via feasibility DP + binary search.

# #     Universal adversary (∀) on VALID shifts only:
# #       • FIRST[i]    = max_{valid dR}                 E[0, i, s, dR]
# #       • INTERNAL[x,i] = max_{valid dL, valid dR}     E[x, i, dL, dR]      for 0 < x < i < m
# #       • LAST[x]     = max_{valid dL}                 E[x, m, dL, s]
# #     A partition is feasible at threshold T iff there exists a chain of k bins whose
# #     FIRST/INTERNAL/LAST values are all ≤ T. We binary-search the smallest such T (minimax).
# #     If best_worst ≥ C (STRICT model), we return (None, best_worst).
# #     """
# #     # Grid & params
# #     edges, pref = build_grid(series, L, U, step)
# #     m = len(edges) - 1
# #     s = int(np.floor(epsilon / step))
# #     if s < 0 or k < 1 or k > m:
# #         return (None, None)

# #     # 4-D deviations with INF on invalid (must use the corrected build_E_4d)
# #     E = build_E_4d(pref, s).astype(int)
# #     INF = int(pref[m]) + 10**9

# #     # ---- Collapse to universal worst-cases over VALID shifts only ----
# #     # FIRST: max over valid dR for first bin [0,i)
# #     first_blk = E[0, :, s, :]                 # shape (m+1, 2s+1)
# #     first_valid = first_blk < INF
# #     FIRST = np.full(m + 1, INF, dtype=int)
# #     rows = first_valid.any(axis=1)
# #     if np.any(rows):
# #         FIRST[rows] = np.where(first_valid[rows], first_blk[rows], -1).max(axis=1)
# #         FIRST[FIRST < 0] = INF  # rows with no valid entries stay INF

# #     # INTERNAL: max over valid (dL, dR) for [x,i)
# #     masked = np.where(E < INF, E, -1)         # invalid → -1 so max ignores them
# #     INTERNAL_ALL = masked.max(axis=(2, 3))    # shape (m+1, m+1)
# #     HAS_VALID = (E < INF).any(axis=(2, 3))
# #     INTERNAL = np.full_like(INTERNAL_ALL, INF)
# #     INTERNAL[HAS_VALID] = INTERNAL_ALL[HAS_VALID]
# #     # Invalidate first/last-bin positions
# #     INTERNAL[0, :] = INF
# #     INTERNAL[:, m] = INF

# #     # LAST: max over valid dL for last bin [x,m)
# #     last_blk = E[:, m, :, s]                  # shape (m+1, 2s+1)
# #     last_valid = last_blk < INF
# #     LAST = np.full(m + 1, INF, dtype=int)
# #     rows = last_valid.any(axis=1)
# #     if np.any(rows):
# #         LAST[rows] = np.where(last_valid[rows], last_blk[rows], -1).max(axis=1)
# #         LAST[LAST < 0] = INF

# #     # Candidate thresholds (exact search set)
# #     uniq = np.unique(E[E < INF])              # exclude INF; sort ascending by np.unique

# #     def feasible_at(T: int) -> Tuple[bool, Optional[List[int]]]:
# #         """
# #         DP over prefixes with j bins:
# #           G[i,1]   = (FIRST[i]   ≤ T)
# #           G[i,j]   = ∃ x∈[j-1..i-1]: G[x,j-1] ∧ (INTERNAL[x,i] ≤ T)   for 2 ≤ j ≤ k-1
# #           Final ok = ∃ x∈[k-1..m-1]: G[x,k-1] ∧ (LAST[x] ≤ T)
# #         """
# #         G = np.zeros((m + 1, k), dtype=bool)     # j ∈ 1..k → index j-1
# #         back = -np.ones((m + 1, k), dtype=int)

# #         # Base layer: j = 1
# #         for i in range(1, m + 1):
# #             if FIRST[i] <= T:
# #                 G[i, 0] = True
# #                 back[i, 0] = 0

# #         # Internal layers: j = 2..k-1, close at i < m (leave one bin for the end)
# #         for j in range(2, k):
# #             jj = j - 1
# #             for i in range(j, m):
# #                 # need a split x with previous feasible and INTERNAL[x,i] ≤ T
# #                 # (INTERNAL is already universal over valid (dL,dR))
# #                 xs = range(j - 1, i)
# #                 for x in xs:
# #                     if G[x, jj - 1] and INTERNAL[x, i] <= T:
# #                         G[i, jj] = True
# #                         back[i, jj] = x
# #                         break

# #         # Final bin: [x, m), universal over valid dL already collapsed in LAST
# #         best_x = -1
# #         for x in range(k - 1, m):
# #             if G[x, k - 2] and LAST[x] <= T:
# #                 best_x = x
# #                 break
# #         if best_x < 0:
# #             return (False, None)

# #         # Backtrack k-1 cuts: b1..b_{k-1}
# #         cuts_idx: List[int] = []
# #         i = best_x
# #         for j in range(k - 1, 0, -1):
# #             cuts_idx.append(i)
# #             i = back[i, j - 1]
# #         cuts_idx.reverse()
# #         return (True, cuts_idx)

# #     # Binary search minimax T*
# #     if uniq.size == 0:
# #         return (None, None)
# #     lo, hi = 0, len(uniq) - 1
# #     best_T, best_cuts = None, None
# #     while lo <= hi:
# #         mid = (lo + hi) // 2
# #         T = int(uniq[mid])
# #         ok, cuts = feasible_at(T)
# #         if ok:
# #             best_T, best_cuts = T, cuts
# #             hi = mid - 1
# #         else:
# #             lo = mid + 1

# #     if best_T is None or best_cuts is None:
# #         return (None, None)

# #     # Feasibility semantics: return None if it doesn't meet C (STRICT)
# #     if best_T >= C:
# #         return (None, int(best_T))

# #     return ([float(edges[c]) for c in best_cuts], int(best_T))



# # def algorithm44_edge_consistent_dp(
# #     series: pd.Series,
# #     L: float, U: float, step: float,
# #     k: int, epsilon: float, C: float
# # ) -> Tuple[Optional[List[float]], Optional[int]]:
# #     """
# #     Algorithm 4 — Edge-consistent minimax with universal adversary
# #     via parametric feasibility (binary search on T) + memoized DFS DP.

# #     Exact semantics (matches Alg-2 and Alg-5 EC):
# #       • Bins are half-open [l, r). Outer edges have 0 shift (index s = floor(eps/step)).
# #       • At each shared edge, the adversary may choose ANY VALID right-shift (dR).
# #       • For a partition to be feasible at threshold T, it must hold that:
# #           - For EVERY valid dR at EVERY internal edge, the current bin deviation ≤ T,
# #           - and the remainder (suffix) is also feasible when that dR becomes the next bin’s left shift.
# #       • Invalid (dL, dR) pairs are ignored (E == INF).

# #     Returns
# #     -------
# #     (cuts_real, best_worst):
# #       cuts_real  : list of real cut positions (len = k-1) if best_worst < C; else None
# #       best_worst : minimized worst-case deviation T* (int), or None if no valid entries
# #     """
# #     # Build grid/tables
# #     edges, pref = build_grid(series, L, U, step)
# #     m = len(edges) - 1
# #     s = int(np.floor(epsilon / step))
# #     if s < 0 or k < 1 or k > m:
# #         return (None, None)

# #     # E[l, r, dL_idx, dR_idx] with invalid entries set to INF by your build_E_4d
# #     E = build_E_4d(pref, s).astype(int)
# #     INF = int(pref[m]) + 10**9

# #     # Candidate thresholds (exclude INF)
# #     uniq = np.unique(E[E < INF])
# #     if uniq.size == 0:
# #         return (None, None)

# #     from functools import lru_cache

# #     def feasible_at(T: int) -> Tuple[bool, Optional[List[int]]]:
# #         """
# #         Decide if there exists a k-bin partition with universal-adversary deviation ≤ T.
# #         Uses a memoized DFS DP on states (i, t, dL_idx):
# #           - i: current left boundary (grid index)
# #           - t: bins left to place
# #           - dL_idx: index of the current bin’s left-edge shift (prev shared edge)
# #         Universal quantifier is enforced over **valid** right-shifts only,
# #         and we require extension (suffix feasibility) for EACH such right-shift.
# #         """
# #         back_choice: Dict[Tuple[int, int, int], int] = {}  # (i,t,dL) -> chosen j for reconstruction

# #         @lru_cache(maxsize=None)
# #         def dp(i: int, t: int, dL_idx: int) -> bool:
# #             # Last bin must end at m; right outer edge fixed to 0 shift (index s)
# #             if t == 1:
# #                 val = E[i, m, dL_idx, s]
# #                 return (val < INF) and (val <= T) and (i < m)

# #             # Choose next boundary j; leave room for remaining (t-1) bins
# #             lo = i + 1
# #             hi = m - (t - 1)
# #             for j in range(lo, hi + 1):
# #                 row = E[i, j, dL_idx, :]                 # all right-shifts for this bin
# #                 valid_mask = row < INF                   # only VALID dR choices
# #                 if not np.any(valid_mask):
# #                     continue
# #                 # universal over valid dR: current bin must be safe for ALL valid dR
# #                 if np.any(row[valid_mask] > T):
# #                     continue
# #                 # and EACH valid dR must allow a feasible suffix
# #                 ok = True
# #                 for dR_idx in np.flatnonzero(valid_mask):
# #                     if not dp(j, t - 1, int(dR_idx)):
# #                         ok = False
# #                         break
# #                 if ok:
# #                     back_choice[(i, t, dL_idx)] = j
# #                     return True
# #             return False

# #         ok = dp(0, k, s)
# #         if not ok:
# #             return (False, None)

# #         # Reconstruct cuts: universal condition guarantees any valid dR works;
# #         # to walk the path we pick any valid one that satisfies the dp recurrence.
# #         cuts_idx: List[int] = []
# #         i, t, dL_idx = 0, k, s
# #         while t > 1:
# #             j = back_choice[(i, t, dL_idx)]
# #             cuts_idx.append(j)
# #             # pick any valid dR that advances
# #             row = E[i, j, dL_idx, :]
# #             valid_mask = row < INF
# #             # all valid dR work by definition; choose the first for the walk
# #             next_dR = int(np.flatnonzero(valid_mask)[0])
# #             i, t, dL_idx = j, t - 1, next_dR

# #         cuts_idx = cuts_idx[:-1]  # drop the terminal m we appended via j
# #         # Ensure exactly k-1 internal boundaries
# #         cuts_idx = cuts_idx[:k-1]
# #         return (True, cuts_idx)

# #     # Binary search minimized worst-case T*
# #     lo, hi = 0, len(uniq) - 1
# #     best_T: Optional[int] = None
# #     best_cuts_idx: Optional[List[int]] = None
# #     while lo <= hi:
# #         mid = (lo + hi) // 2
# #         T = int(uniq[mid])
# #         ok, cuts_idx = feasible_at(T)
# #         if ok:
# #             best_T, best_cuts_idx = T, cuts_idx
# #             hi = mid - 1
# #         else:
# #             lo = mid + 1

# #     if best_T is None or best_cuts_idx is None:
# #         return (None, None)

# #     # Feasibility semantics: return None if it doesn't meet C (strict < C)
# #     if best_T >= C:
# #         return (None, int(best_T))

# #     return ([float(edges[c]) for c in best_cuts_idx], int(best_T))





# # # ──────────────────────────────────────────────────────────────────────────────
# # # Algorithm 5 — Sliding window / graph search
# # #   Two variants:
# # #     (A) independent feasibility (fast heuristic) with optional pre-filter,
# # #     (B) edge-consistent DFS (recommended) with boundary pre-filter.
# # # ──────────────────────────────────────────────────────────────────────────────


# # def algorithm5_graph_independent(
# #     series: pd.Series,
# #     L: float, U: float, step: float,
# #     k: int, epsilon: float, C: float,
# #     *,
# #     use_boundary_prefilter: bool = True,
# # ) -> Optional[List[float]]:
# #     """
# #     Alg-5 (indep): graph search with independent per-bin feasibility.
# #     • Heuristic: ignores shared-edge coupling (may false-negative/positive vs. EC).
# #     • Uses the worst-case per-bin deviation over all **valid** (dL,dR).
# #     """
# #     edges, pref = build_grid(series, L, U, step)
# #     m = len(edges) - 1
# #     s = int(np.floor(epsilon / step))
# #     if s < 0 or k < 1 or k > m:
# #         return None

# #     E = build_E_4d(pref, s).astype(int)
# #     INF = int(pref[m]) + 10**9

# #     # Per-interval worst deviation over VALID shifts only
# #     # If an interval has no valid shift pair, its err is INF (so it won't be used).
# #     valid_mask = E < INF
# #     with np.errstate(all='ignore'):
# #         masked = np.where(valid_mask, E, -1)           # -1 so max ignores invalid
# #         err_indep = masked.max(axis=(2, 3)).astype(int)
# #         # if there were no valid entries, max=-1 → set to INF so it's infeasible
# #         err_indep[err_indep < 0] = INF

# #     feasible = (err_indep < C)  # strict

# #     # Boundary pre-filter P: interval has at least one VALID pair with E < C
# #     if use_boundary_prefilter:
# #         cand_interval = np.any((E < C) & valid_mask, axis=(2, 3))
# #         P = [0, m]
# #         for j in range(1, m):
# #             if cand_interval[:j, j].any() and cand_interval[j, j + 1:].any():
# #                 P.append(j)
# #         P = np.array(sorted(set(P)), dtype=int)

# #         def iter_boundaries(i: int, bins_left: int):
# #             lo, hi = i + 1, m - (bins_left - 1)
# #             seg = P[(P >= lo) & (P <= hi)]
# #             for j in seg:
# #                 yield int(j)
# #     else:
# #         def iter_boundaries(i: int, bins_left: int):
# #             lo, hi = i + 1, m - (bins_left - 1)
# #             for j in range(lo, hi + 1):
# #                 yield j

# #     @lru_cache(maxsize=None)
# #     def dfs(i: int, bins_left: int) -> Optional[Tuple[int, ...]]:
# #         if bins_left == 0:
# #             return (i,) if i == m else None
# #         for j in iter_boundaries(i, bins_left):
# #             if feasible[i, j]:
# #                 tail = dfs(j, bins_left - 1)
# #                 if tail is not None:
# #                     return (i,) + tail
# #         return None

# #     path = dfs(0, k)
# #     if path is None:
# #         return None

# #     cuts_idx = list(path)[1:-1]
# #     return [float(edges[c]) for c in cuts_idx]


# # def algorithm5_graph_edge_consistent(
# #     series: pd.Series,
# #     L: float, U: float, step: float,
# #     k: int, epsilon: float, C: float,
# #     *,
# #     use_boundary_prefilter: bool = True,
# #     min_width: Optional[float] = None,
# #     allowed_boundaries: Optional[List[float]] = None,
# #     required_boundaries: Optional[List[float]] = None,
# # ) -> Optional[List[float]]:
# #     """
# #     Algorithm 5 (edge-consistent, universal adversary) with:
# #       - optional minimum nominal bin width
# #       - optional restriction to specific allowed internal boundaries
# #       - optional requirement that specific boundaries must appear in the final cuts

# #     Parameters
# #     ----------
# #     allowed_boundaries : Optional[List[float]]
# #         If given, the algorithm may choose cuts ONLY from these boundary values.
# #         Values must lie exactly on the base grid.

# #     required_boundaries : Optional[List[float]]
# #         If given, the final cut set must INCLUDE these boundary values.
# #         Other cuts may be chosen freely unless `allowed_boundaries` is also given.

# #     min_width : Optional[float]
# #         Minimum nominal width of each bin, in the same units as `step`.
# #     """
# #     edges, pref = build_grid(series, L, U, step)
# #     m = len(edges) - 1
# #     s = int(np.floor(epsilon / step))
# #     if s < 0 or k < 1 or k > m:
# #         return None

# #     min_cells = None
# #     if min_width is not None:
# #         min_cells = int(np.ceil(min_width / step))
# #         if min_cells < 1:
# #             min_cells = 1
# #         if k * min_cells > m:
# #             return None

# #     E = build_E_4d(pref, s).astype(int)
# #     INF = int(pref[m]) + 10**9

# #     edge_to_idx = {float(edges[i]): i for i in range(len(edges))}

# #     # allowed boundaries: restrict all chosen cuts to this set
# #     allowed_idx = None
# #     if allowed_boundaries is not None:
# #         allowed_idx = set()
# #         for x in allowed_boundaries:
# #             xf = float(x)
# #             if xf not in edge_to_idx:
# #                 raise ValueError(
# #                     f"Boundary {x} is not on the grid. "
# #                     f"Allowed grid values are {list(edges)}"
# #                 )
# #             idx = edge_to_idx[xf]
# #             if idx == 0 or idx == m:
# #                 continue
# #             allowed_idx.add(idx)

# #         if len(allowed_idx) < (k - 1):
# #             return None

# #     # required boundaries: these must appear in final cuts
# #     required_idx = None
# #     if required_boundaries is not None:
# #         required_idx = set()
# #         for x in required_boundaries:
# #             xf = float(x)
# #             if xf not in edge_to_idx:
# #                 raise ValueError(
# #                     f"Boundary {x} is not on the grid. "
# #                     f"Allowed grid values are {list(edges)}"
# #                 )
# #             idx = edge_to_idx[xf]
# #             if idx == 0 or idx == m:
# #                 continue
# #             required_idx.add(idx)

# #         if len(required_idx) > (k - 1):
# #             return None

# #         if allowed_idx is not None and not required_idx.issubset(allowed_idx):
# #             return None

# #     if use_boundary_prefilter:
# #         cand_interval = np.any((E < C) & (E < INF), axis=(2, 3))
# #         P = [0, m]
# #         for j in range(1, m):
# #             if cand_interval[:j, j].any() and cand_interval[j, j + 1:].any():
# #                 P.append(j)
# #         P = np.array(sorted(set(P)), dtype=int)

# #         def iter_boundaries(i: int, bins_left: int):
# #             lo = i + (min_cells or 1)
# #             hi = m - (bins_left - 1) * (min_cells or 1)
# #             seg = P[(P >= lo) & (P <= hi)]
# #             for j in seg:
# #                 j = int(j)
# #                 if allowed_idx is not None and j not in allowed_idx:
# #                     continue
# #                 yield j
# #     else:
# #         def iter_boundaries(i: int, bins_left: int):
# #             lo = i + (min_cells or 1)
# #             hi = m - (bins_left - 1) * (min_cells or 1)
# #             for j in range(lo, hi + 1):
# #                 if allowed_idx is not None and j not in allowed_idx:
# #                     continue
# #                 yield j

# #     @lru_cache(maxsize=None)
# #     def dfs(i: int, bins_left: int, prev_dR_idx: int) -> Optional[Tuple[int, ...]]:
# #         dL_idx = prev_dR_idx if i > 0 else s

# #         if bins_left == 1:
# #             if min_cells is not None and (m - i) < min_cells:
# #                 return None
# #             val = E[i, m, dL_idx, s]
# #             if val < C:
# #                 return (i, m)
# #             return None

# #         for j in iter_boundaries(i, bins_left):
# #             if min_cells is not None and (j - i) < min_cells:
# #                 continue

# #             row = E[i, j, dL_idx, :]
# #             valid_mask = row < INF
# #             if not np.any(valid_mask):
# #                 continue

# #             if np.any(row[valid_mask] >= C):
# #                 continue

# #             ok = True
# #             tail_any = None
# #             for dR_idx in np.flatnonzero(valid_mask):
# #                 tail = dfs(j, bins_left - 1, int(dR_idx))
# #                 if tail is None:
# #                     ok = False
# #                     break
# #                 tail_any = tail

# #             if ok:
# #                 candidate = (i,) + tail_any
# #                 cuts_idx = set(candidate[1:-1])

# #                 if required_idx is not None and not required_idx.issubset(cuts_idx):
# #                     continue

# #                 return candidate

# #         return None

# #     path = dfs(0, k, s)
# #     if path is None:
# #         return None

# #     bnds = list(path)
# #     if bnds[0] != 0:
# #         bnds = [0] + bnds
# #     cuts_idx = bnds[1:-1]
# #     return [float(edges[c]) for c in cuts_idx]





# from functools import lru_cache
# from typing import Optional, List, Tuple, Dict
# import numpy as np
# import pandas as pd


# # ============================================================
# # Helpers
# # ============================================================

# def build_grid(series: pd.Series, L: float, U: float, step: float) -> Tuple[np.ndarray, np.ndarray]:
#     if step <= 0:
#         raise ValueError("step must be > 0")
#     if U <= L:
#         raise ValueError("U must be > L")

#     vals = pd.to_numeric(series, errors="coerce").dropna().to_numpy()

#     m = int(np.ceil((U - L) / step))
#     edges = (L + step * np.arange(m + 1)).astype(float)

#     counts, _ = np.histogram(vals, bins=edges)

#     pref = np.zeros(m + 1, dtype=int)
#     pref[1:] = np.cumsum(counts, dtype=int)

#     return edges, pref


# def _boundary_values_to_indices(edges: np.ndarray, values, m: int) -> Optional[set]:
#     """
#     Convert boundary values like [6.0, 12.0] to grid indices.
#     Ignores L and U because they are outer boundaries, not internal cuts.
#     """
#     if values is None:
#         return None

#     edge_to_idx = {round(float(edges[i]), 12): i for i in range(len(edges))}
#     out = set()

#     for x in values:
#         xf = round(float(x), 12)
#         if xf not in edge_to_idx:
#             raise ValueError(f"Boundary {x} is not on the grid. Grid values are {list(edges)}")

#         idx = edge_to_idx[xf]
#         if idx == 0 or idx == m:
#             continue

#         out.add(idx)

#     return out


# def _min_width_to_cells(min_width: Optional[float], step: float) -> Optional[int]:
#     if min_width is None:
#         return None
#     cells = int(np.ceil(min_width / step))
#     return max(1, cells)


# def build_E_4d(pref: np.ndarray, s: int) -> np.ndarray:
#     """
#     E[l,r,dL,dR] stores count deviation between [l,r) and shifted interval.
#     Invalid shifted intervals are INF.
#     """
#     m = len(pref) - 1
#     INF = int(pref[m]) + 10**9
#     E = np.full((m + 1, m + 1, 2 * s + 1, 2 * s + 1), INF, dtype=int)

#     def cnt(a: int, b: int) -> int:
#         return int(pref[b] - pref[a])

#     for l in range(0, m):
#         for r in range(l + 1, m + 1):
#             base = cnt(l, r)

#             for dL in range(-s, s + 1):
#                 for dR in range(-s, s + 1):
#                     Ls = l + dL
#                     Rs = r + dR

#                     valid = True

#                     if l == 0:
#                         if dL != 0:
#                             valid = False
#                         if not (0 < Rs <= m):
#                             valid = False
#                     elif r == m:
#                         if dR != 0:
#                             valid = False
#                         if not (0 <= Ls < m):
#                             valid = False
#                     else:
#                         if not (0 < Ls < m):
#                             valid = False
#                         if not (0 < Rs < m):
#                             valid = False

#                     if not (Ls < Rs):
#                         valid = False

#                     if not valid:
#                         continue

#                     shifted = cnt(Ls, Rs)
#                     E[l, r, dL + s, dR + s] = abs(base - shifted)

#     return E


# # ============================================================
# # Algorithm 2 — Naive exhaustive
# # ============================================================

# def algorithm2_edge_consistent_naive(
#     series: pd.Series,
#     L: float, U: float, step: float,
#     k: int, epsilon: float, C: float,
#     *,
#     candidate_stride: int = 1,
#     max_combinations: Optional[int] = None,
#     min_width: Optional[float] = None,
#     excluded_boundaries: Optional[List[float]] = None,
# ) -> Optional[List[float]]:

#     edges, pref = build_grid(series, L, U, step)
#     m = len(edges) - 1
#     s = int(np.floor(epsilon / step))

#     if s < 0 or k < 1 or k > m:
#         return None

#     min_cells = _min_width_to_cells(min_width, step)
#     if min_cells is not None and k * min_cells > m:
#         return None

#     excluded_idx = _boundary_values_to_indices(edges, excluded_boundaries, m)

#     from itertools import combinations, product

#     candidates = list(range(1, m, candidate_stride))

#     tested = 0
#     for combo in combinations(candidates, k - 1):
#         if max_combinations is not None and tested >= max_combinations:
#             break
#         tested += 1

#         if excluded_idx is not None and any(c in excluded_idx for c in combo):
#             continue

#         bounds = (0, *combo, m)

#         if min_cells is not None:
#             if any((b - a) < min_cells for a, b in zip(bounds[:-1], bounds[1:])):
#                 continue

#         base_counts = []
#         ok = True
#         for a, b in zip(bounds[:-1], bounds[1:]):
#             if a >= b:
#                 ok = False
#                 break
#             base_counts.append(int(pref[b] - pref[a]))

#         if not ok:
#             continue

#         stable = True

#         for deltas in product(range(-s, s + 1), repeat=k - 1):
#             shifted = [0] + list(deltas) + [0]

#             prev = 0
#             valid = True
#             for t, c in enumerate(bounds[1:-1], start=1):
#                 x = c + shifted[t]
#                 if not (0 < x < m) or x <= prev:
#                     valid = False
#                     break
#                 prev = x

#             if not valid:
#                 continue

#             worst = 0
#             for t in range(k):
#                 l = bounds[t] + shifted[t]
#                 r = bounds[t + 1] + shifted[t + 1]

#                 if r <= l:
#                     valid = False
#                     break

#                 shifted_cnt = int(pref[r] - pref[l])
#                 dev = abs(base_counts[t] - shifted_cnt)

#                 if dev > worst:
#                     worst = dev
#                     if worst >= C:
#                         break

#             if (not valid) or worst >= C:
#                 stable = False
#                 break

#         if stable:
#             return [float(edges[c]) for c in combo]

#     return None


# # ============================================================
# # Algorithm 4 — DP / minimax
# # ============================================================

# def algorithm4_edge_consistent_dp(
#     series: pd.Series,
#     L: float, U: float, step: float,
#     k: int, epsilon: float, C: float,
#     *,
#     min_width: Optional[float] = None,
#     excluded_boundaries: Optional[List[float]] = None,
# ) -> Tuple[Optional[List[float]], Optional[int]]:

#     edges, pref = build_grid(series, L, U, step)
#     m = len(edges) - 1
#     s = int(np.floor(epsilon / step))

#     if s < 0 or k < 1 or k > m:
#         return (None, None)

#     min_cells = _min_width_to_cells(min_width, step)
#     if min_cells is not None and k * min_cells > m:
#         return (None, None)

#     excluded_idx = _boundary_values_to_indices(edges, excluded_boundaries, m)

#     E = build_E_4d(pref, s).astype(int)
#     INF = int(pref[m]) + 10**9

#     uniq = np.unique(E[E < INF])
#     if uniq.size == 0:
#         return (None, None)

#     def boundary_allowed(j: int) -> bool:
#         return excluded_idx is None or j not in excluded_idx

#     def feasible_at(T: int) -> Tuple[bool, Optional[List[int]]]:
#         back_choice: Dict[Tuple[int, int, int], int] = {}

#         @lru_cache(maxsize=None)
#         def dp(i: int, bins_left: int, dL_idx: int) -> bool:
#             if bins_left == 1:
#                 if min_cells is not None and (m - i) < min_cells:
#                     return False
#                 val = E[i, m, dL_idx, s]
#                 return (val < INF) and (val <= T) and (i < m)

#             lo = i + (min_cells or 1)
#             hi = m - (bins_left - 1) * (min_cells or 1)

#             if lo > hi:
#                 return False

#             for j in range(lo, hi + 1):
#                 if not boundary_allowed(j):
#                     continue

#                 row = E[i, j, dL_idx, :]
#                 valid_mask = row < INF

#                 if not np.any(valid_mask):
#                     continue

#                 if np.any(row[valid_mask] > T):
#                     continue

#                 ok = True
#                 for dR_idx in np.flatnonzero(valid_mask):
#                     if not dp(j, bins_left - 1, int(dR_idx)):
#                         ok = False
#                         break

#                 if ok:
#                     back_choice[(i, bins_left, dL_idx)] = j
#                     return True

#             return False

#         ok = dp(0, k, s)
#         if not ok:
#             return (False, None)

#         cuts_idx: List[int] = []
#         i, bins_left, dL_idx = 0, k, s

#         while bins_left > 1:
#             j = back_choice[(i, bins_left, dL_idx)]
#             cuts_idx.append(j)

#             row = E[i, j, dL_idx, :]
#             valid_mask = row < INF

#             # Pick any valid shift that keeps the suffix feasible.
#             next_dR = None
#             for dR_idx in np.flatnonzero(valid_mask):
#                 if dp(j, bins_left - 1, int(dR_idx)):
#                     next_dR = int(dR_idx)
#                     break

#             if next_dR is None:
#                 return (False, None)

#             i, bins_left, dL_idx = j, bins_left - 1, next_dR

#         if len(cuts_idx) != k - 1:
#             return (False, None)

#         return (True, cuts_idx)

#     lo, hi = 0, len(uniq) - 1
#     best_T = None
#     best_cuts = None

#     while lo <= hi:
#         mid = (lo + hi) // 2
#         T = int(uniq[mid])

#         ok, cuts_idx = feasible_at(T)

#         if ok:
#             best_T = T
#             best_cuts = cuts_idx
#             hi = mid - 1
#         else:
#             lo = mid + 1

#     if best_T is None or best_cuts is None:
#         return (None, None)

#     if best_T >= C:
#         return (None, int(best_T))

#     return ([float(edges[c]) for c in best_cuts], int(best_T))


# # ============================================================
# # Algorithm 5 — Edge-consistent graph / DFS
# # ============================================================

# # def algorithm5_graph_edge_consistent(
# #     series: pd.Series,
# #     L: float, U: float, step: float,
# #     k: int, epsilon: float, C: float,
# #     *,
# #     use_boundary_prefilter: bool = True,
# #     min_width: Optional[float] = None,
# #     excluded_boundaries: Optional[List[float]] = None,
# #     required_boundaries: Optional[List[float]] = None,
# # ) -> Optional[List[float]]:

# #     edges, pref = build_grid(series, L, U, step)
# #     m = len(edges) - 1
# #     s = int(np.floor(epsilon / step))

# #     if s < 0 or k < 1 or k > m:
# #         return None

# #     min_cells = _min_width_to_cells(min_width, step)
# #     if min_cells is not None and k * min_cells > m:
# #         return None

# #     excluded_idx = _boundary_values_to_indices(edges, excluded_boundaries, m)
# #     required_idx = _boundary_values_to_indices(edges, required_boundaries, m)

# #     if required_idx is not None:
# #         if len(required_idx) > k - 1:
# #             return None
# #         if excluded_idx is not None and required_idx.intersection(excluded_idx):
# #             return None

# #     E = build_E_4d(pref, s).astype(int)
# #     INF = int(pref[m]) + 10**9

# #     def boundary_allowed(j: int) -> bool:
# #         if excluded_idx is not None and j in excluded_idx:
# #             return False
# #         return True

# #     if use_boundary_prefilter:
# #         cand_interval = np.any((E < C) & (E < INF), axis=(2, 3))
# #         P = [0, m]

# #         for j in range(1, m):
# #             if not boundary_allowed(j):
# #                 continue
# #             if cand_interval[:j, j].any() and cand_interval[j, j + 1:].any():
# #                 P.append(j)

# #         P = np.array(sorted(set(P)), dtype=int)

# #         def iter_boundaries(i: int, bins_left: int):
# #             lo = i + (min_cells or 1)
# #             hi = m - (bins_left - 1) * (min_cells or 1)
# #             seg = P[(P >= lo) & (P <= hi)]
# #             for j in seg:
# #                 yield int(j)

# #     else:
# #         def iter_boundaries(i: int, bins_left: int):
# #             lo = i + (min_cells or 1)
# #             hi = m - (bins_left - 1) * (min_cells or 1)
# #             for j in range(lo, hi + 1):
# #                 if boundary_allowed(j):
# #                     yield j

# #     @lru_cache(maxsize=None)
# #     def dfs(i: int, bins_left: int, prev_dR_idx: int) -> Optional[Tuple[int, ...]]:
# #         dL_idx = prev_dR_idx if i > 0 else s

# #         if bins_left == 1:
# #             if min_cells is not None and (m - i) < min_cells:
# #                 return None

# #             val = E[i, m, dL_idx, s]
# #             if val < C:
# #                 return (i, m)
# #             return None

# #         for j in iter_boundaries(i, bins_left):
# #             row = E[i, j, dL_idx, :]
# #             valid_mask = row < INF

# #             if not np.any(valid_mask):
# #                 continue

# #             if np.any(row[valid_mask] >= C):
# #                 continue

# #             ok = True
# #             tail_any = None

# #             for dR_idx in np.flatnonzero(valid_mask):
# #                 tail = dfs(j, bins_left - 1, int(dR_idx))
# #                 if tail is None:
# #                     ok = False
# #                     break
# #                 tail_any = tail

# #             if ok:
# #                 return (i,) + tail_any

# #         return None

# #     path = dfs(0, k, s)
# #     if path is None:
# #         return None

# #     bnds = list(path)
# #     if bnds[0] != 0:
# #         bnds = [0] + bnds

# #     cuts_idx = bnds[1:-1]

# #     if len(cuts_idx) != k - 1:
# #         return None

# #     if required_idx is not None:
# #         if not required_idx.issubset(set(cuts_idx)):
# #             return None

# #     return [float(edges[c]) for c in cuts_idx]
# def algorithm5_graph_edge_consistent(
#     series: pd.Series,
#     L: float, U: float, step: float,
#     k: int, epsilon: float, C: float,
#     *,
#     use_boundary_prefilter: bool = True,
#     min_width: Optional[float] = None,
#     excluded_boundaries: Optional[List[float]] = None,
#     required_boundaries: Optional[List[float]] = None,
# ) -> Optional[List[float]]:

#     edges, pref = build_grid(series, L, U, step)
#     m = len(edges) - 1
#     s = int(np.floor(epsilon / step))

#     if s < 0 or k < 1 or k > m:
#         return None

#     min_cells = _min_width_to_cells(min_width, step)
#     if min_cells is not None and k * min_cells > m:
#         return None

#     excluded_idx = _boundary_values_to_indices(edges, excluded_boundaries, m)
#     required_idx = _boundary_values_to_indices(edges, required_boundaries, m)

#     if required_idx is None:
#         required_idx = set()

#     if len(required_idx) > k - 1:
#         return None

#     if excluded_idx is not None and required_idx.intersection(excluded_idx):
#         return None

#     E = build_E_4d(pref, s).astype(int)
#     INF = int(pref[m]) + 10**9

#     required_list = sorted(required_idx)
#     req_to_bit = {r: i for i, r in enumerate(required_list)}
#     full_required_mask = (1 << len(required_list)) - 1

#     def boundary_allowed(j: int) -> bool:
#         return excluded_idx is None or j not in excluded_idx

#     if use_boundary_prefilter:
#         cand_interval = np.any((E < C) & (E < INF), axis=(2, 3))
#         P = [0, m]

#         for j in range(1, m):
#             if not boundary_allowed(j):
#                 continue
#             if cand_interval[:j, j].any() and cand_interval[j, j + 1:].any():
#                 P.append(j)

#         P = np.array(sorted(set(P)), dtype=int)

#         def iter_boundaries(i: int, bins_left: int):
#             lo = i + (min_cells or 1)
#             hi = m - (bins_left - 1) * (min_cells or 1)
#             seg = P[(P >= lo) & (P <= hi)]
#             for j in seg:
#                 yield int(j)

#     else:
#         def iter_boundaries(i: int, bins_left: int):
#             lo = i + (min_cells or 1)
#             hi = m - (bins_left - 1) * (min_cells or 1)
#             for j in range(lo, hi + 1):
#                 if boundary_allowed(j):
#                     yield j

#     @lru_cache(maxsize=None)
#     def dfs(i: int, bins_left: int, prev_dR_idx: int, req_mask: int) -> Optional[Tuple[int, ...]]:
#         dL_idx = prev_dR_idx if i > 0 else s

#         # Python-version-safe replacement for req_mask.bit_count()
#         missing_required = len(required_list) - bin(req_mask).count("1")
#         cuts_left = bins_left - 1

#         # Not enough remaining cut positions to include all missing required cuts
#         if missing_required > cuts_left:
#             return None

#         if bins_left == 1:
#             if req_mask != full_required_mask:
#                 return None

#             if min_cells is not None and (m - i) < min_cells:
#                 return None

#             val = E[i, m, dL_idx, s]
#             if val < C:
#                 return (i, m)
#             return None

#         for j in iter_boundaries(i, bins_left):
#             row = E[i, j, dL_idx, :]
#             valid_mask = row < INF

#             if not np.any(valid_mask):
#                 continue

#             # universal stability: every valid right shift must be stable
#             if np.any(row[valid_mask] >= C):
#                 continue

#             new_mask = req_mask
#             if j in req_to_bit:
#                 new_mask |= (1 << req_to_bit[j])

#             ok = True
#             tail_any = None

#             for dR_idx in np.flatnonzero(valid_mask):
#                 tail = dfs(j, bins_left - 1, int(dR_idx), new_mask)
#                 if tail is None:
#                     ok = False
#                     break
#                 tail_any = tail

#             if ok:
#                 return (i,) + tail_any

#         return None

#     path = dfs(0, k, s, 0)
#     if path is None:
#         return None

#     bnds = list(path)
#     if bnds[0] != 0:
#         bnds = [0] + bnds

#     cuts_idx = bnds[1:-1]

#     if len(cuts_idx) != k - 1:
#         return None

#     if required_idx and not required_idx.issubset(set(cuts_idx)):
#         return None

#     return [float(edges[c]) for c in cuts_idx]









#max

from functools import lru_cache
from typing import Optional, List, Tuple, Dict
import numpy as np
import pandas as pd


# ============================================================
# Helpers
# ============================================================

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


def build_E_4d(pref: np.ndarray, s: int) -> np.ndarray:
    """
    E[l, r, dL_idx, dR_idx] for half-open [l, r) with integer shifts dL, dR in [-s..s].
    Invalid shifted intervals are INF.
    """
    m = len(pref) - 1
    INF = int(pref[m]) + 10**9
    E = np.full((m + 1, m + 1, 2 * s + 1, 2 * s + 1), INF, dtype=int)

    def cnt(a: int, b: int) -> int:
        return int(pref[b] - pref[a])

    for l in range(0, m):
        for r in range(l + 1, m + 1):
            base = cnt(l, r)

            for dL in range(-s, s + 1):
                for dR in range(-s, s + 1):
                    Ls = l + dL
                    Rs = r + dR

                    valid = True
                    if l == 0:
                        if dL != 0:
                            valid = False
                        if not (0 < Rs <= m):
                            valid = False
                    elif r == m:
                        if dR != 0:
                            valid = False
                        if not (0 <= Ls < m):
                            valid = False
                    else:
                        if not (0 < Ls < m):
                            valid = False
                        if not (0 < Rs < m):
                            valid = False

                    if not (Ls < Rs):
                        valid = False

                    if not valid:
                        continue

                    shifted = cnt(Ls, Rs)
                    E[l, r, dL + s, dR + s] = abs(base - shifted)

    return E


# ============================================================
# Algorithm 2 — Naive exhaustive
# ============================================================

def algorithm2_edge_consistent_naive(
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

    from itertools import combinations, product

    candidates = list(range(1, m, candidate_stride))

    tested = 0
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

        base_counts = []
        ok = True
        for a, b in zip(bounds[:-1], bounds[1:]):
            if a >= b:
                ok = False
                break
            base_counts.append(int(pref[b] - pref[a]))
        if not ok:
            continue

        stable = True

        for deltas in product(range(-s, s + 1), repeat=k - 1):
            shifted = [0] + list(deltas) + [0]

            prev = 0
            valid = True
            for t, c in enumerate(bounds[1:-1], start=1):
                x = c + shifted[t]
                if not (0 < x < m) or x <= prev:
                    valid = False
                    break
                prev = x

            if not valid:
                continue

            worst = 0
            for t in range(k):
                l = bounds[t] + shifted[t]
                r = bounds[t + 1] + shifted[t + 1]

                if r <= l:
                    valid = False
                    break

                shifted_cnt = int(pref[r] - pref[l])
                dev = abs(base_counts[t] - shifted_cnt)

                if dev > worst:
                    worst = dev
                    if worst >= C:
                        break

            if (not valid) or worst >= C:
                stable = False
                break

        if stable:
            return [float(edges[c]) for c in combo]

    return None


# ============================================================
# Algorithm 4 — DP / minimax
# ============================================================

def algorithm4_edge_consistent_dp(
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

    if s < 0 or k < 1 or k > m:
        return (None, None)

    min_cells = _min_width_to_cells(min_width, step)
    max_cells = _max_width_to_cells(max_width, step)

    if min_cells is not None and k * min_cells > m:
        return (None, None)
    if min_cells is not None and max_cells is not None and min_cells > max_cells:
        return (None, None)

    excluded_idx = _boundary_values_to_indices(edges, excluded_boundaries, m)

    E = build_E_4d(pref, s).astype(int)
    INF = int(pref[m]) + 10**9

    uniq = np.unique(E[E < INF])
    if uniq.size == 0:
        return (None, None)

    def boundary_allowed(j: int) -> bool:
        return excluded_idx is None or j not in excluded_idx

    def feasible_at(T: int) -> Tuple[bool, Optional[List[int]]]:
        back_choice: Dict[Tuple[int, int, int], int] = {}

        @lru_cache(maxsize=None)
        def dp(i: int, bins_left: int, dL_idx: int) -> bool:
            if bins_left == 1:
                last_w = m - i
                if min_cells is not None and last_w < min_cells:
                    return False
                if max_cells is not None and last_w > max_cells:
                    return False

                val = E[i, m, dL_idx, s]
                return (val < INF) and (val <= T) and (i < m)

            lo = i + (min_cells or 1)
            hi = m - (bins_left - 1) * (min_cells or 1)
            if max_cells is not None:
                hi = min(hi, i + max_cells)

            if lo > hi:
                return False

            for j in range(lo, hi + 1):
                if not boundary_allowed(j):
                    continue

                row = E[i, j, dL_idx, :]
                valid_mask = row < INF
                if not np.any(valid_mask):
                    continue

                if np.any(row[valid_mask] > T):
                    continue

                ok = True
                for dR_idx in np.flatnonzero(valid_mask):
                    if not dp(j, bins_left - 1, int(dR_idx)):
                        ok = False
                        break

                if ok:
                    back_choice[(i, bins_left, dL_idx)] = j
                    return True

            return False

        ok = dp(0, k, s)
        if not ok:
            return (False, None)

        cuts_idx: List[int] = []
        i, bins_left, dL_idx = 0, k, s

        while bins_left > 1:
            j = back_choice[(i, bins_left, dL_idx)]
            cuts_idx.append(j)

            row = E[i, j, dL_idx, :]
            valid_mask = row < INF

            next_dR = None
            for dR_idx in np.flatnonzero(valid_mask):
                if dp(j, bins_left - 1, int(dR_idx)):
                    next_dR = int(dR_idx)
                    break

            if next_dR is None:
                return (False, None)

            i, bins_left, dL_idx = j, bins_left - 1, next_dR

        if len(cuts_idx) != k - 1:
            return (False, None)

        return (True, cuts_idx)

    lo, hi = 0, len(uniq) - 1
    best_T = None
    best_cuts = None

    while lo <= hi:
        mid = (lo + hi) // 2
        T = int(uniq[mid])

        ok, cuts_idx = feasible_at(T)

        if ok:
            best_T = T
            best_cuts = cuts_idx
            hi = mid - 1
        else:
            lo = mid + 1

    if best_T is None or best_cuts is None:
        return (None, None)

    if best_T >= C:
        return (None, int(best_T))

    return ([float(edges[c]) for c in best_cuts], int(best_T))


# ============================================================
# Algorithm 5 — Edge-consistent graph / DFS
# ============================================================

def algorithm5_graph_edge_consistent(
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

    if s < 0 or k < 1 or k > m:
        return None

    min_cells = _min_width_to_cells(min_width, step)
    max_cells = _max_width_to_cells(max_width, step)

    if min_cells is not None and k * min_cells > m:
        return None
    if min_cells is not None and max_cells is not None and min_cells > max_cells:
        return None

    excluded_idx = _boundary_values_to_indices(edges, excluded_boundaries, m)
    required_idx = _boundary_values_to_indices(edges, required_boundaries, m)

    if required_idx is None:
        required_idx = set()

    if len(required_idx) > k - 1:
        return None

    if excluded_idx is not None and required_idx.intersection(excluded_idx):
        return None

    E = build_E_4d(pref, s).astype(int)
    INF = int(pref[m]) + 10**9

    required_list = sorted(required_idx)
    req_to_bit = {r: i for i, r in enumerate(required_list)}
    full_required_mask = (1 << len(required_list)) - 1

    def boundary_allowed(j: int) -> bool:
        return excluded_idx is None or j not in excluded_idx

    if use_boundary_prefilter:
        cand_interval = np.any((E < C) & (E < INF), axis=(2, 3))
        P = [0, m]

        for j in range(1, m):
            if not boundary_allowed(j):
                continue
            if cand_interval[:j, j].any() and cand_interval[j, j + 1:].any():
                P.append(j)

        P = np.array(sorted(set(P)), dtype=int)

        def iter_boundaries(i: int, bins_left: int):
            lo = i + (min_cells or 1)
            hi = m - (bins_left - 1) * (min_cells or 1)
            if max_cells is not None:
                hi = min(hi, i + max_cells)

            seg = P[(P >= lo) & (P <= hi)]
            for j in seg:
                yield int(j)

    else:
        def iter_boundaries(i: int, bins_left: int):
            lo = i + (min_cells or 1)
            hi = m - (bins_left - 1) * (min_cells or 1)
            if max_cells is not None:
                hi = min(hi, i + max_cells)

            for j in range(lo, hi + 1):
                if boundary_allowed(j):
                    yield j

    @lru_cache(maxsize=None)
    def dfs(i: int, bins_left: int, prev_dR_idx: int, req_mask: int) -> Optional[Tuple[int, ...]]:
        dL_idx = prev_dR_idx if i > 0 else s

        missing_required = len(required_list) - bin(req_mask).count("1")
        cuts_left = bins_left - 1

        if missing_required > cuts_left:
            return None

        if bins_left == 1:
            if req_mask != full_required_mask:
                return None

            last_w = m - i
            if min_cells is not None and last_w < min_cells:
                return None
            if max_cells is not None and last_w > max_cells:
                return None

            val = E[i, m, dL_idx, s]
            if val < C:
                return (i, m)
            return None

        for j in iter_boundaries(i, bins_left):
            row = E[i, j, dL_idx, :]
            valid_mask = row < INF

            if not np.any(valid_mask):
                continue

            if np.any(row[valid_mask] >= C):
                continue

            new_mask = req_mask
            if j in req_to_bit:
                new_mask |= (1 << req_to_bit[j])

            ok = True
            tail_any = None

            for dR_idx in np.flatnonzero(valid_mask):
                tail = dfs(j, bins_left - 1, int(dR_idx), new_mask)
                if tail is None:
                    ok = False
                    break
                tail_any = tail

            if ok:
                return (i,) + tail_any

        return None

    path = dfs(0, k, s, 0)
    if path is None:
        return None

    bnds = list(path)
    if bnds[0] != 0:
        bnds = [0] + bnds

    cuts_idx = bnds[1:-1]

    if len(cuts_idx) != k - 1:
        return None

    if required_idx and not required_idx.issubset(set(cuts_idx)):
        return None

    return [float(edges[c]) for c in cuts_idx]


#script to run benchmark and save dataset to CSV

# import time
# import pandas as pd
# import numpy as np

# def run_benchmark_alg5_win_integer_events():
#     # 1. Create a "High Variance" Event Log (Integer IDs / Hours).
#     # We populate the dataset such that the number of events per hour constantly changes.
#     # Hour 0 has 1 event, Hour 1 has 2 events, Hour 2 has 3 events... up to 8, then repeats.
#     vals = []
#     for hour in range(2000):
#         # Place the exact integer `hour` into the list (hour % 8 + 1) times.
#         # No decimals! Just raw event records.
#         vals.extend([hour] * (hour % 8 + 1)) 
        
#     series = pd.Series(vals)
    
#     # --- Save the event log to a CSV file ---
#     # We name the column "time_of_event" to match the crime/hour logic
#     series.to_csv("crime_events_log.csv", index=False, header=["time_of_event"])
#     print("Dataset saved to 'crime_events_log.csv'")
#     # ----------------------------------------
    
#     # 2. Setup parameters
#     # The grid spans from hour 0 to hour 2000. 
#     # step = 10.0 means we are binning the data into 10-hour blocks.
#     L, U, step = 0.0, 2000.0, 10.0  
#     k = 10
#     epsilon = 20.0                  
#     C = 5                           
    
#     print("=== Configuration ===")
#     print(f"Grid Range: [{L}, {U}] with step {step} (m = {int((U-L)/step)} bins)")
#     print(f"Total Events Logged: {len(series)}")
#     print(f"k = {k}, epsilon = {epsilon}, C = {C}\n")
    
#     # Benchmark Algorithm 4 (DP / Minimax)
#     print("Running Algorithm 4...")
#     start_4 = time.perf_counter()
#     res_4 = algorithm4_edge_consistent_dp(series, L, U, step, k, epsilon, C)
#     end_4 = time.perf_counter()
#     time_4 = end_4 - start_4
    
#     # Benchmark Algorithm 5 (Graph / DFS)
#     print("Running Algorithm 5...")
#     start_5 = time.perf_counter()
#     res_5 = algorithm5_graph_edge_consistent(series, L, U, step, k, epsilon, C)
#     end_5 = time.perf_counter()
#     time_5 = end_5 - start_5
    
#     print("\n=== Results ===")
#     print(f"Algorithm 4 (DP) Time:   {time_4:.5f} seconds")
#     print(f"Algorithm 5 (DFS) Time:  {time_5:.5f} seconds")
#     print("-" * 30)
    
#     if time_5 < time_4:
#         multiplier = time_4 / time_5
#         print(f"Success! Algorithm 5 is {multiplier:.2f}x faster with this raw integer event log.")
#     else:
#         print("Algorithm 4 was faster.")

# if __name__ == "__main__":
#     run_benchmark_alg5_win_integer_events()




# import time
# import pandas as pd
# import numpy as np
# import gc

# def run_scaling_benchmark():
#     # Loop m from 2000 up to 20000 in steps of 1000
#     m_values = range(2000, 20001, 1000)
    
#     for m in m_values:
#         print(f"\n{'='*50}")
#         print(f"Testing Grid Size: m = {m}")
#         print(f"{'='*50}")
        
#         # 1. Generate high-variance event data scaled to the current m
#         # We loop from 0 to m, placing (hour % 8 + 1) events at each hour.
#         vals = []
#         for hour in range(m):
#             vals.extend([hour] * (hour % 8 + 1))
            
#         series = pd.Series(vals)
        
#         # 2. Parameters mapped exactly to m bins
#         L = 0.0
#         U = float(m)
#         step = 1.0       # 1 unit per bin guarantees exactly m bins
#         k = 10
#         epsilon = 2.0    # s = 2
#         C = 2            # Strict threshold for aggressive filtering
        
#         print(f"Data Points generated: {len(series)}")
#         print("Building matrix and running algorithms... (This may take time)")
        
#         try:
#             # Benchmark Algorithm 4
#             start_4 = time.perf_counter()
#             res_4 = algorithm4_edge_consistent_dp(series, L, U, step, k, epsilon, C)
#             end_4 = time.perf_counter()
#             time_4 = end_4 - start_4
            
#             # Benchmark Algorithm 5
#             start_5 = time.perf_counter()
#             res_5 = algorithm5_graph_edge_consistent(series, L, U, step, k, epsilon, C)
#             end_5 = time.perf_counter()
#             time_5 = end_5 - start_5
            
#             print(f"Algorithm 4 (DP) Time:   {time_4:.5f} seconds")
#             print(f"Algorithm 5 (DFS) Time:  {time_5:.5f} seconds")
            
#             if time_5 < time_4:
#                 multiplier = time_4 / time_5
#                 print(f"-> Success! Algorithm 5 is {multiplier:.2f}x faster.")
#             else:
#                 print("-> Algorithm 4 was faster.")
                
#         except MemoryError:
#             print("\n[!] MemoryError: Your system ran out of RAM!")
#             print(f"The 4D matrix for m={m} is too large to fit in memory.")
#             break 
            
#         # Force Python to clean up the giant matrices before the next loop
#         gc.collect()

# if __name__ == "__main__":
#     run_scaling_benchmark()



#alg5 with out the table build time



def algorithm5_graph_edge_consistent_optimized(
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

    if s < 0 or k < 1 or k > m:
        return None

    min_cells = _min_width_to_cells(min_width, step)
    max_cells = _max_width_to_cells(max_width, step)

    if min_cells is not None and k * min_cells > m:
        return None
    if min_cells is not None and max_cells is not None and min_cells > max_cells:
        return None

    excluded_idx = _boundary_values_to_indices(edges, excluded_boundaries, m)
    required_idx = _boundary_values_to_indices(edges, required_boundaries, m)
    if required_idx is None:
        required_idx = set()
    if len(required_idx) > k - 1:
        return None
    if excluded_idx is not None and required_idx.intersection(excluded_idx):
        return None

    required_list = sorted(required_idx)
    req_to_bit = {r: idx for idx, r in enumerate(required_list)}
    full_required_mask = (1 << len(required_list)) - 1

    def boundary_allowed(j: int) -> bool:
        return excluded_idx is None or j not in excluded_idx

    # --- NEW: Helper to calculate error on the fly using ONLY pref ---
    def check_error(l: int, r: int, dL: int, dR: int) -> int:
        Ls = l + dL
        Rs = r + dR
        
        # Boundary safety checks
        if l == 0 and (dL != 0 or not (0 < Rs <= m)): return 10**9
        if r == m and (dR != 0 or not (0 <= Ls < m)): return 10**9
        if l != 0 and r != m and (not (0 < Ls < m) or not (0 < Rs < m)): return 10**9
        if not (Ls < Rs): return 10**9
        
        base = int(pref[r] - pref[l])
        shifted = int(pref[Rs] - pref[Ls])
        return abs(base - shifted)

    # --- NEW: On-the-fly Prefilter ---
    if use_boundary_prefilter:
        # Instead of np.any on a giant matrix, we evaluate validity on the fly.
        # We short-circuit (break early) as soon as we find ONE valid shift.
        cand_interval = np.zeros((m + 1, m + 1), dtype=bool)
        for l in range(m):
            for r in range(l + 1, m + 1):
                valid = False
                for dL in range(-s, s + 1):
                    for dR in range(-s, s + 1):
                        if check_error(l, r, dL, dR) < C:
                            valid = True
                            break
                    if valid:
                        break
                cand_interval[l, r] = valid

        P = [0, m]
        for j in range(1, m):
            if not boundary_allowed(j):
                continue
            if cand_interval[:j, j].any() and cand_interval[j, j + 1:].any():
                P.append(j)
        P = np.array(sorted(set(P)), dtype=int)

        def iter_boundaries(i: int, bins_left: int):
            lo = i + (min_cells or 1)
            hi = m - (bins_left - 1) * (min_cells or 1)
            if max_cells is not None:
                hi = min(hi, i + max_cells)
            seg = P[(P >= lo) & (P <= hi)]
            for j in seg:
                yield int(j)
    else:
        def iter_boundaries(i: int, bins_left: int):
            lo = i + (min_cells or 1)
            hi = m - (bins_left - 1) * (min_cells or 1)
            if max_cells is not None:
                hi = min(hi, i + max_cells)
            for j in range(lo, hi + 1):
                if boundary_allowed(j):
                    yield j

    # --- NEW: DFS using on-the-fly calculations ---
    @lru_cache(maxsize=None)
    def dfs(i: int, bins_left: int, prev_dR: int, req_mask: int) -> Optional[Tuple[int, ...]]:
        dL = prev_dR if i > 0 else 0

        missing_required = len(required_list) - bin(req_mask).count("1")
        if missing_required > bins_left - 1:
            return None

        if bins_left == 1:
            if req_mask != full_required_mask:
                return None
            last_w = m - i
            if min_cells is not None and last_w < min_cells: return None
            if max_cells is not None and last_w > max_cells: return None

            err = check_error(i, m, dL, 0)
            if err < 10**9 and err < C:
                return (i, m)
            return None

        for j in iter_boundaries(i, bins_left):
            # --- STRICT MINIMAX FIX ---
            # Step 1: Check ALL valid shifts first
            valid_dRs = []
            branch_failed = False
            
            for dR in range(-s, s + 1):
                err = check_error(i, j, dL, dR)
                if err < 10**9: # If it is a valid geometric shift
                    if err >= C: 
                        branch_failed = True # Fails the strict rule!
                        break
                    valid_dRs.append(dR)
            
            # If even one shift was >= C, or there were no valid shifts, skip 'j' entirely
            if branch_failed or not valid_dRs:
                continue
            # --------------------------

            new_mask = req_mask
            if j in req_to_bit:
                new_mask |= (1 << req_to_bit[j])

            # Step 2: If we pass the strict test, proceed with DFS
            ok = True
            tail_any = None
            for dR in valid_dRs:
                tail = dfs(j, bins_left - 1, dR, new_mask)
                if tail is None:
                    ok = False
                    break
                tail_any = tail

            if ok and tail_any is not None:
                return (i,) + tail_any

        return None

    path = dfs(0, k, 0, 0)
    
    if path is None:
        return None
    bnds = list(path)
    if bnds[0] != 0:
        bnds = [0] + bnds
    cuts_idx = bnds[1:-1]
    
    if len(cuts_idx) != k - 1:
        return None
    if required_idx and not required_idx.issubset(set(cuts_idx)):
        return None

    return [float(edges[c]) for c in cuts_idx]


### running copmare between 5 and 4 calculate also the table build time
# import time
# import pandas as pd
# import numpy as np
# import gc

# def run_scaling_benchmark_with_matrix_time():
#     # Loop m from 2000 up to 20000 in steps of 1000
#     m_values = range(2000, 20001, 1000)
    
#     for m in m_values:
#         print(f"\n{'='*50}")
#         print(f"Testing Grid Size: m = {m}")
#         print(f"{'='*50}")
        
#         # 1. Generate high-variance event data
#         vals = []
#         for hour in range(m):
#             vals.extend([hour] * (hour % 8 + 1))
            
#         series = pd.Series(vals)
        
#         # 2. Parameters mapped exactly to m bins
#         L, U, step = 0.0, float(m), 1.0       
#         k = 10
#         epsilon = 2.0    
#         C = 5            
        
#         print(f"Data Points generated: {len(series)}")
        
#         try:
#             # --- NEW: Time the Matrix Building Process Isolated ---
#             print("Measuring matrix E build time...")
#             edges, pref = build_grid(series, L, U, step)
#             s = int(np.floor(epsilon / step))
            
#             start_E = time.perf_counter()
#             _ = build_E_4d(pref, s)
#             end_E = time.perf_counter()
#             time_E = end_E - start_E
#             # -----------------------------------------------------

#             # Benchmark Algorithm 4
#             print("Running Algorithm 4...")
#             start_4 = time.perf_counter()
#             res_4 = algorithm4_edge_consistent_dp(series, L, U, step, k, epsilon, C)
#             end_4 = time.perf_counter()
#             time_4 = end_4 - start_4
            
#             # Benchmark Algorithm 5
#             print("Running Algorithm 5...")
#             start_5 = time.perf_counter()
#             res_5 = algorithm5_graph_edge_consistent(series, L, U, step, k, epsilon, C)
#             end_5 = time.perf_counter()
#             time_5 = end_5 - start_5
            
#             print("\n=== Results ===")
#             print(f"Matrix E Build Time: {time_E:.5f} seconds")
#             print(f"Algorithm 4 Total Time:   {time_4:.5f} seconds")
#             print(f"Algorithm 5 Total Time:  {time_5:.5f} seconds")
            
#             # Show how much of Alg 5's time was JUST the algorithm logic (subtracting the matrix build)
#             pure_alg5_time = max(0, time_5 - time_E)
#             print(f"(Pure Alg 5 Search Time excluding Matrix: {pure_alg5_time:.5f} seconds)")

#             if time_5 < time_4:
#                 multiplier = time_4 / time_5
#                 print(f"\n-> Success! Algorithm 5 is {multiplier:.2f}x faster overall.")
#             else:
#                 print("\n-> Algorithm 4 was faster.")
                
#         except MemoryError:
#             print("\n[!] MemoryError: Your system ran out of RAM!")
#             print(f"The 4D matrix for m={m} is too large to fit in memory.")
#             break 
            
#         # Force Python to clean up the giant matrices before the next loop
#         gc.collect()

# if __name__ == "__main__":
#     run_scaling_benchmark_with_matrix_time()


import time
import pandas as pd
import numpy as np
import gc


def run_scaling_benchmark_with_matrix_time():

    # ============================================================
    # Store all benchmark results here
    # ============================================================
    results = []

    # Loop m from 1000 up to 20000 in steps of 1000
    m_values = range(1000, 6000, 500)

    # Random number generator
    rng = np.random.default_rng()

    for m in m_values:

        print(f"\n{'='*50}")
        print(f"Testing Grid Size: m = {m}")
        print(f"{'='*50}")

        # ============================================================
        # 1. Generate RANDOM event data
        # ============================================================

        num_points = int(4.5 * m)

        vals = rng.integers(
            low=0,
            high=m,
            size=num_points
        )

        series = pd.Series(vals)

        # ============================================================
        # 2. Parameters
        # ============================================================

        L = 0.0
        U = float(m)
        step = 1.0

        k = 10
        epsilon = 2.0
        C = 10

        print(f"Data Points generated: {len(series)}")

        try:

            # ========================================================
            # Matrix E Build Time
            # ========================================================

            print("Measuring matrix E build time...")

            edges, pref = build_grid(
                series,
                L,
                U,
                step
            )

            s = int(np.floor(epsilon / step))

            start_E = time.perf_counter()

            _ = build_E_4d(
                pref,
                s
            )

            end_E = time.perf_counter()

            time_E = end_E - start_E


            # ========================================================
            # Algorithm 4
            # ========================================================

            print("Running Algorithm 4 (DP)...")

            start_4 = time.perf_counter()

            res_4 = algorithm4_edge_consistent_dp(
                series,
                L,
                U,
                step,
                k,
                epsilon,
                C
            )

            end_4 = time.perf_counter()

            time_4 = end_4 - start_4

            found_4 = (
                "Found"
                if res_4[0] is not None
                else "Not Found"
            )


            # ========================================================
            # Algorithm 5 Original
            # ========================================================

            # print("Running Algorithm 5 (Original DFS)...")

            # start_5 = time.perf_counter()

            # res_5 = algorithm5_graph_edge_consistent(
            #     series,
            #     L,
            #     U,
            #     step,
            #     k,
            #     epsilon,
            #     C
            # )

            # end_5 = time.perf_counter()

            # time_5 = end_5 - start_5

            # found_5 = (
            #     "Found"
            #     if res_5 is not None
            #     else "Not Found"
            # )


            # ========================================================
            # Algorithm 5 Optimized
            # ========================================================

            print("Running Algorithm 5 (Optimized DFS)...")

            start_5_opt = time.perf_counter()

            res_5_opt = algorithm5_graph_edge_consistent_optimized(
                series,
                L,
                U,
                step,
                k,
                epsilon,
                C
            )

            end_5_opt = time.perf_counter()

            time_5_opt = end_5_opt - start_5_opt

            found_5_opt = (
                "Found"
                if res_5_opt is not None
                else "Not Found"
            )


            # ========================================================
            # Save this m result
            # ========================================================

            results.append({
                "m": m,
                "num_points": len(series),

                "matrix_E_time": time_E,

                "alg4_time": time_4,
                "alg4_status": found_4,

                # "alg5_original_time": time_5,
                # "alg5_original_status": found_5,

                "alg5_optimized_time": time_5_opt,
                "alg5_optimized_status": found_5_opt
            })


            # ========================================================
            # Print Results
            # ========================================================

            print("\n=== Results ===")

            print(
                f"Matrix E Build Time: "
                f"{time_E:.5f} seconds"
            )

            print("-" * 60)

            print(
                f"Algorithm 4          | "
                f"Status: {found_4:<9} | "
                f"Time: {time_4:.5f} s"
            )

            # print(
            #     f"Algorithm 5 Original | "
            #     f"Status: {found_5:<9} | "
            #     f"Time: {time_5:.5f} s"
            # )

            print(
                f"Algorithm 5 Optimized| "
                f"Status: {found_5_opt:<9} | "
                f"Time: {time_5_opt:.5f} s"
            )

            print("-" * 60)

            if time_5_opt < time_4:

                multiplier = time_4 / time_5_opt

                print(
                    f"-> Alg 5 Optimized is "
                    f"{multiplier:.2f}x faster than Alg 4."
                )


        except MemoryError:

            print(
                f"\n[!] MemoryError for m={m}"
            )

            print(
                "Attempting Algorithm 5 Optimized only..."
            )

            try:

                start_5_opt = time.perf_counter()

                res_5_opt = algorithm5_graph_edge_consistent_optimized(
                    series,
                    L,
                    U,
                    step,
                    k,
                    epsilon,
                    C
                )

                end_5_opt = time.perf_counter()

                time_5_opt = end_5_opt - start_5_opt

                found_5_opt = (
                    "Found"
                    if res_5_opt is not None
                    else "Not Found"
                )


                # Save partial result
                results.append({
                    "m": m,
                    "num_points": len(series),

                    "matrix_E_time": None,

                    "alg4_time": None,
                    "alg4_status": "MemoryError",

                    "alg5_original_time": None,
                    "alg5_original_status": "MemoryError",

                    "alg5_optimized_time": time_5_opt,
                    "alg5_optimized_status": found_5_opt
                })


                print(
                    f"Algorithm 5 Optimized | "
                    f"Status: {found_5_opt:<9} | "
                    f"Time: {time_5_opt:.5f} s"
                )

            except Exception as e:

                print(
                    f"Alg 5 Optimized failed: {e}"
                )

            break


        # ============================================================
        # Clean memory
        # ============================================================

        gc.collect()


    # ================================================================
    # SAVE ALL RESULTS TO CSV
    # ================================================================

    results_df = pd.DataFrame(results)

    results_df.to_csv(
        "scaling_benchmark_results.csv",
        index=False
    )

    print("\n" + "=" * 60)
    print("Benchmark finished.")
    print("Results saved to: scaling_benchmark_results.csv")
    print("=" * 60)

    print("\nFinal Results:")
    print(results_df)


if __name__ == "__main__":
    run_scaling_benchmark_with_matrix_time()