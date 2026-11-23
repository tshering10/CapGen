from pathlib import Path

from subtitle_editor.models import Alignment, SubtitleDocument


def seconds_to_ass(timestamp: float) -> str:
    if timestamp < 0:
        timestamp = 0
    hours, remainder = divmod(timestamp, 3600)
    minutes, seconds = divmod(remainder, 60)
    whole_seconds = int(seconds)
    centiseconds = round((seconds - whole_seconds) * 100)
    if centiseconds == 100:
        whole_seconds += 1
        centiseconds = 0
    return f"{int(hours):01d}:{int(minutes):02d}:{whole_seconds:02d}.{centiseconds:02d}"


def seconds_to_srt(timestamp: float) -> str:
    if timestamp < 0:
        timestamp = 0
    hours, remainder = divmod(timestamp, 3600)
    minutes, seconds = divmod(remainder, 60)
    whole_seconds = int(seconds)
    milliseconds = round((seconds - whole_seconds) * 1000)
    if milliseconds == 1000:
        whole_seconds += 1
        milliseconds = 0
    return f"{int(hours):02d}:{int(minutes):02d}:{whole_seconds:02d},{milliseconds:03d}"


def ass_color(hex_color: str, opacity: float = 1.0) -> str:
    value = hex_color.lstrip("#")
    if len(value) != 6:
        raise ValueError("Colors must use a 6-digit hex format")
    red = int(value[0:2], 16)
    green = int(value[2:4], 16)
    blue = int(value[4:6], 16)
    alpha = round((1 - opacity) * 255)
    return f"&H{alpha:02X}{blue:02X}{green:02X}{red:02X}"


def alignment_number(alignment: Alignment) -> int:
    return {
        Alignment.LEFT: 1,
        Alignment.CENTER: 2,
        Alignment.RIGHT: 3,
    }[alignment]


def generate_ass(document: SubtitleDocument) -> str:
    style = document.style
    play_res_x = 1080
    play_res_y = 1920
    position_x = round(style.position_x * play_res_x)
    position_y = round(style.position_y * play_res_y)

    lines = [
        "[Script Info]",
        "ScriptType: v4.00+",
        "PlayResX: 1080",
        "PlayResY: 1920",
        "ScaledBorderAndShadow: yes",
        "",
        "[V4+ Styles]",
        "Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,"
        "OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,"
        "ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,"
        "Alignment,MarginL,MarginR,MarginV,Encoding",
        (
            f"Style: Default,{style.font_family},{style.font_size},"
            f"{ass_color(style.font_color)},"
            f"{ass_color(style.font_color)},"
            f"{ass_color(style.background_color)},"
            f"{ass_color(style.background_color, style.background_opacity)},"
            "0,0,0,0,100,100,0,0,3,2,1,"
            f"{alignment_number(style.alignment)},40,40,20,1"
        ),
        "",
        "[Events]",
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, "
        "Effect, Text",
    ]

    for segment in document.segments:
        text = segment.text.replace("\\", "\\\\").replace("{", "\\{").replace("}", "\\}")
        override = f"{{\\an{alignment_number(style.alignment)}\\pos({position_x},{position_y})}}"
        lines.append(
            f"Dialogue: 0,{seconds_to_ass(segment.start)},"
            f"{seconds_to_ass(segment.end)},Default,,0,0,0,,{override}{text}"
        )

    return "\n".join(lines) + "\n"


def generate_srt(document: SubtitleDocument) -> str:
    entries = []
    for index, segment in enumerate(document.segments, start=1):
        entries.append(
            f"{index}\n"
            f"{seconds_to_srt(segment.start)} --> {seconds_to_srt(segment.end)}\n"
            f"{segment.text}\n"
        )
    return "\n".join(entries)


def write_ass(document: SubtitleDocument, destination: Path) -> Path:
    destination.write_text(generate_ass(document), encoding="utf-8")
    return destination


def write_srt(document: SubtitleDocument, destination: Path) -> Path:
    destination.write_text(generate_srt(document), encoding="utf-8-sig")
    return destination
