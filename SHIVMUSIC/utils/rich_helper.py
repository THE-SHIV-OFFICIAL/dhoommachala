"""Reusable Telegram Rich Message layouts used by main and clone bots."""

from html import escape
import re

from ftmgram.types import InputRichMessage


EMOJI = {
    "sparkle": "<tg-emoji emoji-id='6172312314423808834'>✨</tg-emoji>",
    "book": "<tg-emoji emoji-id='5260512129240276089'>📚</tg-emoji>",
    "chart": "<tg-emoji emoji-id='5936143551854285132'>📊</tg-emoji>",
    "command": "<tg-emoji emoji-id='6172663483834831848'>⌨️</tg-emoji>",
    "info": "<tg-emoji emoji-id='5188540541922480562'>❓</tg-emoji>",
    "music": "<tg-emoji emoji-id='6082387600599944892'>🎧</tg-emoji>",
}


def _cell(value: object, *, header: bool = False) -> str:
    tag = "th" if header else "td"
    return f"<{tag}>{escape(str(value))}</{tag}>"


def rich_table(title: str, headers: list[str], rows: list[tuple[object, ...]], note: str | None = None) -> InputRichMessage:
    head = "".join(_cell(item, header=True) for item in headers)
    body = "".join(
        f"<tr>{''.join(_cell(item) for item in row)}</tr>" for row in rows
    )
    note_html = f"<blockquote expandable>{note}</blockquote>" if note else ""
    html = (
        f"<b>{EMOJI['sparkle']} {escape(title)} {EMOJI['sparkle']}</b>\n"
        f"<table><tr>{head}</tr>{body}</table>\n{note_html}"
    )
    return InputRichMessage(html=html)


def build_rich_stats(title: str, stats_dict: dict[str, object]) -> InputRichMessage:
    return rich_table(
        title,
        ["Metric", "Value"],
        [(key, value) for key, value in stats_dict.items()],
        f"{EMOJI['music']} Live system information",
    )


def build_rich_help(title: str, rows: list[tuple[str, str]], note: str | None = None) -> InputRichMessage:
    return rich_table(title, ["Command", "Description"], rows, note)


def legacy_help_to_rich(text: str) -> InputRichMessage:
    """Turn an existing help block into the same bordered two-column layout."""
    clean = re.sub(r"<[^>]+>", "", text).strip()
    lines = [line.strip(" •") for line in clean.splitlines() if line.strip()]
    title = lines.pop(0).strip(" :") if lines else "Commands"
    rows: list[tuple[str, str]] = []
    notes: list[str] = []
    for line in lines:
        if " – " in line:
            command, description = line.split(" – ", 1)
            rows.append((command.strip(), description.strip()))
        elif line.startswith("/") and " " in line:
            command, description = line.split(" ", 1)
            rows.append((command.strip(), description.strip(" :-")))
        else:
            notes.append(line)
    if not rows:
        rows = [("Info", line) for line in notes] or [("Info", "No commands available")]
        notes = []
    return build_rich_help(title, rows, "\n".join(notes) or None)

