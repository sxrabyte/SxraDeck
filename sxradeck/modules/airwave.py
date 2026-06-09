import subprocess
from dataclasses import dataclass

from pygments import highlight


@dataclass
class Finding:
    label: str
    output: str
    highlight: bool

#To run system commands using python
def run_command(cmd: str) -> str:
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True
        )
        return result.stdout.strip() or result.stderr.strip()
    except Exception as e:
        return f"Error: {e}"


def aircrack_ng() -> list[Finding]:
    findings = []

    findings.append(Finding(
        label=""
    ))

    return findings