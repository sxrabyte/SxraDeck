from dataclasses import dataclass, field

@dataclass
class Command:
    label: str
    cmd: str | None = None
    prompt: list[str] = field(default_factory=list)