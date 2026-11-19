# UAT: Line of Blue synthetic demo (NPCC Communications)

Run 2026-11-19T14:12:09.546Z against http://127.0.0.1:8765 (paid actions skipped).

## Summary

| Persona | Viewport | Scenarios | Page findings | Console / page errors | HTTP errors | Blocked by guardrail |
|---|---|---|---|---|---|---|
| SC-01 conductor: Golden Hour, 12 actors | desktop | ✅ sc01 | 0 fail | 0 | 0 | 0 |
| SC-02 conductor: spoof curfew and state indicators | desktop | ✅ sc02 | 0 fail | 0 | 0 | 0 |
| SC-03 conductor: mobilisation and referral | desktop | ✅ sc03 | 0 fail | 0 | 0 | 0 |
| SC-04 conductor: lawful opinion at a protest | desktop | ✅ sc04 | 0 fail | 0 | 0 | 0 |
| SC-05 conductor: bilingual flood hoax | desktop | ✅ sc05 | 0 fail | 0 | 0 | 0 |
| SC-05 conductor: bilingual flood hoax | mobile | ✅ sc05 | 0 fail | 0 | 0 | 0 |
| SC-06 conductor: hard blocks | desktop | ✅ sc06 | 0 fail | 0 | 0 | 0 |
| SC-07 conductor: get ahead with the forecast and the L.O.B Agent | desktop | ✅ sc07 | 0 fail | 0 | 0 | 0 |
| Analyst and press officer using the L.O.B Agent | desktop | ✅ agent | 0 fail | 0 | 0 | 0 |
| Analyst and press officer using the L.O.B Agent | mobile | ✅ agent | 1 fail | 0 | 0 | 0 |
| Home Office public safety official (read-only brief) | desktop | ✅ limits | 0 fail | 0 | 0 | 0 |
| PCC office (governance observer) | desktop | ✅ limits | 0 fail | 0 | 0 | 0 |
| PCC office (governance observer) | mobile | ✅ limits | 0 fail | 0 | 0 | 0 |
| Force comms officer from another force | desktop | ✅ limits | 0 fail | 0 | 0 | 0 |
| Smoke tour of every screen | desktop | ✅ tour | 0 fail | 0 | 0 | 0 |
| Smoke tour of every screen | mobile | ✅ tour | 1 fail | 0 | 0 | 0 |

## SC-01 conductor: Golden Hour, 12 actors · desktop

