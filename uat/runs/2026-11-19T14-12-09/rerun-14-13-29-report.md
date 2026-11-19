# UAT: Line of Blue synthetic demo (NPCC Communications)

Run 2026-11-19T14:13:29.123Z against http://127.0.0.1:8765 (paid actions skipped).

## Summary

| Persona | Viewport | Scenarios | Page findings | Console / page errors | HTTP errors | Blocked by guardrail |
|---|---|---|---|---|---|---|
| Analyst and press officer using the L.O.B Agent | desktop | ✅ agent | 0 fail | 0 | 0 | 0 |
| Analyst and press officer using the L.O.B Agent | mobile | ✅ agent | 0 fail | 0 | 0 | 0 |
| Smoke tour of every screen | desktop | ✅ tour | 0 fail | 0 | 0 | 0 |
| Smoke tour of every screen | mobile | ✅ tour | 0 fail | 0 | 0 | 0 |

## Analyst and press officer using the L.O.B Agent · desktop

### ✅ Ask, cite, check a draft
- ✅ 1. `goto` {"path":"/#governance"}
- ✅ 2. `click` {"testid":"reset"}
- ✅ 3. `select` act as nc-insight
- ✅ 4. `goto` {"path":"/#agent"}
- ✅ 5. `fill` {"css":"#agentQ"} = "UAT synthetic: which guidance covers Welsh language duties for a bilingual rebuttal?"
- ✅ 6. `click` {"testid":"agent-ask"}
- ✅ 7. `waitFor` {"ms":800}
- ✅ 8. `expectText` {"text":"KB-WELSH"}
- ✅ 9. `expectText` {"text":"Offline playbook answer"}
- ✅ 10. `select` act as nm-press
- ✅ 11. `goto` {"path":"/#safe-to-say"}
- ✅ 12. `click` {"testid":"example-1"}
- ✅ 13. `waitFor` {"ms":600}
- ✅ 14. `goto` {"path":"/#agent"}
- ✅ 15. `click` {"testid":"agent-quick-check"}
- ✅ 16. `waitFor` {"ms":800}
- ✅ 17. `expectText` {"text":"Not yet"}
- ✅ 18. `expectText` {"text":"KB-CCA81"}
- ✅ 19. `judge` {"name":"agent-check","prompt":"L.O.B Agent: when asked about a risky draft, does it say what must be fixed, why, and cite the relevant law or guidance?"} — shots/004-role-agent-user-desktop-agent-check.png

## Analyst and press officer using the L.O.B Agent · mobile

### ✅ Ask, cite, check a draft
- ✅ 1. `goto` {"path":"/#governance"}
- ✅ 2. `click` {"testid":"reset"}
- ✅ 3. `select` act as nc-insight
- ✅ 4. `goto` {"path":"/#agent"}
- ✅ 5. `fill` {"css":"#agentQ"} = "UAT synthetic: which guidance covers Welsh language duties for a bilingual rebuttal?"
- ✅ 6. `click` {"testid":"agent-ask"}
- ✅ 7. `waitFor` {"ms":800}
- ✅ 8. `expectText` {"text":"KB-WELSH"}
- ✅ 9. `expectText` {"text":"Offline playbook answer"}
- ✅ 10. `select` act as nm-press
- ✅ 11. `goto` {"path":"/#safe-to-say"}
- ✅ 12. `click` {"testid":"example-1"}
- ✅ 13. `waitFor` {"ms":600}
- ✅ 14. `goto` {"path":"/#agent"}
- ✅ 15. `click` {"testid":"agent-quick-check"}
- ✅ 16. `waitFor` {"ms":800}
- ✅ 17. `expectText` {"text":"Not yet"}
- ✅ 18. `expectText` {"text":"KB-CCA81"}
- ✅ 19. `judge` {"name":"agent-check","prompt":"L.O.B Agent: when asked about a risky draft, does it say what must be fixed, why, and cite the relevant law or guidance?"} — shots/004-role-agent-user-mobile-agent-check.png

## Smoke tour of every screen · desktop

