
def clean_value(value):
    if not value:
        return None
    value = str(value).strip().lower()
    rmv_list = ['thk', 'thick', 'long', 'wide']
    for k in rmv_list:
        if k in value:
            value = value.replace(k, '')
    return value.strip()


def unified_measurement(value):
    # returns a uniform lenght/width/tickness in inches
    conversion_dict = {
        '-inch': 1,
        '(in)': 1,
        '"': 1,
        'in.': 1,
        'in': 1,
        '(mm)': .0393,
        'mm': .0393,
        '(ft)': 12,
        'ft': 12,
        "'": 12,
        '(cm)': .393,
        'cm': .393,
        '(m)': 39.3,
    }
    conversion = 1
    _value = value
    for key in conversion_dict.keys():
        if key in _value:
            conversion = conversion_dict.get(key, 1)
            _value = _value.replace(key, '')
    letter_count = 0
    for char in _value:
        if char.isalpha():
            letter_count += 1
    # if letter_count > 0:
    #     return value.lower()
    # _value = _value.strip()
    if ',' in _value:
        sizes = []
        val_lest = _value.split(',')
        for val in val_lest:
            sizes.append(unified_measurement(val))
        return ', '.join(sizes)
    space_split = _value.split(' ')
    if len(space_split) < 2:
        if '/' in _value:
            num, den = _value.split('/')
            rval = str((float(num) / float(den) * conversion))
            return rval.replace(' .', '')
        else:
            try:
                _value = float(_value.strip()) * conversion
                return str(_value)
            except ValueError:
                return 'N/A'
                # return str(_value)
    first = float(space_split[0])
    second = space_split[1]
    if '/' in second:
        num, den = second.split('/')
        add = float(num) / float(den)
        nval = add + first
        rval = str(nval * conversion)
        return rval.replace(' .', '')
    _value = _value.replace(' .', '')
    try:
        _value = float(_value) * conversion
        return str(_value)
    except ValueError:
        return _value