### ✅ Harbourside Market stabbing end to end
- ✅ 1. `goto` {"path":"/#governance"}
- ✅ 2. `click` {"testid":"reset"}
- ✅ 3. `select` act as nm-gold
- ✅ 4. `goto` {"path":"/#golden-hour"}
- ✅ 5. `click` {"testid":"open-cell"}
- ✅ 6. `expectText` {"text":"Open since"}
- ✅ 7. `select` act as nm-press
- ✅ 8. `click` {"button":"/Officers were called/"}
- ✅ 9. `click` {"button":"/Two people were injured/"}
- ✅ 10. `select` act as nm-sio
- ✅ 11. `click` {"css":"[data-testid^='verify-']"}
- ✅ 12. `click` {"css":"[data-testid^='verify-']"}
- ✅ 13. `expectText` {"text":"2/2"}
- ✅ 14. `select` act as nm-press
- ✅ 15. `goto` {"path":"/#safe-to-say"}
- ✅ 16. `click` {"testid":"example-0"}
- ✅ 17. `waitFor` {"ms":600}
- ✅ 18. `expectText` {"text":"No legal or policy risks found"}
- ✅ 19. `click` {"testid":"submit-draft"}
- ✅ 20. `select` act as nm-legal
- ✅ 21. `goto` {"path":"/#golden-hour"}
- ✅ 22. `click` {"testid":"legal-approve"}
- ✅ 23. `select` act as nm-sio
- ✅ 24. `click` {"testid":"sio-approve"}
- ✅ 25. `select` act as nm-gold
- ✅ 26. `click` {"testid":"gold-approve"}
- ✅ 27. `select` act as nm-press
- ✅ 28. `click` {"testid":"publish"}
- ✅ 29. `expectText` {"text":"Published"}
- ✅ 30. `click` {"testid":"clock-30"}
- ✅ 31. `click` {"testid":"clock-30"}
- ✅ 32. `select` act as nc-insight
- ✅ 33. `goto` {"path":"/#radar"}
- ✅ 34. `click` {"testid":"narr-NAR-01"}
- ✅ 35. `expectText` {"text":"False suspect identity"}
- ✅ 36. `click` {"testid":"link-incident"}
- ✅ 37. `judge` {"name":"radar-nar01","prompt":"Narrative Radar at 14:50: is NAR-01 shown as a false claim with velocity, reach, platforms and places, pseudonymised accounts on — shots/005-conductor-sc01-desktop-radar-nar01.png
- ✅ 38. `select` act as nm-gold
- ✅ 39. `goto` {"path":"/#golden-hour"}
- ✅ 40. `expectText` {"text":"false identity claim is spreading"}
- ✅ 41. `fill` {"css":"#discReason"} = "UAT synthetic: a false identity claim is driving tension; confirming nationality is necessary and proportionate."
- ✅ 42. `click` {"testid":"decide-confirm"}
- ✅ 43. `click` {"testid":"ho-request"}
- ✅ 44. `select` act as ho-press
- ✅ 45. `goto` {"path":"/#inbox"}
- ✅ 46. `expectText` {"text":"confirm immigration status"}
- ✅ 47. `click` {"testid":"ho-confirm"}
- ✅ 48. `select` act as nc-duty
- ✅ 49. `goto` {"path":"/#lines"}
- ✅ 50. `click` {"testid":"draft-line"}
- ✅ 51. `select` act as nc-head
- ✅ 52. `click` {"testid":"approve-line"}
- ✅ 53. `select` act as sv-comms
- ✅ 54. `click` {"testid":"ack-line"}
- ✅ 55. `select` act as dg-comms
- ✅ 56. `click` {"testid":"ack-line"}
- ✅ 57. `select` act as km-comms
- ✅ 58. `click` {"testid":"ack-line"}
- ✅ 59. `judge` {"name":"cascade-receipts","prompt":"National lines: do read receipts show the three receiving forces acknowledged (the host force, Northmoor, owns the incident — shots/008-conductor-sc01-desktop-cascade-receipts.png
- ✅ 60. `select` act as eth
- ✅ 61. `goto` {"path":"/#audit"}
- ✅ 62. `expectText` {"text":"Disclosure decision"}
- ✅ 63. `judge` {"name":"decision-log","prompt":"Decision log: does every decision show a named (synthetic) person, a time and the reason, with nothing that profiles a member o — shots/010-conductor-sc01-desktop-decision-log.png
- ✅ 64. `goto` {"path":"/#scenarios"}
- ✅ 65. `click` {"testid":"scenario-SC-01"}
- ✅ 66. `expectHidden` every SC-01 step is ticked
- ✅ 67. `judge` {"name":"sc01-complete","prompt":"Scenario SC-01: are all 14 steps ticked, each naming the actor and organisation?"} — shots/012-conductor-sc01-desktop-sc01-complete.png

## SC-02 conductor: spoof curfew and state indicators · desktop

### ✅ Spoof notice, handover, no attribution
- ✅ 1. `goto` {"path":"/#governance"}
- ✅ 2. `click` {"testid":"reset"}
- ✅ 3. `click` {"testid":"clock-30"}
- ✅ 4. `click` {"testid":"clock-30"}
- ✅ 5. `click` {"testid":"clock-30"}
- ✅ 6. `select` act as nc-insight
- ✅ 7. `goto` {"path":"/#radar"}
- ✅ 8. `click` {"testid":"narr-NAR-04"}
- ✅ 9. `expectText` {"text":"Tier B indicators"}
- ✅ 10. `click` {"testid":"handover"}
- ✅ 11. `select` act as ctp
- ✅ 12. `goto` {"path":"/#inbox"}
- ✅ 13. `click` {"testid":"accept-handover"}
- ✅ 14. `select` act as nm-press
- ✅ 15. `goto` {"path":"/#safe-to-say"}
- ✅ 16. `click` {"testid":"example-2"}
- ✅ 17. `waitFor` {"ms":600}
- ✅ 18. `expectText` {"text":"Public attribution to a state actor"}
- ✅ 19. `expectVisible` submit-draft is disabled for this role
- ✅ 20. `fill` {"testid":"draft-text"} = "UAT synthetic: There is no curfew in Port Ellery. The notice is fake. Check our official website and verified accounts before sharing."
- ✅ 21. `waitFor` {"ms":600}
- ✅ 22. `expectNotText` {"text":"Public attribution to a state actor"}
- ✅ 23. `fill` {"css":"#dReason"} = "UAT synthetic: holding rebuttal ahead of SIO-verified facts; it states only that no curfew exists."
- ✅ 24. `click` {"testid":"submit-draft"}
- ✅ 25. `select` act as nm-legal
- ✅ 26. `click` {"testid":"legal-approve"}
- ✅ 27. `select` act as nm-sio
- ✅ 28. `click` {"testid":"sio-approve"}
- ✅ 29. `select` act as nm-gold
- ✅ 30. `click` {"testid":"gold-approve"}
- ✅ 31. `select` act as nm-press
- ✅ 32. `click` {"testid":"publish"}
- ✅ 33. `goto` {"path":"/#scenarios"}
- ✅ 34. `click` {"testid":"scenario-SC-02"}
- ✅ 35. `expectHidden` every SC-02 step is ticked

## SC-03 conductor: mobilisation and referral · desktop

### ✅ Tension, referral, response time
- ✅ 1. `goto` {"path":"/#governance"}
- ✅ 2. `click` {"testid":"reset"}
- ✅ 3. `click` {"testid":"clock-30"}
- ✅ 4. `click` {"testid":"clock-30"}
- ✅ 5. `click` {"testid":"clock-30"}
- ✅ 6. `click` {"testid":"clock-30"}
- ✅ 7. `select` act as sib
- ✅ 8. `goto` {"path":"/#radar"}
- ✅ 9. `click` {"testid":"narr-NAR-05"}
- ✅ 10. `click` {"testid":"tension"}
- ✅ 11. `select` act as nc-insight
- ✅ 12. `goto` {"path":"/#escalations"}
- ✅ 13. `click` {"css":"[data-testid^='refer-']"}
- ✅ 14. `expectText` {"text":"awaiting platform"}
- ✅ 15. `click` {"testid":"clock-30"}
- ✅ 16. `click` {"css":"[data-testid^='resolve-']"}
- ✅ 17. `expectText` {"text":"removed after"}
- ✅ 18. `goto` {"path":"/#scenarios"}
- ✅ 19. `click` {"testid":"scenario-SC-03"}
- ✅ 20. `expectHidden` every SC-03 step is ticked

## SC-04 conductor: lawful opinion at a protest · desktop

### ✅ Tier D refusal and impartial explainer
- ✅ 1. `goto` {"path":"/#governance"}
- ✅ 2. `click` {"testid":"reset"}
- ✅ 3. `click` {"testid":"clock-30"}
- ✅ 4. `select` act as nc-insight
- ✅ 5. `goto` {"path":"/#radar"}
- ✅ 6. `click` {"testid":"narr-NAR-07"}
- ✅ 7. `click` {"css":"[data-testid='track-account']"}
- ✅ 8. `expectText` {"text":"Line of Blue analyses narratives, not people"}
- ✅ 9. `select` act as km-comms
- ✅ 10. `goto` {"path":"/#safe-to-say"}
- ✅ 11. `click` {"testid":"example-6"}
- ✅ 12. `waitFor` {"ms":600}
- ✅ 13. `expectText` {"text":"Political impartiality"}
- ✅ 14. `fill` {"css":"#dReason"} = "UAT synthetic: we name the label only to rebut it with facts about the policing plan."
- ✅ 15. `click` {"testid":"submit-draft"}
- ✅ 16. `click` {"testid":"publish"}
- ✅ 17. `goto` {"path":"/#scenarios"}
- ✅ 18. `click` {"testid":"scenario-SC-04"}
- ✅ 19. `expectHidden` every SC-04 step is ticked

## SC-05 conductor: bilingual flood hoax · desktop

### ✅ Welsh and English rebuttal
- ✅ 1. `goto` {"path":"/#governance"}
- ✅ 2. `click` {"testid":"reset"}
- ✅ 3. `click` {"testid":"clock-30"}
- ✅ 4. `select` act as dg-comms
- ✅ 5. `goto` {"path":"/#safe-to-say"}
- ✅ 6. `click` {"testid":"example-7"}
- ✅ 7. `waitFor` {"ms":600}
- ✅ 8. `expectText` {"text":"Welsh version missing"}
- ✅ 9. `click` {"testid":"welsh-template"}
- ✅ 10. `waitFor` {"ms":600}
- ✅ 11. `expectNotText` {"text":"Welsh version missing"}
- ✅ 12. `click` {"testid":"submit-draft"}
- ✅ 13. `click` {"testid":"publish"}
- ✅ 14. `goto` {"path":"/#scenarios"}
- ✅ 15. `click` {"testid":"scenario-SC-05"}
- ✅ 16. `expectHidden` every SC-05 step is ticked

## SC-05 conductor: bilingual flood hoax · mobile

### ✅ Welsh and English rebuttal
- ✅ 1. `goto` {"path":"/#governance"}
- ✅ 2. `click` {"testid":"reset"}
- ✅ 3. `click` {"testid":"clock-30"}
- ✅ 4. `select` act as dg-comms
- ✅ 5. `goto` {"path":"/#safe-to-say"}
- ✅ 6. `click` {"testid":"example-7"}
- ✅ 7. `waitFor` {"ms":600}
- ✅ 8. `expectText` {"text":"Welsh version missing"}
- ✅ 9. `click` {"testid":"welsh-template"}
- ✅ 10. `waitFor` {"ms":600}
- ✅ 11. `expectNotText` {"text":"Welsh version missing"}
- ✅ 12. `click` {"testid":"submit-draft"}
- ✅ 13. `click` {"testid":"publish"}
- ✅ 14. `goto` {"path":"/#scenarios"}
- ✅ 15. `click` {"testid":"scenario-SC-05"}
- ✅ 16. `expectHidden` every SC-05 step is ticked

## SC-06 conductor: hard blocks · desktop

### ✅ Child defendant and complainant anonymity
- ✅ 1. `goto` {"path":"/#governance"}
- ✅ 2. `click` {"testid":"reset"}
- ✅ 3. `select` act as sv-comms
- ✅ 4. `goto` {"path":"/#safe-to-say"}
- ✅ 5. `click` {"testid":"example-4"}
- ✅ 6. `waitFor` {"ms":600}
- ✅ 7. `expectText` {"text":"Identifies a child defendant"}
- ✅ 8. `expectVisible` submit-draft is disabled for this role
- ✅ 9. `select` act as km-comms
- ✅ 10. `click` {"testid":"example-5"}
- ✅ 11. `waitFor` {"ms":600}
- ✅ 12. `expectText` {"text":"Could identify a sexual offence complainant"}
- ✅ 13. `expectVisible` submit-draft is disabled for this role
- ✅ 14. `goto` {"path":"/#scenarios"}
- ✅ 15. `click` {"testid":"scenario-SC-06"}
- ✅ 16. `expectHidden` every SC-06 step is ticked

## SC-07 conductor: get ahead with the forecast and the L.O.B Agent · desktop

### ✅ Pre-bunk the spoof notice before it appears
- ✅ 1. `goto` {"path":"/#governance"}
- ✅ 2. `click` {"testid":"reset"}
- ✅ 3. `select` act as nm-gold
- ✅ 4. `goto` {"path":"/#golden-hour"}
- ✅ 5. `click` {"testid":"open-cell"}
- ✅ 6. `expectText` {"text":"Rumour forecast"}
- ✅ 7. `expectText` {"text":"Spoof official notices"}
- ✅ 8. `select` act as nm-head
- ✅ 9. `goto` {"path":"/#agent"}
- ✅ 10. `click` {"testid":"agent-quick-plan"}
- ✅ 11. `waitFor` {"ms":800}
- ✅ 12. `expectText` {"text":"Get-ahead plan"}
- ✅ 13. `expectText` {"text":"KB-ISD24"}
- ✅ 14. `click` {"css":"button.cite[data-k='KB-ISD24']"}
- ✅ 15. `expectVisible` {"testid":"kb-selected"}
- ✅ 16. `judge` {"name":"agent-plan","prompt":"L.O.B Agent: does the answer give a timed get-ahead plan for each likely rumour, cite public sources by id, offer a pre-bunk that — shots/004-conductor-sc07-desktop-agent-plan.png
- ✅ 17. `select` act as nm-press
- ✅ 18. `goto` {"path":"/#golden-hour"}
- ✅ 19. `click` {"testid":"prebunk-NAR-04"}
- ✅ 20. `waitFor` {"ms":600}
- ✅ 21. `expectText` {"text":"pre-bunk for NAR-04"}
- ✅ 22. `expectText` {"text":"No legal or policy risks found"}
- ✅ 23. `click` {"testid":"submit-draft"}
- ✅ 24. `select` act as nm-legal
- ✅ 25. `goto` {"path":"/#golden-hour"}
- ✅ 26. `click` {"testid":"legal-approve"}
- ✅ 27. `select` act as nm-sio
- ✅ 28. `click` {"testid":"sio-approve"}
- ✅ 29. `select` act as nm-gold
- ✅ 30. `click` {"testid":"gold-approve"}
- ✅ 31. `select` act as nm-press
- ✅ 32. `click` {"testid":"publish"}
- ✅ 33. `expectText` {"text":"line out first"}
- ✅ 34. `click` {"testid":"clock-30"}
- ✅ 35. `click` {"testid":"clock-30"}
- ✅ 36. `click` {"testid":"clock-30"}
- ✅ 37. `select` act as nc-insight
- ✅ 38. `goto` {"path":"/#picture"}
- ✅ 39. `expectVisible` {"testid":"velocity-chart"}
- ✅ 40. `expectVisible` {"testid":"race-NAR-04"}
- ✅ 41. `expectText` {"text":"min ahead"}
- ✅ 42. `judge` {"name":"national-picture","prompt":"National picture at 15:20: do the charts show claim velocity over time, each claim's race between first post, threshold and — shots/007-conductor-sc07-desktop-national-picture.png
- ✅ 43. `select` act as nm-gold
- ✅ 44. `goto` {"path":"/#golden-hour"}
- ✅ 45. `expectVisible` {"testid":"swimlane"}
- ✅ 46. `goto` {"path":"/#scenarios"}
- ✅ 47. `click` {"testid":"scenario-SC-07"}
- ✅ 48. `expectHidden` every SC-07 step is ticked

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

**Page findings**
- ❌ horizontal-overflow on /: 21px wider than viewport ([shot](shots/002-role-agent-user-mobile--agent.png))

## Home Office public safety official (read-only brief) · desktop

### ✅ Sees the brief, cannot act on force work
- ✅ 1. `goto` {"path":"/#governance"}
- ✅ 2. `click` {"testid":"reset"}
- ✅ 3. `select` act as ho-psg
- ✅ 4. `goto` {"path":"/#inbox"}
- ✅ 5. `expectText` {"text":"National situation summary"}
- ✅ 6. `goto` {"path":"/#golden-hour"}
- ✅ 7. `expectVisible` open-cell is disabled for this role
- ✅ 8. `goto` {"path":"/#safe-to-say"}
- ✅ 9. `click` {"testid":"example-0"}
- ✅ 10. `waitFor` {"ms":600}
- ✅ 11. `expectVisible` submit-draft is disabled for this role

## PCC office (governance observer) · desktop

### ✅ Read-only governance view
- ✅ 1. `goto` {"path":"/#governance"}
- ✅ 2. `click` {"testid":"reset"}
- ✅ 3. `select` act as pcc
- ✅ 4. `goto` {"path":"/#inbox"}
- ✅ 5. `expectText` {"text":"National situation summary"}
- ✅ 6. `goto` {"path":"/#lines"}
- ✅ 7. `expectVisible` draft-line is disabled for this role
- ✅ 8. `judge` {"name":"pcc-inbox","prompt":"PCC office: is the view read-only and free of operational detail they should not change?"} — shots/004-role-pcc-desktop-pcc-inbox.png

## PCC office (governance observer) · mobile

### ✅ Read-only governance view
- ✅ 1. `goto` {"path":"/#governance"}
- ✅ 2. `click` {"testid":"reset"}
- ✅ 3. `select` act as pcc
- ✅ 4. `goto` {"path":"/#inbox"}
- ✅ 5. `expectText` {"text":"National situation summary"}
- ✅ 6. `goto` {"path":"/#lines"}
- ✅ 7. `expectVisible` draft-line is disabled for this role
- ✅ 8. `judge` {"name":"pcc-inbox","prompt":"PCC office: is the view read-only and free of operational detail they should not change?"} — shots/004-role-pcc-mobile-pcc-inbox.png

## Force comms officer from another force · desktop

### ✅ Cannot sign off another force's incident
- ✅ 1. `goto` {"path":"/#governance"}
- ✅ 2. `click` {"testid":"reset"}
- ✅ 3. `select` act as sv-comms
- ✅ 4. `goto` {"path":"/#golden-hour"}
- ✅ 5. `expectVisible` open-cell is disabled for this role
- ✅ 6. `goto` {"path":"/#lines"}
- ✅ 7. `expectVisible` draft-line is disabled for this role

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

**Page findings**
- ❌ horizontal-overflow on /: 21px wider than viewport ([shot](shots/004-tour-mobile-mobile--agent.png))

## For review against expectations

Each item is a screen to judge against the profile's expectations. Claude fills in the verdicts in `verdicts.md`.

1. **conductor-sc01 · desktop** /: Narrative Radar at 14:50: is NAR-01 shown as a false claim with velocity, reach, platforms and places, pseudonymised accounts only, and a time to truth once linked? ([shot](shots/005-conductor-sc01-desktop-radar-nar01.png))

2. **conductor-sc01 · desktop** /: National lines: do read receipts show the three receiving forces acknowledged (the host force, Northmoor, owns the incident) and the Welsh force localised? ([shot](shots/008-conductor-sc01-desktop-cascade-receipts.png))

3. **conductor-sc01 · desktop** /: Decision log: does every decision show a named (synthetic) person, a time and the reason, with nothing that profiles a member of the public? ([shot](shots/010-conductor-sc01-desktop-decision-log.png))

4. **conductor-sc01 · desktop** /: Scenario SC-01: are all 14 steps ticked, each naming the actor and organisation? ([shot](shots/012-conductor-sc01-desktop-sc01-complete.png))

5. **conductor-sc07 · desktop** /: L.O.B Agent: does the answer give a timed get-ahead plan for each likely rumour, cite public sources by id, offer a pre-bunk that names no one, and say people decide? ([shot](shots/004-conductor-sc07-desktop-agent-plan.png))

6. **conductor-sc07 · desktop** /: National picture at 15:20: do the charts show claim velocity over time, each claim's race between first post, threshold and police line (with NAR-04 ahead), and the map, readably and without overlaps? ([shot](shots/007-conductor-sc07-desktop-national-picture.png))

7. **role-agent-user · desktop** /: L.O.B Agent: when asked about a risky draft, does it say what must be fixed, why, and cite the relevant law or guidance? ([shot](shots/004-role-agent-user-desktop-agent-check.png))

8. **role-agent-user · mobile** /: L.O.B Agent: when asked about a risky draft, does it say what must be fixed, why, and cite the relevant law or guidance? ([shot](shots/004-role-agent-user-mobile-agent-check.png))

9. **role-pcc · desktop** /: PCC office: is the view read-only and free of operational detail they should not change? ([shot](shots/004-role-pcc-desktop-pcc-inbox.png))

10. **role-pcc · mobile** /: PCC office: is the view read-only and free of operational detail they should not change? ([shot](shots/004-role-pcc-mobile-pcc-inbox.png))

11. **tour-mobile · desktop** /: Does the Data and safeguards screen read cleanly at this width with no clipped text? ([shot](shots/013-tour-mobile-desktop-tour-end.png))

12. **tour-mobile · mobile** /: Does the Data and safeguards screen read cleanly at this width with no clipped text? ([shot](shots/013-tour-mobile-mobile-tour-end.png))
