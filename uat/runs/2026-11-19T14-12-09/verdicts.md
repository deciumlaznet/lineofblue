# Verdicts: Line of Blue demo UAT, 19 Nov 2026 14:12

**Result:** 291 steps across 16 persona and viewport runs. The first full run had 2 failures, both the same mobile overflow on the L.O.B Agent screen: the quick-prompt buttons did not wrap. After the CSS fix, the two affected runs were re-run (run 14-13-29, `role-agent-user` and `tour-mobile`, desktop and mobile) with 0 failures. No console errors, HTTP errors or blank pages.

| Screen | Verdict | Notes |
|---|---|---|
| radar-nar01, cascade-receipts, decision-log, sc01-complete | Pass | Same as the 13:46 run. |
| agent-plan (SC-07) | Pass | Timed plan for five likely rumours, cites KB-ISD24 and KB-HMIC24 in the text plus each playbook's sources, offers a NAR-01 pre-bunk that names no one, and says people decide. |
| national-picture (SC-07) | Pass | Velocity lines for the five largest claims with a legend and a "now" marker. In the race chart NAR-04 shows "line out 84 min ahead" in green, and the others show no line yet in red. Map labels sit beside the dots, with some overlap at Port Ellery (known since v1, minor). |
| agent-check (desktop and mobile) | Pass | For the risky holding statement: "Not yet", with the must-fix items (named suspect, contempt, immigration), what to do instead, and KB-APP, KB-ART8, KB-CCA81, KB-ETHNAT and KB-DEFAM cited. It wraps cleanly at phone width after the fix. |
| pcc-inbox, tour-end | Pass | Unchanged. |

**New coverage:**
- SC-07 "Get ahead" proves the pre-bunk can go through the full Golden Hour sign-off (legal, SIO, Gold) at 13:50, 84 minutes before the first spoof notice.
- The agent is tested in offline mode (no Claude in a standalone browser).
- In the published artifact the same screen uses Claude with the same knowledge base. That path needs a manual check, because it depends on the viewer's consent.
