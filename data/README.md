[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23108549.svg)](https://doi.org/10.5281/zenodo.23108549)

# Reproducibility data package — orbit calculations

Data behind the atlas at https://pahuberVT.github.io/ost-verification/ and the orbit results of the
paper *Verification of the Outer Space Treaty with active interrogation* (P. Huber). Every number in
this README is read from a file; the file is named in parentheses after it. Paths without a leading
`data/` are relative to this directory; paths such as `coorbit/…` or `artifacts/…` are in the source
repository (the "repo").

## 1. What this is

The paper studies random-sampling inspection of the N = 7852 steady Starlink satellites
(`catalogue/shells.json` meta `n_steady`), with a sampling fraction f = M/N (`inspection.tex`, eq. at
line 38) and three inspection platforms (labels as used on the atlas page, `../index.html`):

* **S1 — co-orbit platforms**: finite-thrust tours that rendezvous with each target in turn and hold
  150 m behind it for one revolution (`flown/*/<inspector>/summary.json` provenance `trail_m`,
  `dwell_rev`). Flown: the full fleet `v0_v36` (f = 1), the f = 0.1 sample `F0.1_s0_v36`, and the two
  "wing" fleets that pick up what the fly-by platforms do not reach (`N4_plus21dose_v36`,
  `drifter_F0.1_wing_v36`).
* **S2 — routed fly-by platform**: one manoeuvring drifter steering to a 0.2–0.4 km pass of each
  tagged satellite (`../payloads/drifter_F01_payload.json` meta `band`). Record:
  `encounters/encounters_drifter_F0.1_s0.npz`.
* **S3 — passive fly-by platforms**: four non-manoeuvring drifters, encounter = each target's closest
  approach of the mission (`../payloads/survey_N4_events.json` meta `tag`). Record:
  `encounters/encounters_N4.npz`; seeds in `fleets/place5_band_asflown.json`.

The atlas payloads (`../payloads/`) are the page's own reduced views of these records; this directory
holds the records the paper rests on, so that the orbit results can be checked without the atlas.

### Two kinds of trajectory

1. **Targets on the catalogue clock are SGP4 of the shipped TLE file and nothing else.** Anyone with
   `catalogue/starlink_realphase_2026-03-25.tle` and a standard SGP4 reproduces them exactly. The
   project uses the reference implementation of Vallado et al. 2006, "Revisiting Spacetrack Report #3",
   as the Python package `sgp4` (version 2.27 in the project's `orbit` conda environment), gravity
   constants WGS72 (`coverage/propagator.py`). The catalogue layer of the page (`../payloads/catalogue.json`)
   and the per-pass target states in the fly-by payloads derive from it. The per-leg target rows in the
   co-orbit payloads (`tgt` in `../payloads/insp/*/*.json`) are the Orekit copy of that SGP4 seed,
   propagated with the chaser's physics inside the leg (`summary.json` provenance `target_path`:
   "universe.steady_catalogue -> propagator.build_satrecs -> globalref.from_sgp4 (ref-sgp4, TEME ->
   EME2000 at the boundary)").
2. **The 60-s ephemeris archives (available on request, section 7) are our flown chaser trajectories**
   (and the Orekit target copies), produced by the repo's Orekit flight code
   (`coorbit/tour_flight.py`, driven fleet-wide by `coorbit/fleet_flight.py`; sha256 of all 14 flight
   source files in `summary.json` provenance `source_sha256`) from each leg's departure state. They are
   reproducible by re-flying with that code on the sized tours shipped here, not from SGP4. Section 5
   says which shipped fields give the departure state of each leg.

## 2. Provenance

* **Flight code commits** (`flown/<run>/<inspector>/summary.json`, `provenance.git_commit`; counts =
  inspectors with legs):
  * `v0_v36`: `b9ff2200a1ee4924c0d8e4e26de9831f3d451809` (61 of 61).
  * `F0.1_s0_v36`: `2065e67a964829cfe63b407caa7ae89ebb112517` (10), `ad5286e96bcb3f64c7ac3402a1f10c9a039748dd` (5),
    `fdfd5dee6bd74d39b0b85dc5e1b04efb43ade3ac` (2). The three are labels of one source set: every
    inspector's `provenance.source_sha256` (14 flight files) is identical across the run.
  * `N4_plus21dose_v36`: `fdfd5dee6bd74d39b0b85dc5e1b04efb43ade3ac` (13 of 13).
  * `drifter_F0.1_wing_v36`: `fdfd5dee6bd74d39b0b85dc5e1b04efb43ade3ac` (1 of 1).
  * `provenance.git_dirty` is `true` in every summary of all four runs: the working tree carried
    uncommitted changes when the flights ran. The sha256 of the 14 flight source files actually used
    is recorded per inspector in `provenance.source_sha256` and is the binding identity of the flight code.
* **Keep-out radius**: 100.0 m (`summary.json` provenance `terminal_keepout_m`; also `keepout_m` in
  every leg record of `checkpoint.json`).
* **Catalogue**: `starlink_realphase_2026-03-25.tle`, sha256
  `5d5748ef788681fea65e6fe79553cd2092bad86eb4b88172ea54cc0476b8b05b` (computed on the shipped file);
  the first 12 hex digits `5d5748ef7886` are the frozen identity checked by `coverage/universe.py`
  (`CATALOGUE_SHA12`) and stamped as `catalogue_sha12` / `catalogue` in every summary, npz provenance,
  fleet file and payload meta.
* **Platform** (`summary.json` provenance, identical in all 92 inspector summaries of the four runs):
  `thrust_N` 0.17, `isp_s` 1500.0, `mass0_kg` 300.0, `trail_m` 150.0, `dwell_rev` 1.0. The same values
  appear as `platform.thrust_N / isp_s / mass_kg` in `../payloads/drifter_F01_payload.json` meta and as
  `burn_stats.thrust_N` in every tour payload meta.
* **Dynamics of the flown legs** (`summary.json` provenance): Orekit via `orekit_jpype` 13.1.5.0;
  `gravity_degree_order` [2, 0] (J2 only), `mu_m3s2` 398600441800000.0, `ae_m` 6378136.46,
  `j2` 0.0010826263563941533, integrator `DormandPrince853`, `pos_tol_m` 1e-06; recorder samples
  `sample_s_leg` 600 s and `sample_s_terminal` 60 s.
* **Dynamics of the fly-by records**: S3 drifters Orekit Cowell 4x4 with drag on, targets ref-sgp4,
  1825 d horizon, 12 km capture (`../payloads/survey_N4_events.json` meta `tag`; `encounters_N4.npz`
  provenance `gravity` [4, 4], `horizon_days` 1825.0, `capture_km` 12.0, `coarse_dt_s` 250.0). S2
  drifter Orekit Cowell 4x4 drag off with drag make-up as an estimate (`drifter_F01_payload.json` meta
  `tag`; `encounters_drifter_F0.1_s0.npz` provenance `capture_km` 50.0, `x_km` 0.4).
* **Mission epoch**: `2026-03-25T21:25:17.146830260753631584Z` (`summary.json` provenance
  `mission_epoch_utc`; `epoch_utc` in `encounters_N4.npz` provenance; JD 2461125.0 + 0.39255956979468465,
  `epoch_jd0`/`epoch_fr0` there). It is the latest TLE epoch in the catalogue
  (`coverage/propagator.py`, `common_epoch_jd`); catalogue line-1 epochs span day-of-year 26083.369 to
  26084.893 (read from the TLE file).
* **Sized tours** (the plans the flights followed; [EST] sizing, `fleets/*.json` field `tag`): fleet
  files carry a `sha12` that the flown record stamps back as `fleet_sha12` (`flown/<run>/fleet_summary.json`),
  and each inspector's sized tour is pinned by `sized_tour_sha256` in its `summary.json` and
  `checkpoint.json` (for example `47d946367822586146d1d9114afb89950b2407950d535106ae35cc141bc1552d` for
  `fleets/sized_tours/tour_F0.1_s0_A10_t0.12_e1e+09_r10000/43_484_lam8_i00.json`).

## 3. Files and schema

```
README.md
catalogue/
  starlink_realphase_2026-03-25.tle   7852 objects, 3-line TLE (name, line 1, line 2), B* zeroed
  build_realphase.py                  builds the catalogue from the pristine pull (+ shells.json)
  shells.json                         the 7852-object steady universe the builder restricts to
  celestrak/march25-26-tle.txt        the pristine Celestrak pull the catalogue was built from
fleets/
  tour_fleet_v0.json, tour_fleet_F0.1_s0.json,
  tour_N4_A10_t0.12_e1e+09_r100000_plus21dose_liftall.json,
  tour_F0.1_s0_A10_t0.12_e1e+09_r10000.json          the four sized S1 fleets
  sized_tours/<fleet>/<inspector>.json                per-inspector sized tours (69 / 17 / 16 / 1 files)
  cases/*.txt                                         uncovered sets the two wing fleets were sized on
  place5_band_asflown.json                            the S3 drift fleet seeds
encounters/
  encounters_N4.npz                   S3 fly-by record (230944 rows, 4 drifters)
  encounters_drifter_F0.1_s0.npz      S2 fly-by record (783 rows, 1 drifter)
flown/<run>/
  fleet_summary.json, ephem_manifest.json, closest_approach.json
  <inspector>/summary.json, <inspector>/checkpoint.json
```

### 3.1 Catalogue

* `starlink_realphase_2026-03-25.tle` — 7852 TLEs (count of line-1 rows). Derived from the pristine
  pull by `build_realphase.py`: restrict to the steady NORADs of `shells.json`, keep each object's
  latest entry with epoch in [26060, 26099] (`EPOCH_LO`, `EPOCH_HI` in the script; stale 2024 rows
  rejected), replace the B* field (line 1, columns 54–61) by the zero field ` 00000+0` (read from line 1
  of the shipped catalogue; the script copies this 8-character field from an older catalogue
  `starlink_nodrag.tle` that is not shipped and no longer in the repo — pass any line-1 with that
  field as `--old`), recompute the line-1 checksum. All other elements are the real Celestrak values
  ("real phasing"). Zero B* is the station-kept model: no drag decay (`coverage/universe.py` docstring).
* `celestrak/march25-26-tle.txt` — sha256 `302122bdd38741527b7e320e4388a61d22d20b7422dbae129560a99250c7bc4f`,
  50755 TLEs (count of line-1 rows), read-only pristine pull. The repo also holds the earlier pull
  `data/catalogues/celestrak/march15-16-tle.txt` (sha256
  `e1dc794d31a58c3c68e5d9cb5f602894271b9a2f9946c6ba87941661e1441e56`, 58696 TLEs); the builder does not
  read it, so it is not shipped. The pulls are the Celestrak Starlink TLE sets of 15–16 and 25–26 March
  2026 (file names).
* `shells.json` — sha256 `5fcbbfe8ac6fcf53a5409534213d1a2b2d235c2aac51bbf68865499a69ccd3bf`. `meta`:
  `n_steady` 7852 = `n_shelled` 7815 + `n_unshelled_steady` 37 (the 37 NORADs listed), `n_transient`
  1832, shell grouping `inc_gap` 0.15 deg, `alt_gap` 3.0 km, `min_pop` 20, steadiness criterion
  `rate_steady_kmday` 0.1; `shells[]` each with `inc`, `core_alt` and its `norads`. `coverage/universe.py`
  asserts the 7852 = 7815 + 37 invariant and that every steady NORAD is present in the catalogue.

### 3.2 Fleets (S1) and the S3 seeds

Fleet file (`fleets/tour_*.json`): `name`, `tag` ("[EST] ep_tour.fleet sizing; drag NOT priced; dwell 1
rev; chosen = fewest inspectors then shortest campaign"), `sha12`, `run`, `n_inspectors`, `n_targets`,
`n_single`, `n_dead_end`, `dv_max` [m/s], `campaign_d` [d], `groups{inc:alt -> …}`, `inspectors[]`
with `id`, `group`, `lam` [m/s per day, the dv-vs-time weight], `m_max`, `n_legs`, `n_targets`,
`sized_dv` [m/s], `sized_t_d` [d], `t_leg_max_d`, `sha12`, `tour` (repo path of the sized tour, here
under `sized_tours/`).

| fleet file | inspectors | targets | sized dv_max [m/s] | sized campaign [d] | sha12 |
|---|---|---|---|---|---|
| `tour_fleet_v0.json` (f = 1) | 69 | 7852 | 4699.94 | 1825.55 | `c0bd5d935c6e` |
| `tour_fleet_F0.1_s0.json` (f = 0.1) | 17 | 785 | 4626.35 | 1826.19 | `bb25768884ee` |
| `tour_N4_A10_t0.12_e1e+09_r100000_plus21dose_liftall.json` (wing of S3) | 16 | 239 | 4686.04 | 1582.79 | `423f62b6634b` |
| `tour_F0.1_s0_A10_t0.12_e1e+09_r10000.json` (wing of S2) | 1 | 2 | 181.58 | 130.26 | `7f9faef4360d` |

(all values from the respective file's `n_inspectors`, `n_targets`, `dv_max`, `campaign_d`, `sha12`.)

Sized tour (`sized_tours/<fleet>/<inspector>.json`): `lam`, `group`, `unit`, `inspector`, `n_targets`,
`served`, `dv_total` [m/s], `t_total_d`, `stop`, `dead_end`, `t_leg_max_d`, `m_max`, `legs[]` with
`frm`, `to` (NORAD), `how`, `node_gap_deg`, `dv_leg`, `dv_serve` [m/s], `T_d`, `da_d_km`, `di_d_deg`,
`t_d`, `dv_cum`, `mass` [kg]. Inspectors with a single target have no legs and no flown directory.

Cases: `cases/tour_N4_A10_t0.12_e1e+09_r100000_plus21dose.txt` — 239 NORAD ids (non-comment lines):
the 220 ids not covered by the S3 fleet under the detector criterion encoded in the name, plus the
objects whose dose under the survey firing rule exceeds 0.25 Gy (file header).
`cases/tour_F0.1_s0_A10_t0.12_e1e+09_r10000.txt` — 2 ids, the satellites the S2 drifter did not reach
(`drifter_F01_payload.json` meta `unreachable` [62743, 63426]).

`place5_band_asflown.json` (S3 seeds; sha256 `948bd0c6c7b421a071db329830a90e62cd0ef2ca660e054fef87f17c1a7caf84`,
equal to `fleet_sha256` in the `encounters_N4.npz` provenance): `meta` (`inc_deg` 53.16, `seed_alts_km`
[358, 486, 552, 573, 490], `raans_deg` [0, 90, 180, 270, 45], `n_seeds` 5) and `seeds[]` with
`seed_id`, Keplerian `a_m`, `e`, `i_rad`, `raan_rad`, `argp_rad`, `nu_rad`, `mass_kg` 260.0, `cd` 2.2,
`area_m2` 2.0, `mode` "drifter", `da_m`. The N4 record uses four of the five (`place_a490_r45` dropped,
`encounters_N4.npz` provenance `dropped`/`kept`).

### 3.3 Encounters (S2, S3)

Load with `numpy.load(path, allow_pickle=True)`; `provenance` is a JSON string (0-d array).

`encounters_N4.npz` — 84,546,416 bytes, sha256 `44b49b2e8e29dc09598d87d970c8d58d7e2eff5f9112a77b0647145b98d7f9d6`.
230944 rows. Arrays: `inspector_names` (4), `inspector_idx`, `norad`, `min_dist_km`, `tca_min` [minutes
after the mission epoch], `tca_utc` [ISO-8601 to 1 us], `vrel_kms`, relative position at TCA `dpx dpy dpz`
[km], velocities `vix viy viz`, `vjx vjy vjz` [km/s], inspector position `six siy siz` [km], radii
`ri_km`, `rj_km`, osculating elements of both bodies at TCA `elem_{i,j}_{a_km,e,i_rad,raan_rad,argp_rad,nu_rad,period_s}`;
`frame` "TEME" (positions/velocities), `elements_frame` "EME2000" (provenance `frame`, `elements_frame`).
Provenance (verbatim fields): `derived_by` targeting/survey_subset.py, `git_commit`
`79060d0966836ba2d0e27f09e15e7d6a4f954414`, `source` data/placement_study/encounters_N5.npz,
`source_sha256` `06cba6119e5604c1956714634872818044f9fca3066ed1a5728f26792d6a6055`, `dropped`
[place_a490_r45], `subset_seed_file` conops/fleets/minimal4_band.json; `source_provenance`:
`run_git_commit` `2a5648e0b36cdc2f242374160ad75ef06bc72280`, `catalogue_sha12` 5d5748ef7886, `gravity`
[4, 4], `horizon_s` 157680000.0, `coarse_dt_s` 250.0, `capture_km` 12.0, `x_km` 8.0, TCA refinement
scipy bounded minimize_scalar with `xatol_min` 1e-08, `n_encounters` 354804 (of the N5 source).
`tag` "[FLOWN] rows of the source run, subset".

`encounters_drifter_F0.1_s0.npz` — 334,998 bytes, sha256 `88e62a726cbee2c9c11d0de94cb2d397a540eacfc87441f4df71998a5e06b3a0`.
783 rows, same geometry arrays as above (no `elem_*`; provenance `fields_missing_vs_survey`), plus the
two nudge arcs of each pass: `arc{1,2}_t_abs_d` [mission day], `arc{1,2}_dur_s`, `arc{1,2}_mass_kg`
(ignition mass), `arc{1,2}_prop_kg`, `arc{1,2}_dir_tnw` (unit vector, TNW). Provenance: `run_dir`
fig_scratch/hybrid/d00_ladder_full, `run_git_commit` `a1e8b0a1b723aba6951a7c31db575b45a2b21107`,
`seed_tag` f01_soonest_v3_d00, `tagged_list` fig_scratch/randomF/lists/randF0.1_s0.txt (`tagged_sha256`
`edce04f04a32ebf76a00d966b2234eada8fdf30ad743fb111746956d80c7140d`, `n_tagged` 785), `catalogue_sha12`
5d5748ef7886, `capture_km` 50.0, `x_km` 0.4, `caps_lifted` false, `retire_reason` "3 consecutive hops
without an intervening pass"; `ledger`: `dv_nudge_ms` 2311.06, `dv_hop_ms` 434.40, `dv_drag_ms_EST`
225.26, `dv_reserve_ms` 300.0, `dv_total_ms` 3270.72, `dv_budget_ms` 5000.0, `t_used_d` 1805.53,
`t_cap_d` 1825.0, `n_nudges` 771, `n_hops` 38, `max_nudge_ms` 18.79, `n_served` 783, `n_unreachable` 2;
`source_npz_sha256` `50a8f3d21b784a6f418cbfad03742e8fa1c424ff817b19a9f4cc206276c57c48`, `exported_by`
fig_scratch/hybrid/drifter_encounters_export.py, `export_git_commit`
`3941a893cfcf9679ce67b7828cbbccdf1072d44d`; `tag` "[FLOWN] recorder's own TEME states at each flown TCA".

### 3.4 Flown S1 records

Per run (`flown/<run>/`, from `fleet_summary.json` and `ephem_manifest.json`):

| run | fleet | inspectors (with legs) | legs | MAX dv [m/s] | MAX t [d] | stuck | archives (bytes) |
|---|---|---|---|---|---|---|---|
| `v0_v36` | tour_fleet_v0 | 69 (61) | 7783 | 4906.63 | 1821.99 | 0 | 61 (2,312,140,185) |
| `F0.1_s0_v36` | tour_fleet_F0.1_s0 | 17 (17) | 768 | 4572.06 | 1810.17 | 0 | 17 (367,174,889) |
| `N4_plus21dose_v36` | …plus21dose_liftall | 16 (13) | 223 | 4969.34 | 1552.10 | 0 | 13 (143,333,013) |
| `drifter_F0.1_wing_v36` | tour_F0.1_s0_A10_t0.12_e1e+09_r10000 | 1 (1) | 1 | 174.98 | 133.68 | 0 | 1 (1,786,291) |

(`n_done`, `n_stuck`, `dv_max`, `t_max_d` from `fleet_summary.json`; inspectors with legs, leg counts
and bytes summed over `ephem_manifest.json` `inspectors{}`; `n_legs` there equals the count of
`closest_approach.json` entries.)

* `fleet_summary.json`: `fleet`, `fleet_sha12`, `n_inspectors`, `n_done`, `n_stuck`, `stuck[]`,
  `results[]` (`id`, `status`, `dv` [m/s], `t_d`, `legs`, `worst_leg` [m/s], `wall_s`), `dv_max`,
  `t_max_d`, `worst_leg`, `dv_sum`.
* `ephem_manifest.json`: `run`, `archive_dir`, `inspectors{id -> archive, sha256, bytes, n_legs,
  legs[] (leg file names), packed_utc}` — the sha256 of every 60-s ephemeris archive (section 7).
* `closest_approach.json`: one entry per leg: `terminal{range_m, t_s, R, T, N, ahead, n}` (the minimum
  chaser–target range over the terminal stage, RTN components in m, `t_s` seconds after the mission
  epoch, `n` rows scanned), `before{…}` (same over the approach before hand-off), `leg` (leg file),
  `t_split_s`, `sample_s` [600.0, 60.0], `ephemeris_src{archive, sha256}`.
* `<inspector>/summary.json`: `provenance` (section 2 fields plus `sized_tour`, `sized_tour_sha256`,
  `lam_mps_per_day`, `catalogue_sha12`, `mission_epoch_utc`, `target_path`, `source_sha256{14 files}`,
  `di_grid_deg`, `replan_fracs`, `n_rev_ladder`, `t_leg_max_rule`, `leg_boundary`, `of_date_frame`
  "TEME", `platform`, `python`, `numpy`), `n_legs_sized`, `n_legs_flown`, `stopped`, `cum{dv_mps,
  cadence_s, sized_T_s}`, `sized_totals{dv_mps, T_d}`, `legs[]` (same records as the checkpoint).
* `<inspector>/checkpoint.json`: `sized_tour`, `sized_tour_sha256`, `lam_mps_per_day`, `order[]`
  (NORADs served, start first), `n_legs`, `next_leg`, `t_dep_s`, `chaser{r_m, v_ms, mass_kg}` (state
  after the last leg, EME2000), `start_construction` ("target <n> ref-sgp4 state at t=0, displaced
  150.0 m along -T (RTN along-track), velocity unchanged"), `cum`, `stopped`, `legs[]` with per leg:
  `leg`, `frm`, `to`, `t_dep_s`, `t_dep_d`, `target_seed_utc`, sized values (`sized_dv_leg_mps`,
  `sized_dv_serve_mps`, `sized_T_d`, `sized_T_leg_d`, `sized_node_gap_deg`, `sized_da_d_km`), replan
  estimates, flown values (`flown_dv_arc1_mps`, `flown_dv_trims_mps`, `flown_dv_arc2_mps`,
  `flown_dv_leg_mps`, `flown_dv_terminal_mps`, `flown_dv_total_mps`, `flown_T_leg_d`,
  `flown_T_total_d`, `cadence_d`, `slip_d`), geometry at hand-off (`node_gap_deg`, `phase_gap_deg`,
  `a_d_minus_a_k_km`, `i_d_minus_i_k_deg`, `handoff_sep_km`, `handoff_a_roe_m`, `handoff_a_de_km`),
  terminal (`terminal_n_rev`, `terminal_iterations`, `terminal_dv_mps`, `hold_min_m`, `hold_max_m`,
  `keepout_m`, `keepout_side`, `term_min_sep_m`, `term_min_sep_t_s`, `drift_m_per_rev`), `mass_kg`
  (end of leg), `wall_s`, `timing_s`, `artifact` (repo path of the leg file), `reanchor{rel_rtn_m,
  rel_rtn_ms, flown_target_minus_catalogue_km, chaser_shift_km}` (section 6).
* The per-leg records `leg_*.json` (plan, arcs, replans, hand-off and end states, terminal LP; ephemeris
  stripped) are not shipped here; they are in the repo under `artifacts/tour_fleet_flown/<run>/<inspector>/`
  (7783 / 768 / 223 / 1 files for v0 / F0.1_s0 / N4 wing / drifter wing).

### 3.5 Atlas payloads (`../payloads/`, not duplicated here)

Built by `fig_scratch/hybrid/tour_payload.py` (per inspector), `fleet_payload.py` (per fleet),
`globe_payload.py` (S2 drifter), `arm_payload.py` (S3 survey) and `catalogue_payload.py`.

Common conventions. Frame: TEME throughout; the co-orbit records are EME2000 and are rotated to TEME
by Orekit's own frame transform (`tour_payload.py` docstring; tour meta `tag`). Time: `t`, `t0`, `t1`
and all `*_d` fields are mission days from the common epoch 2026-03-25T21:25:17.146 UTC
(`catalogue.json` meta `epoch`); `utc` strings are the same instants. Positions `ri`, `rt` [km] are
rounded to 0.1 km = 100 m; velocities `vi`, `vt` [km/s] to 1e-5; `el_*` = osculating
[a km, e, i rad, RAAN rad, argp rad, true anomaly rad] with a to 1 m and the rest to 1e-7, `per_*`
Keplerian period [s] to 0.01; `gmst` prime-meridian right ascension in TEME [rad]; `sun` unit vector
in TEME; `alt` = |r| - 6378.137 km (`re_km`). (`tour_payload.py` lines 139–223, `arm_payload.py`
167–175, `globe_payload.py` 188–200.)

* `insp/<run>/<inspector>.json` (kind "tour"): `meta` (`git`, `catalogue`, `sized_tour`, `archive{sha256,
  bytes, n_legs, manifest}` — the archive hash was recomputed and required to equal the manifest,
  `keepout_m`, `n_legs`, `n_targets`, `dv_total_ms`, `t_total_d`, `dv_sized_ms`, `t_sized_d`,
  `dv_worst_ms`, `stride_s` 21600.0, `sample_s_leg`, `sample_s_terminal`, `legs[]{t0, t1, dv, frm, to}`,
  `burn_kinds` ["arc1", "trim_after_arc1", "trim_coast_30pct", "trim_coast_10pct", "trim_coast_3pct",
  "arc2", "terminal"], `burn_stats`, `n_tgt_rows`); `events[]` one per leg at the recorded end of the
  terminal: `n` (target), `frm`, `leg`, `t`, `utc`, `miss`/`nat` [km, the hold separation], `hand_d`,
  `dep_next_d`, `ca{r [m], s [s from arrival], rtn [R, T, N m], src}` (recorded closest approach of the
  terminal window), `dv`, `dv_leg`, `dv_term`, `dv_sized` [m/s, 2 decimals], `T`, `T_sized`, `t_dep` [d],
  `node_gap` [deg], `phase_gap` [deg], `da` [km], `di` [deg], `hold` [min, max m], `mass` [kg],
  `n_arcs`, `reanchor_km`, `rel[]` rows [s from arrival, along-track m, radial m, cross-track m] in the
  target's RTN, 1 decimal, every 60-s record within one revolution of arrival and every fifth (300 s)
  elsewhere until the next departure; `ri`, `rt`, `vi`, `vt`, `gmst`, `sun`, `el_i`, `el_t`, `per_i`,
  `per_t`. `track[]` chaser rows {`t`, `el`, `per`}: one recorded row per 6 h of drift (`stride_s`
  21600) plus the row at each event and the first recorded row inside every thrust arc; stops at the
  next leg's departure. `tgt[]` per leg {`n`, `leg`, `rows[] [t_d, el, per]`} the target's recorded
  rows at the same stride (first row = the seed at departure). `burns[]` every finite-thrust arc:
  `[t0_d, t1_d, dR, dT, dN, dv_mps, mass_kg, leg, kind]` — start/end mission day (7 decimals),
  unit thrust direction in the chaser's RTN (Orekit QSW: R radial, T along-track, N normal; 4
  decimals), the recorded propellant-derived arc dv (6 decimals), chaser mass at the last recorded
  row at or before ignition (3 decimals), leg index, index into `meta.burn_kinds`. `hops` is empty for
  tours.
* `fleet_*_events.json`, `wing_*_events.json` (kind "fleet", mode "flown"): `meta` (`run`, `git`,
  `fleet_sha12`, `n_sats`, `n_flown`, `n_stuck`, `n_serves`, `max_dv_ms`, `max_t_d`, `dv_total_ms`,
  `worst_leg_ms`, sized counterparts, `groups{}`, `terminal{n_legs, min_m, med_m, max_m,
  n_inside_100m, n_inside_10m}`, `keepout_m`, `flown_dir`, `reanchor{…}` (section 6),
  `max_dv_inspector`, `max_t_inspector`); `events[]` one per serve: `n`, `t`, `utc`, `who`
  (inspector id), `leg`, `miss`/`nat` [km], `dv`, `T`, `dv_term`, `dv_sized`, `T_sized`, `hold`,
  `node_gap`, `da`, `mass`, `cdv` (cumulative dv), per-inspector totals `sat_dv`, `sat_serves`,
  `sat_t`, `sat_dv_sized`, `sat_t_sized`, `fam` (inc:alt group), `gmst`, `ri`, `el_i`, `per_i`.
  Positions here are the catalogue (SGP4) state of the target at the serve epoch, not the recorded
  ephemeris (meta `tag`); `hops` empty.
* `drifter_F01_payload.json` (kind "hybrid", S2): `meta` (`git`, `catalogue`, `tagged_list`,
  `n_served` 783, `n_targets` 785, `unreachable`, `ledger{…}`, `platform{thrust_N, isp_s, mass_kg, cd,
  area_m2, budget_ms, mission_d, dv_reserve_ms, cruise_floor_km}`, `band`, `aim`, `burn_stats`);
  `events[]` one per pass: `n`, `t`, `t_plan`, `utc`, `miss` [km, 4 decimals], `nat` [natural miss
  without the nudge, km], `vrel` [km/s], `dv` [nudge m/s], `burn`, `a1`, `a2` [arc durations s],
  `free`, `lead` [d], `alt`, `prop` [kg], `cdv` [cumulative m/s], `ri`, `rt`, `dp` [relative position
  km, 1e-5], `vi`, `vt`, `gmst`, `sun`, `el_i`, `el_t`, `per_i`, `per_t`; `hops[]` {`t`, `frm`, `to`
  [altitude km], `dv`, `dur` [d]}; `burns[]` and `hop_burns[]` `[t_start_d, t_end_d, sign, dv_mps,
  mass_kg, index]` with `sign` ±1 along the velocity, `index` the pass (or hop) served; the whole nudge
  dv is booked on the first arc of a pass and the ignition mass restarts at the platform mass each leg
  (`globe_payload.py`, `burn_arcs` docstring).
* `survey_N4_events.json` (kind "survey", S3): `meta` (`source_npz`, `source_sha256`, `npz_provenance`,
  `n_targets` 7833, `n_encounters` 230944, `drifters[]`, `cov{threshold km -> count}`, `cov_curve`,
  `miss_med`, `miss_max`); `events[]` one per target (its closest approach of the mission): `n`, `t`,
  `utc`, `miss`/`nat` [km], `vrel`, `alt`, `who` (drifter), `ri`, `rt`, `dp`, `vi`, `vt`, `gmst`, `sun`,
  `el_i`, `el_t`, `per_i`, `per_t`; dv fields are 0 (no manoeuvres).
* `catalogue.json` (kind "catalogue"): `sats[]` `[norad, a km, i rad, RAAN0 rad, u0 rad, RAAN_dot
  rad/day, u_dot rad/day]`, u = argument of latitude; the two rates are least-squares fits to the
  reference SGP4 trajectory over the first 200 days (`fit_days`), circular track (catalogue e < 0.002);
  `spin` [GMST at epoch rad, rate rad/day]; `sun[]` daily TEME unit vectors (`sun_step_d` 1.0, 1826
  rows); `gate_km{day -> [median, p95, max]}` error of the fitted track against SGP4, e.g. at 1825 d
  58.56 / 161.95 / 213.96 km (`catalogue.json` meta). This layer is a drawing aid; check targets
  against the TLE file, not against it.

## 4. What can be checked independently

* **Arc dv sums vs the ledger.** For any inspector, the sum of `dv_mps` over `burns[]` in its payload
  equals `meta.dv_total_ms`, the checkpoint `cum.dv_mps`, and the sum of `flown_dv_total_mps` over its
  `legs[]`; per leg, `flown_dv_arc1 + flown_dv_trims + flown_dv_arc2 = flown_dv_leg` and
  `flown_dv_leg + flown_dv_terminal = flown_dv_total` (`checkpoint.json`). Fleet totals: `dv_sum`,
  `dv_max` in `fleet_summary.json`.
* **Rocket equation per arc.** With `thrust_N` 0.17 and `isp_s` 1500.0 (`summary.json` provenance),
  mass flow = thrust / (Isp g0); each burn tuple gives `t1 - t0` (days) and the ignition `mass_kg`, so
  the propellant and dv of every arc follow and can be compared with `dv_mps`. `tour_payload.py`
  itself checks the terminal arcs this way against the recorded mass column (lines 119–131).
* **J2 propagation.** From any recorded state (payload `track` elements at a row; or the departure
  state of section 5) propagate with J2 only (`gravity_degree_order` [2, 0], `mu_m3s2`, `ae_m`, `j2`
  from the provenance) through the listed arcs (constant thrust along the RTN direction given) to the
  next recorded row or event.
* **Hold at 150 m, closest approach >= 100 m, no station crossing.** From the `rel` rows of each
  event: the separation holds near 150 m along-track (`hold` [min, max] in m; `trail_m` 150.0), the
  norm never goes below `keepout_m` 100.0 (`closest_approach.json` `terminal.range_m`; fleet meta
  `terminal.n_inside_100m` is 0 in all four runs), and the along-track component keeps one sign
  through the terminal window (no station crossing; `keepout_side` in every leg record).
* **Fly-by miss and relative speed** from the two states: for every row of the npz files,
  |`dp`| = `min_dist_km` and |`vi - vj`| = `vrel_kms`; the same from `ri`, `rt`, `vi`, `vt` in the
  survey and hybrid payload events (to their rounding).
* **Targets vs SGP4 from the TLE file.** Every target state at a catalogue-clock instant (`rt`/`vt`
  of a fly-by event; the fleet events' `ri`; the first `tgt` row of each co-orbit leg; `target_r_m`/`target_v_ms`
  in the checkpoint's start construction) is SGP4 (WGS72) of the shipped TLE at `tca_utc`/`utc`,
  TEME, from the mission epoch.

## 5. Re-flying one leg

A leg is reproduced by `coorbit/tour_flight.py` (`python -m coorbit.tour_flight --tour <sized tour>
--out <dir>`, `--resume` to continue; fleet-wide `python -m coorbit.fleet_flight --fleet <fleet json>
--out <dir>`; module docstrings) at the recorded commit with the recorded `source_sha256`. The
inputs are all shipped:

* the sized tour `fleets/sized_tours/<fleet>/<inspector>.json` (pinned by `sized_tour_sha256` in the
  checkpoint) gives the order of targets and the plan each leg started from (`legs[]`);
* the catalogue TLE gives every target seed: `target_seed_utc` in `checkpoint.json legs[k]` is the
  instant at which target `to` is seeded from SGP4;
* the chaser's departure state of leg k is built from shipped fields: for leg 0, the SGP4 state of
  `order[0]` at t = 0 displaced 150.0 m along -T with the same velocity and mass 300.0 kg
  (`start_construction`; `mass0_kg`); for leg k > 0, the SGP4 state of target `legs[k-1].to` at
  `legs[k].t_dep_s`, plus the relative state `legs[k-1].reanchor.rel_rtn_m` / `rel_rtn_ms` re-composed
  on that target's RTN triad (rows R = r/|r|, N = r x v normalised, T = N x R; `coorbit/tour_flight.py`
  `_rtn`, `reanchor`), with mass `legs[k-1].mass_kg`.

The departure, hand-off and end states as flown (`departure.chaser_r_m` etc.) are also in the repo's
`leg_*.json` records.

## 6. Known limitations

* **Stride.** The co-orbit payload `track` carries one recorded row per 6 h of drift (`stride_s`
  21600.0); within an arc only the first row is guaranteed. The full record is 600 s in the leg and
  60 s in the terminal (`sample_s_leg`, `sample_s_terminal`), and lives in the archives (section 7).
  `rel` rows are complete at 60 s within one revolution of arrival and thinned to 300 s elsewhere;
  the builder prints the interpolation error of the thinned rows against the 60-s record.
* **Rounding.** Payload positions are rounded to 100 m, velocities to 1e-5 km/s (section 3.5); the
  npz files and the flown records are unrounded doubles.
* **Frame.** Everything on the page is TEME (the SGP4 native frame); the flown records are EME2000
  and were rotated by Orekit. The elements in `encounters_N4.npz` are EME2000 (`elements_frame`).
* **Leg-boundary re-anchor.** Inside a leg the target is the Orekit copy of its SGP4 seed and walks
  away from the catalogue over the leg; at each leg boundary the chaser is re-placed relative to the
  served target's catalogue state, carrying the relative hold state across (`summary.json` provenance
  `leg_boundary`; `tour_flight.py` `reanchor` docstring). The step the chaser takes is recorded per
  leg as `reanchor.chaser_shift_km` and summarised in the fleet-level payload meta `reanchor`:

  | run | legs | median [km] | p95 [km] | max [km] | > 100 km | > 1000 km |
  |---|---|---|---|---|---|---|
  | `v0_v36` (`fleet_v0_v36_events.json`) | 7783 | 7.01 | 26.48 | 668.39 | 3 | — |
  | `F0.1_s0_v36` (`fleet_F01_v36_events.json`) | 768 | 12.21 | 71.29 | 1765.04 | 31 | 2 |
  | `N4_plus21dose_v36` (`wing_N4_v36_events.json`) | 223 | 9.76 | 210.39 | 1875.07 | 19 | 3 |
  | `drifter_F0.1_wing_v36` (`wing_F01_v36_events.json`) | 1 | 88.21 | 88.21 | 88.21 | 0 | 0 |

  The payload `track` of an inspector therefore jumps by that amount at each leg boundary; the flown
  leg itself is continuous and the hold geometry is preserved to O(1e-3) (`reanchor` docstring).
* **Sized numbers are estimates.** All `sized_*` fields and the fleet files are sizer output
  ("[EST]"); only the `flown_*` fields and the records are flown.
* **Drag.** The S1 legs are J2 only; the S2 drifter's drag make-up is an estimate
  (`dv_drag_ms_EST`); the S3 drifters were flown with drag on (section 2).

## 7. Full ephemerides

The 60-s ephemeris archives — one `tar.gz` per inspector holding the per-leg records with their
chaser and target rows (EME2000, 600 s in the leg, 60 s in the terminal) — are not in this package.
Their sha256 and sizes are in `flown/<run>/ephem_manifest.json`: 92 archives, 2,824,434,378 bytes in
total (sum of `bytes`), of which `v0_v36` alone is 2,312,140,185 bytes. They are available on request
from the author.

## 8. Licence and contact

Contact: Patrick Huber, pahuber@vt.edu. This package is published in the repository
https://github.com/pahuberVT/ost-verification under the GNU General Public License v3.0 (its LICENSE
file). Archived on Zenodo: DOI 10.5281/zenodo.23108549 (https://doi.org/10.5281/zenodo.23108549), record of
GitHub release v1.0 (2026-10-02); later releases become new versions under the same concept DOI. Cite the DOI
and the page build commit given in `../manifest.json` (`code_commit`).
