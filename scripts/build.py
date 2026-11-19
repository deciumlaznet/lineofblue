#!/usr/bin/env python3
"""Build the demo: inline styles, app and synthetic world into one file.
dist/artifact.html  page body for a claude.ai Artifact (the host adds the document skeleton)
dist/index.html     full standalone document (open locally, serve anywhere, or test with the UAT runner)"""
import json, os
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rd = lambda p: open(os.path.join(R, p), encoding="utf-8").read()
world = json.dumps(json.loads(rd("data/world.json")), ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
body = rd("app/shell.html").replace("/*STYLES*/", rd("app/styles.css")).replace("/*WORLD*/", world).replace("/*APP*/", rd("app/app.js"))
os.makedirs(os.path.join(R, "dist"), exist_ok=True)
open(os.path.join(R, "dist/artifact.html"), "w", encoding="utf-8").write(body)
full = '<!doctype html>\n<html lang="en-GB">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n' + body.replace('<div class="banner"', '</head>\n<body>\n<div class="banner"', 1) + '\n</body>\n</html>\n'
open(os.path.join(R, "dist/index.html"), "w", encoding="utf-8").write(full)
print("built", len(body), "bytes")
