# Verdicts: run 2026-11-19T16-33-35 (320 steps, 13 personas, desktop and mobile)

**Result:** 2 failures, both the same check. Fixed and rerun as 2026-11-19T16-35-09 with **0 failures**.

| Finding | Cause | Fix |
|---|---|---|
| National map, Cumbria: "Sellafield" missing from "Who else may need to act nearby" (desktop and mobile) | The nearby radius was 45 km. Sellafield is about 50 km from the Cumbria HQ point. | `nearby(force, km = 70)` in `app/app.js`. |

## Judged screens (rerun)
- **National map:** a recognisable UK and Ireland coastline, 45 force HQs, BTP hubs, CNC, MDP, service police and port layers, each with its own mark and a toggle. Real versus synthetic is labelled above the map and in the caption. On mobile it fits the width and the area panel and table read cleanly. Pass.
- **Workflows and autonomy:** seven lanes and 28 cards, each coloured by autonomy level, with a live status pill and the person who signs off. The mix bar and legend read without colour alone (counts are printed). The PCC persona sees the "only the Head of NPCC Communications can change a level" note and no level selector. Pass.
- Note: the mix shows 7 fully agentic in the PCC screenshot because the earlier step in the same persona changed W1.3 to fully agentic as nc-head; this is the intended audit test, not a data fault.
