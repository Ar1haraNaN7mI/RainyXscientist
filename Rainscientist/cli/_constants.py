"""Shared constants and utilities for CLI and TUI modules."""

from datetime import UTC, datetime

from ..sessions import AGENT_NAME

WELCOME_SLOGANS = [
    "Ready for vibe research? What do you want cooking?",
    "Science doesn't sleep. Neither do your agents.",
    "From hypothesis to paper — let's cook.",
    "Your research kitchen is ready. What's on the menu?",
    "Experiments don't run themselves. Oh wait — they do now.",
    "Drop a question. We'll bring the citations.",
    "Vibe first. Discovery follows.",
    "What breakthrough are we cooking today?",
    "Harness the vibe. Start the research.",
    "Ideas in. Discoveries out.",
    "Automating the grind so you can focus on the 'Eureka'.",
    "Your lab, scaled. One prompt, a thousand simulations.",
    "Parallelize your curiosity. The agents are standing by.",
    "Let the agents handle the noise. You curate the signal.",
    "Raw data is just ingredients. Let's turn it into a feast.",
    "The frontier is just a prompt away.",
]

# ASCII art logo — FIGlet "big" font (RXSCIENTIST); taller glyphs than the old flat-wide style.
# Shared by both Rich CLI and Textual TUI banners.
LOGO_LINES = (
    " _____  __   __ _____  _____ _____ ______ _   _ _______ _____  _____ _______ ",
    "|  __ \\ \\ \\ / // ____|/ ____|_   _|  ____| \\ | |__   __|_   _|/ ____|__   __|",
    "| |__) | \\ V /| (___ | |      | | | |__  |  \\| |  | |    | | | (___    | |   ",
    "|  _  /   > <  \\___ \\| |      | | |  __| | . ` |  | |    | |  \\___ \\   | |   ",
    "| | \\ \\  / . \\ ____) | |____ _| |_| |____| |\\  |  | |   _| |_ ____) |  | |   ",
    "|_|  \\_\\/_/ \\_\\_____/ \\_____|_____|______|_| \\_|  |_|  |_____|_____/   |_|   ",
)

# Distinct rainbow hues (one band per logo row, cycled if more lines are added later).
LOGO_RAINBOW = [
    "#ff1744",  # red
    "#ff6d00",  # orange
    "#ffd600",  # yellow
    "#00e676",  # green
    "#00b0ff",  # light blue
    "#651fff",  # violet
]

# Back-compat alias (blue gradient); prefer LOGO_RAINBOW + itertools.cycle in banners.
LOGO_GRADIENT = LOGO_RAINBOW


def build_metadata(workspace_dir: str | None, model: str | None) -> dict:
    """Build metadata dict for LangGraph checkpoint persistence."""
    return {
        "agent_name": AGENT_NAME,
        "updated_at": datetime.now(UTC).isoformat(),
        "workspace_dir": workspace_dir or "",
        "model": model or "",
    }
