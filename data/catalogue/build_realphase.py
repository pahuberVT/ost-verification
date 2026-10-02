"""Build the station-kept working catalogue from a PRISTINE Celestrak pull.

Provenance chain (governance): pristine untouched Celestrak pull (read-only, sha-pinned)
  -> restrict to the 7852 steady NORADs (universe.STEADY)
  -> one TLE per NORAD = its LATEST entry inside the pull window (stale/2024 entries rejected)
  -> station-kept model: zero B* (no drag decay), REAL elements otherwise untouched (real phasing)
  -> recompute the line-1 checksum
  -> write 3-line catalogue + report sha256.

Physical realism is verified by PROPAGATED positions (a plane must spread ~thousands of km at a common
instant), NEVER by element phase angles at per-TLE epochs -- the u_L-at-epoch "collapse" is a node-epoch
convention, not co-location (see the 2026-07-08 false-alarm resolution).

Run: conda activate orbit; PYTHONNOUSERSITE=1 python data/catalogues/build_realphase.py \
        --src data/catalogues/celestrak/march25-26-tle.txt --out data/catalogues/starlink_realphase_2026-03-25.tle
"""
import argparse, os, sys, hashlib, collections
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "coverage"))
import universe
from sgp4.api import Satrec
from itertools import combinations

EPOCH_LO, EPOCH_HI = 26060.0, 26099.0    # accept only 2026 mid/late-March epochs (reject stale 2024 rows)


def is_l1(s): return len(s) >= 63 and s.startswith("1 ") and s[2:7].strip().isdigit()
def is_l2(s): return len(s) >= 63 and s.startswith("2 ") and s[2:7].strip().isdigit()


def checksum(body68):
    """TLE checksum: sum of digits (minus signs count 1) over the first 68 cols, mod 10."""
    s = 0
    for c in body68[:68]:
        if c.isdigit():
            s += int(c)
        elif c == "-":
            s += 1
    return str(s % 10)


def zero_bstar_line1(l1, zero_bstar_field):
    """Return line1 with the B* field (cols 54-61) replaced by a zero field + recomputed checksum."""
    assert len(zero_bstar_field) == 8, "B* field must be 8 chars"
    body = l1[:53] + zero_bstar_field + l1[61:68]
    return body + checksum(body)


