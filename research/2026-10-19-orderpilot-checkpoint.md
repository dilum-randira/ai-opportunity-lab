# OrderPilot — 2026-10-19 engineering and validation checkpoint

## Status
This note records work prepared offline on 2026-10-19. It does **not** imply the offline source changes have been merged. The full candidate package remains outside the repository pending review and integration.

## Candidate changes requiring integration
- Add a merchant pilot decision gate that distinguishes synthetic scenarios from consented real-world measurements.
- Assess processing time, error rates, proposed subscription prices, merchant interest, and operating costs before calling a paid pilot ready.
- Correct the unit-economics break-even calculation so fractional messaging quantities are rounded conservatively.
- Correct a research protocol example filename.

## Offline verification (not GitHub CI)
The prepared candidate was reported to pass 24 offline tests and 221 deterministic randomized scenarios. These are historical offline results, **not** proof that the current repository passes after integration. Re-run all tests and CI before merge.

## Commercial validation hypotheses
Illustrative, not measured: 520 orders/month × 60 seconds saved/order × LKR 400/hour = LKR 3,466.67/month of modeled labor value. At LKR 2,500/month subscription, modeled gross difference is LKR 966.67 before additional operating costs. Do not present this as customer ROI or validated willingness to pay.

## Next steps
1. Compare the offline candidate files against current main, preserving existing changes.
2. Review rounding logic and add regression tests for boundary conditions.
3. Integrate the pilot decision gate and CLI with documented input schema.
4. Run the complete repository test suite and GitHub CI.
5. Collect consented data from five prospective merchants, with explicit measurement provenance.
6. Verify merged code on main by fetching file contents at the resulting commit SHA.

## Publication integrity
This checkpoint is documentation only. Source files, regression tests and integration changes described above must not be claimed as published until fetched and verified on main.
