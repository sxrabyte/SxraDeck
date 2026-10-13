from dataclasses import dataclass, field


@dataclass
class Command:
    """A runnable shell command.

    label   : human-readable name shown in the UI.
    cmd     : shell string. May contain ``{NAME}`` placeholders that are
              filled from touch-entered parameters before running.
    prompt  : parameter names to collect before running (order preserved).
              Each name must match a ``{NAME}`` placeholder in ``cmd``.
    confirm : if True, show a confirmation screen before executing
              (use for destructive / disruptive actions).
    """

    label: str
    cmd: str | None = None
    prompt: list[str] = field(default_factory=list)
    confirm: bool = False
