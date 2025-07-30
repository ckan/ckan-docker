def dataset_type_class(value):
    """Returns a CSS-safe class name for dataset types, or '' if unknown or missing."""
    if not value:
        return ""

    mapping = {
        'Derived': 'derived',
        'Raw dataset': 'raw',
        'Interpolated': 'interpolated',
        'Aggregated': 'aggregated',
        'Map': 'map',
        # Add more as needed
    }

    css_class = mapping.get(value)
    return f"add-info-value-{css_class}" if css_class else ""