import json
from pathlib import Path

def run():
    print("[EXPORT] Creating Immunefi-ready bug report...")
    data_path = Path("data/bounty_payload.json")
    if not data_path.exists():
        print("[!] Missing data file at data/bounty_payload.json")
        return

    data = json.loads(data_path.read_text())

    md = f"""# 🐞 Immunefi Bug Report

**Project:** {data['project']}
**Severity:** {data['severity']}
**Block Number:** {data['block']}
**Type:** {data['vulnerability']}

## 🧠 Description

{data['description']}

## 🧪 Steps to Reproduce
"""

    for step in data['steps']:
        md += f"- {step}\\n"

    md += f"""

## 💥 Impact
Estimated impact: **{data['impact']}**

## ✅ Recommendation
{data['recommendation']}

## 📎 Proof of Exploit
Script: `{data['proof']['script']}`  
Screenshot: `{data['proof']['screenshot']}`
"""

    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    report_path = output_dir / "bug_report.md"
    report_path.write_text(md)

    print(f"[+] Markdown report saved to {report_path}")