def load_pull(path):
    """{norad: [(epoch_float, name, l1, l2), ...]} for steady NORADs, all epochs kept."""
    L = [l.rstrip("\n") for l in open(path, errors="replace")]
    L = [l for l in L if l.strip()]
    byn = {}
    i = 0
    while i < len(L) - 1:
        if is_l1(L[i]) and is_l2(L[i + 1]):
            try:
                n = int(L[i][2:7])
                if n in universe.STEADY:
                    ep = float(L[i][18:32])
                    name = L[i - 1].strip() if i > 0 and not is_l1(L[i - 1]) and not is_l2(L[i - 1]) else f"NORAD {n}"
                    byn.setdefault(n, []).append((ep, name, L[i], L[i + 1]))
            except Exception:
                pass
            i += 2
        else:
            i += 1
    return byn


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True, help="pristine Celestrak pull (read-only source)")
    ap.add_argument("--out", required=True, help="output working catalogue path")
    ap.add_argument("--old", default=os.path.join(HERE, "starlink_nodrag.tle"),
                    help="old catalogue to copy the exact zero-B* field format from")
    args = ap.parse_args()

    # exact zero-B* 8-char field, mirrored from the known-good old catalogue
    old_lines = [l.rstrip("\n") for l in open(args.old, errors="replace") if l.startswith("1 ")]
    zero_bstar = old_lines[0][53:61]
    assert zero_bstar.replace(" ", "").replace("+", "").replace("-", "").strip("0") == "", \
        f"expected a zero B* field in old cat, got {zero_bstar!r}"
    print(f"[format] zero-B* field mirrored from old cat: {zero_bstar!r}")

    byn = load_pull(args.src)
    print(f"[src] {os.path.basename(args.src)}: {len(byn)} steady NORADs present (of {len(universe.STEADY)})")

    out_rows = {}
    stale, missing, badprop = [], [], []
    for n in sorted(universe.STEADY):
        entries = byn.get(n, [])
        in_win = [e for e in entries if EPOCH_LO <= e[0] <= EPOCH_HI]
        if not in_win:
            (missing if not entries else stale).append(n)
            continue
        ep, name, l1, l2 = max(in_win, key=lambda e: e[0])     # latest in-window entry
        l1z = zero_bstar_line1(l1, zero_bstar)
        # sanity: it must still propagate
        try:
            s = Satrec.twoline2rv(l1z, l2)
            e, r, v = s.sgp4(int(s.jdsatepoch + s.jdsatepochF), (s.jdsatepoch + s.jdsatepochF) % 1)
            if e != 0:
                badprop.append(n); continue
        except Exception:
            badprop.append(n); continue
        out_rows[n] = (name, l1z, l2, ep, r)

    print(f"[build] wrote {len(out_rows)} sats  | rejected: stale(no 2026 entry)={len(stale)} "
          f"missing(absent)={len(missing)} badprop={len(badprop)}")
    if stale or missing or badprop:
        print(f"  STALE {stale[:10]}{'...' if len(stale)>10 else ''}")
        print(f"  MISSING {missing[:10]}{'...' if len(missing)>10 else ''}")
        print(f"  BADPROP {badprop[:10]}{'...' if len(badprop)>10 else ''}")

    # write the 3-line catalogue
    with open(args.out, "w") as f:
        for n in sorted(out_rows):
            name, l1z, l2, ep, r = out_rows[n]
            f.write(f"{name}\n{l1z}\n{l2}\n")
    sha = hashlib.sha256(open(args.out, "rb").read()).hexdigest()
    print(f"[out] {args.out}\n      n={len(out_rows)}  sha256={sha}  sha12={sha[:12]}")

    # ---- verification ----
    eps = np.array([out_rows[n][3] for n in out_rows])
    print(f"[verify] epochs: min={eps.min():.3f} max={eps.max():.3f} span_days={eps.max()-eps.min():.3f} "
          f"all_2026={bool((eps>=EPOCH_LO).all() and (eps<=EPOCH_HI).all())}")
    # B*=0 baked in?
    z = sum(1 for n in out_rows if out_rows[n][1][53:61] == zero_bstar)
    print(f"[verify] B*=0 baked into {z}/{len(out_rows)} line-1s")
    # physical realism: densest plane, propagate to a common instant, pairwise separations
    sats = {n: Satrec.twoline2rv(out_rows[n][1], out_rows[n][2]) for n in out_rows}
    raan = np.array([float(out_rows[n][2][17:25]) for n in out_rows]); ids = list(out_rows)
    mode = collections.Counter(np.round(raan).astype(int)).most_common(1)[0][0]
    plane = [ids[k] for k in range(len(ids)) if abs(((raan[k]-mode+180) % 360)-180) < 0.6]
    from sgp4.api import jday
    jd, fr = jday(2026, 3, 27, 0, 0, 0)
    pos = []
    for n in plane:
        e, r, v = sats[n].sgp4(jd, fr)
        if e == 0:
            pos.append(r)
    pos = np.array(pos)
    dd = np.array([np.linalg.norm(pos[i]-pos[j]) for i, j in combinations(range(len(pos)), 2)])
    print(f"[verify] densest plane RAAN~{mode} n={len(plane)}: pairwise sep km "
          f"min={dd.min():.1f} med={np.median(dd):.1f} max={dd.max():.1f} "
          f"(realistic filled plane ~thousands km; ~0 would mean collapsed)")


if __name__ == "__main__":
    main()
