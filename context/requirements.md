# Requirements

* Single budget **S**; enforce t0 parity (Invest gets Buy closing spend).
* Invest contrib: `max(0, S − rent_t)`; Buy-liquid contrib: `max(0, S − housing_outflow_t)`.
* Housing outflow: P\&I, taxes, maintenance, insurance, HOA, PMI/MIP.
* Toggles: FHA vs Conventional, finance vs pay-cash upfront MIP, tax base current vs original, real-dollars display.
* Outputs: P10/P50/P90 bands; P(Invest>Buy) at T; city overlay medians; Baseline Snapshot overlay + deltas.
* Perf: default (5k paths, 30y) in a few seconds; fixed seed reproducible.
