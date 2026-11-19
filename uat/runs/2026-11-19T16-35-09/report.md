# UAT: Line of Blue synthetic demo (NPCC Communications)

Run 2026-11-19T16:35:09.378Z against http://127.0.0.1:8765 (paid actions skipped).

## Summary

| Persona | Viewport | Scenarios | Page findings | Console / page errors | HTTP errors | Blocked by guardrail |
|---|---|---|---|---|---|---|
| National comms leader: map and workflows | desktop | ✅ lead | 0 fail | 0 | 0 | 0 |
| National comms leader: map and workflows | mobile | ✅ lead | 0 fail | 0 | 0 | 0 |
| Smoke tour of every screen | desktop | ✅ tour | 0 fail | 0 | 0 | 0 |
| Smoke tour of every screen | mobile | ✅ tour | 0 fail | 0 | 0 | 0 |

## National comms leader: map and workflows · desktop

### ✅ Map overlays, autonomy levels, sign-off queue
- ✅ 1. `goto` {"path":"/#governance"}
- ✅ 2. `click` {"testid":"reset"}
- ✅ 3. `select` act as nc-head
- ✅ 4. `goto` {"path":"/#nmap"}
- ✅ 5. `expectVisible` {"testid":"uk-map"}
- ✅ 6. `expectText` {"text":"Real geography, synthetic messages"}
- ✅ 7. `click` {"testid":"layer-cnc"}
- ✅ 8. `expectHidden` {"css":".ukmap .lyr.cnc"}
- ✅ 9. `click` {"testid":"layer-cnc"}
- ✅ 10. `expectVisible` {"css":".ukmap .lyr.cnc"}
- ✅ 11. `click` {"css":"tr[data-f='Cumbria']"}
- ✅ 12. `expectText` {"text":"Who else may need to act nearby"}
- ✅ 13. `expectText` {"text":"Sellafield"}
- ✅ 14. `judge` {"name":"national-map","prompt":"National map: is it a recognisable map of the UK with force HQs, British Transport Police rail hubs, civil nuclear, defence, se — shots/003-role-comms-leader-desktop-national-map.png
- ✅ 15. `goto` {"path":"/#workflows"}
- ✅ 16. `expectVisible` {"testid":"wf-lanes"}
- ✅ 17. `expectText` {"text":"Autonomy mix"}
- ✅ 18. `expectVisible` {"testid":"signoff-queue"}
- ✅ 19. `select` {"css":"select[data-s='W1.3']"} = "1"
- ✅ 20. `goto` {"path":"/#audit"}
- ✅ 21. `expectText` {"text":"Autonomy level changed"}
- ✅ 22. `select` act as pcc
- ✅ 23. `goto` {"path":"/#workflows"}
- ✅ 24. `expectText` {"text":"Only the Head of NPCC Communications"}
- ✅ 25. `judge` {"name":"workflows","prompt":"Workflows and autonomy: are the seven workflows shown as lanes, each step coloured by autonomy level with a live status, an autono — shots/006-role-comms-leader-desktop-workflows.png

## National comms leader: map and workflows · mobile

### ✅ Map overlays, autonomy levels, sign-off queue
- ✅ 1. `goto` {"path":"/#governance"}
- ✅ 2. `click` {"testid":"reset"}
- ✅ 3. `select` act as nc-head
- ✅ 4. `goto` {"path":"/#nmap"}
- ✅ 5. `expectVisible` {"testid":"uk-map"}
- ✅ 6. `expectText` {"text":"Real geography, synthetic messages"}
- ✅ 7. `click` {"testid":"layer-cnc"}
- ✅ 8. `expectHidden` {"css":".ukmap .lyr.cnc"}
- ✅ 9. `click` {"testid":"layer-cnc"}
- ✅ 10. `expectVisible` {"css":".ukmap .lyr.cnc"}
- ✅ 11. `click` {"css":"tr[data-f='Cumbria']"}
- ✅ 12. `expectText` {"text":"Who else may need to act nearby"}
- ✅ 13. `expectText` {"text":"Sellafield"}
- ✅ 14. `judge` {"name":"national-map","prompt":"National map: is it a recognisable map of the UK with force HQs, British Transport Police rail hubs, civil nuclear, defence, se — shots/003-role-comms-leader-mobile-national-map.png
- ✅ 15. `goto` {"path":"/#workflows"}
- ✅ 16. `expectVisible` {"testid":"wf-lanes"}
- ✅ 17. `expectText` {"text":"Autonomy mix"}
- ✅ 18. `expectVisible` {"testid":"signoff-queue"}
- ✅ 19. `select` {"css":"select[data-s='W1.3']"} = "1"
- ✅ 20. `goto` {"path":"/#audit"}
- ✅ 21. `expectText` {"text":"Autonomy level changed"}
- ✅ 22. `select` act as pcc
- ✅ 23. `goto` {"path":"/#workflows"}
- ✅ 24. `expectText` {"text":"Only the Head of NPCC Communications"}
- ✅ 25. `judge` {"name":"workflows","prompt":"Workflows and autonomy: are the seven workflows shown as lanes, each step coloured by autonomy level with a live status, an autono — shots/006-role-comms-leader-mobile-workflows.png

## Smoke tour of every screen · desktop

### ✅ Every workspace renders
- ✅ 1. `goto` {"path":"/#inbox"}
- ✅ 2. `expectText` {"text":"Synthetic demo."}
- ✅ 3. `goto` {"path":"/#picture"}
- ✅ 4. `expectText` {"text":"Synthetic demo."}
- ✅ 5. `goto` {"path":"/#nmap"}
- ✅ 6. `expectText` {"text":"Synthetic demo."}
- ✅ 7. `goto` {"path":"/#radar"}
- ✅ 8. `expectText` {"text":"Synthetic demo."}
- ✅ 9. `goto` {"path":"/#agent"}
- ✅ 10. `expectText` {"text":"Synthetic demo."}
- ✅ 11. `goto` {"path":"/#workflows"}
- ✅ 12. `expectText` {"text":"Synthetic demo."}
- ✅ 13. `goto` {"path":"/#golden-hour"}
- ✅ 14. `expectText` {"text":"Synthetic demo."}
- ✅ 15. `goto` {"path":"/#safe-to-say"}
- ✅ 16. `expectText` {"text":"Synthetic demo."}
- ✅ 17. `goto` {"path":"/#lines"}
- ✅ 18. `expectText` {"text":"Synthetic demo."}
- ✅ 19. `goto` {"path":"/#escalations"}
- ✅ 20. `expectText` {"text":"Synthetic demo."}
- ✅ 21. `goto` {"path":"/#horizon"}
- ✅ 22. `expectText` {"text":"Synthetic demo."}
- ✅ 23. `goto` {"path":"/#scenarios"}
- ✅ 24. `expectText` {"text":"Synthetic demo."}
- ✅ 25. `goto` {"path":"/#audit"}
- ✅ 26. `expectText` {"text":"Synthetic demo."}
- ✅ 27. `goto` {"path":"/#governance"}
- ✅ 28. `expectText` {"text":"Synthetic demo."}
- ✅ 29. `judge` {"name":"tour-end","prompt":"Does the Data and safeguards screen read cleanly at this width with no clipped text?"} — shots/015-tour-mobile-desktop-tour-end.png

## Smoke tour of every screen · mobile

### ✅ Every workspace renders
- ✅ 1. `goto` {"path":"/#inbox"}
- ✅ 2. `expectText` {"text":"Synthetic demo."}
- ✅ 3. `goto` {"path":"/#picture"}
- ✅ 4. `expectText` {"text":"Synthetic demo."}
- ✅ 5. `goto` {"path":"/#nmap"}
- ✅ 6. `expectText` {"text":"Synthetic demo."}
- ✅ 7. `goto` {"path":"/#radar"}
- ✅ 8. `expectText` {"text":"Synthetic demo."}
- ✅ 9. `goto` {"path":"/#agent"}
- ✅ 10. `expectText` {"text":"Synthetic demo."}
- ✅ 11. `goto` {"path":"/#workflows"}
- ✅ 12. `expectText` {"text":"Synthetic demo."}
- ✅ 13. `goto` {"path":"/#golden-hour"}
- ✅ 14. `expectText` {"text":"Synthetic demo."}
- ✅ 15. `goto` {"path":"/#safe-to-say"}
- ✅ 16. `expectText` {"text":"Synthetic demo."}
- ✅ 17. `goto` {"path":"/#lines"}
- ✅ 18. `expectText` {"text":"Synthetic demo."}
- ✅ 19. `goto` {"path":"/#escalations"}
- ✅ 20. `expectText` {"text":"Synthetic demo."}
- ✅ 21. `goto` {"path":"/#horizon"}
- ✅ 22. `expectText` {"text":"Synthetic demo."}
- ✅ 23. `goto` {"path":"/#scenarios"}
- ✅ 24. `expectText` {"text":"Synthetic demo."}
- ✅ 25. `goto` {"path":"/#audit"}
- ✅ 26. `expectText` {"text":"Synthetic demo."}
- ✅ 27. `goto` {"path":"/#governance"}
- ✅ 28. `expectText` {"text":"Synthetic demo."}
- ✅ 29. `judge` {"name":"tour-end","prompt":"Does the Data and safeguards screen read cleanly at this width with no clipped text?"} — shots/015-tour-mobile-mobile-tour-end.png

## For review against expectations

Each item is a screen to judge against the profile's expectations. Claude fills in the verdicts in `verdicts.md`.

1. **role-comms-leader · desktop** /: National map: is it a recognisable map of the UK with force HQs, British Transport Police rail hubs, civil nuclear, defence, service police and port sites as distinct marks, synthetic message bubbles, and a clear note on what is real and what is synthetic? ([shot](shots/003-role-comms-leader-desktop-national-map.png))

2. **role-comms-leader · desktop** /: Workflows and autonomy: are the seven workflows shown as lanes, each step coloured by autonomy level with a live status, an autonomy mix bar, clocks against standards, and a queue of what waits on a person? ([shot](shots/006-role-comms-leader-desktop-workflows.png))

3. **role-comms-leader · mobile** /: National map: is it a recognisable map of the UK with force HQs, British Transport Police rail hubs, civil nuclear, defence, service police and port sites as distinct marks, synthetic message bubbles, and a clear note on what is real and what is synthetic? ([shot](shots/003-role-comms-leader-mobile-national-map.png))

4. **role-comms-leader · mobile** /: Workflows and autonomy: are the seven workflows shown as lanes, each step coloured by autonomy level with a live status, an autonomy mix bar, clocks against standards, and a queue of what waits on a person? ([shot](shots/006-role-comms-leader-mobile-workflows.png))

5. **tour-mobile · desktop** /: Does the Data and safeguards screen read cleanly at this width with no clipped text? ([shot](shots/015-tour-mobile-desktop-tour-end.png))

6. **tour-mobile · mobile** /: Does the Data and safeguards screen read cleanly at this width with no clipped text? ([shot](shots/015-tour-mobile-mobile-tour-end.png))
