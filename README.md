# ost-verification
Orbit and other data related to OST verification in space

## Orbit Mission Atlas

Interactive atlas of the flown inspection fleets of the paper *Verification of the Outer Space Treaty with
active interrogation* (P. Huber): https://pahuberVT.github.io/ost-verification/

Four tabs: Hybrid f = 1 (4 S3 passive fly-by platforms + 16 S1 co-orbit platforms), S2 routed fly-by f = 0.1
(+ 1 S1), S1 co-orbit f = 1 (69 platforms), S1 co-orbit f = 0.1 (17 platforms). Every trajectory shown is a
flown Orekit record; the numbers in the page come from the shipped files, never typed.

## Data package

`data/README.md` documents everything shipped for an independent check of the orbit calculations: the TLE
catalogue, the fleet files and sized tours, the encounter files the detection analysis consumes, the flown
records (summaries, checkpoints, closest approaches, archive hashes) and the schema of the per-platform
payloads under `payloads/`. The 60 s ephemeris archives (2.8 GB) are available from the author on request.