### ✅ Every workspace renders
- ✅ 1. `goto` {"path":"/#inbox"}
- ✅ 2. `expectText` {"text":"Synthetic demo."}
- ✅ 3. `goto` {"path":"/#picture"}
- ✅ 4. `expectText` {"text":"Synthetic demo."}
- ✅ 5. `goto` {"path":"/#radar"}
- ✅ 6. `expectText` {"text":"Synthetic demo."}
- ✅ 7. `goto` {"path":"/#agent"}
- ✅ 8. `expectText` {"text":"Synthetic demo."}
- ✅ 9. `goto` {"path":"/#golden-hour"}
- ✅ 10. `expectText` {"text":"Synthetic demo."}
- ✅ 11. `goto` {"path":"/#safe-to-say"}
- ✅ 12. `expectText` {"text":"Synthetic demo."}
- ✅ 13. `goto` {"path":"/#lines"}
- ✅ 14. `expectText` {"text":"Synthetic demo."}
- ✅ 15. `goto` {"path":"/#escalations"}
- ✅ 16. `expectText` {"text":"Synthetic demo."}
- ✅ 17. `goto` {"path":"/#horizon"}
- ✅ 18. `expectText` {"text":"Synthetic demo."}
- ✅ 19. `goto` {"path":"/#scenarios"}
- ✅ 20. `expectText` {"text":"Synthetic demo."}
- ✅ 21. `goto` {"path":"/#audit"}
- ✅ 22. `expectText` {"text":"Synthetic demo."}
- ✅ 23. `goto` {"path":"/#governance"}
- ✅ 24. `expectText` {"text":"Synthetic demo."}
- ✅ 25. `judge` {"name":"tour-end","prompt":"Does the Data and safeguards screen read cleanly at this width with no clipped text?"} — shots/013-tour-mobile-desktop-tour-end.png

## Smoke tour of every screen · mobile

### ✅ Every workspace renders
- ✅ 1. `goto` {"path":"/#inbox"}
- ✅ 2. `expectText` {"text":"Synthetic demo."}
- ✅ 3. `goto` {"path":"/#picture"}
- ✅ 4. `expectText` {"text":"Synthetic demo."}
- ✅ 5. `goto` {"path":"/#radar"}
- ✅ 6. `expectText` {"text":"Synthetic demo."}
- ✅ 7. `goto` {"path":"/#agent"}
- ✅ 8. `expectText` {"text":"Synthetic demo."}
- ✅ 9. `goto` {"path":"/#golden-hour"}
- ✅ 10. `expectText` {"text":"Synthetic demo."}
- ✅ 11. `goto` {"path":"/#safe-to-say"}
- ✅ 12. `expectText` {"text":"Synthetic demo."}
- ✅ 13. `goto` {"path":"/#lines"}
- ✅ 14. `expectText` {"text":"Synthetic demo."}
- ✅ 15. `goto` {"path":"/#escalations"}
- ✅ 16. `expectText` {"text":"Synthetic demo."}
- ✅ 17. `goto` {"path":"/#horizon"}
- ✅ 18. `expectText` {"text":"Synthetic demo."}
- ✅ 19. `goto` {"path":"/#scenarios"}
- ✅ 20. `expectText` {"text":"Synthetic demo."}
- ✅ 21. `goto` {"path":"/#audit"}
- ✅ 22. `expectText` {"text":"Synthetic demo."}
- ✅ 23. `goto` {"path":"/#governance"}
- ✅ 24. `expectText` {"text":"Synthetic demo."}
- ✅ 25. `judge` {"name":"tour-end","prompt":"Does the Data and safeguards screen read cleanly at this width with no clipped text?"} — shots/013-tour-mobile-mobile-tour-end.png

## For review against expectations

Each item is a screen to judge against the profile's expectations. Claude fills in the verdicts in `verdicts.md`.

1. **role-agent-user · desktop** /: L.O.B Agent: when asked about a risky draft, does it say what must be fixed, why, and cite the relevant law or guidance? ([shot](shots/004-role-agent-user-desktop-agent-check.png))

2. **role-agent-user · mobile** /: L.O.B Agent: when asked about a risky draft, does it say what must be fixed, why, and cite the relevant law or guidance? ([shot](shots/004-role-agent-user-mobile-agent-check.png))

3. **tour-mobile · desktop** /: Does the Data and safeguards screen read cleanly at this width with no clipped text? ([shot](shots/013-tour-mobile-desktop-tour-end.png))

4. **tour-mobile · mobile** /: Does the Data and safeguards screen read cleanly at this width with no clipped text? ([shot](shots/013-tour-mobile-mobile-tour-end.png))
