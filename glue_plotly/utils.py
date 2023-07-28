from re import match, sub

__all__ = ['cleaned_labels', 'ticks_values']


def cleaned_labels(labels):
    cleaned = [sub(r'\\math(default|regular)', r'\\mathrm', label) for label in labels]
    for j in range(len(cleaned)):
        label = cleaned[j]
        if '$' in label:
            cleaned[j] = '${0}$'.format(label.replace('$', ''))
    return cleaned


def opacity_value_string(a):
    asint = int(a)
    asfloat = float(a)
    n = asint if asint == asfloat else asfloat
    return str(n)


DECIMAL_PATTERN = "\\d+\\.?\\d*"
RGBA_PATTERN = f"rgba\\(({DECIMAL_PATTERN}),\\s*({DECIMAL_PATTERN}),\\s*({DECIMAL_PATTERN}),\\s*({DECIMAL_PATTERN})\\)"


def rgba_string_to_values(rgba_str):
    m = match(RGBA_PATTERN, rgba_str)
    if not m or len(m.groups()) != 4:
        raise ValueError("Invalid RGBA expression")
    r, g, b, a = m.groups()
    return [r, g, b, a]
