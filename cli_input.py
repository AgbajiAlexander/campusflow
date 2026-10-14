"""Reusable retry-loop prompts. input_fn/output_fn are injectable for tests."""


def prompt_choice(prompt, valid, input_fn=input, output_fn=print, allow_blank=False):
    canonical = {v.casefold(): v for v in valid}
    while True:
        raw = input_fn(prompt).strip()
        if raw == "" and allow_blank:
            return ""
        if raw.casefold() in canonical:
            return canonical[raw.casefold()]
        hint = " (or press Enter to skip)" if allow_blank else ""
        output_fn(f"Invalid choice. Options: {', '.join(valid)}{hint}")


def prompt_text(prompt, input_fn=input, output_fn=print, min_len=1):
    while True:
        raw = input_fn(prompt).strip()
        if len(raw) >= min_len:
            return raw
        output_fn(f"Please enter at least {min_len} character(s).")