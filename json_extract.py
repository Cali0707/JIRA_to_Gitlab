def json_extract(obj, key):
    """Recursively fetch values from nested JSON."""
    arr = []

    def extract(obj, arr, key):
        """Recursively search for values of key in JSON tree."""
        if isinstance(obj, dict):
            for k, v, in obj.items():
                if isinstance(v, (dict, list)):
                    extract(v, arr, key)
                elif v == 'paragraph':
                    arr.append('<br/>')
                elif k == key:
                    if v is not None:
                        arr.append(v)
        elif isinstance(obj, list):
            for item in obj:
                extract(item, arr, key)
        return arr
    separator = ' '
    values = separator.join(extract(obj, arr, key))
    return values
