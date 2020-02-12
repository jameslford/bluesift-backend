

rmv_list = ['thk', 'thick', 'long', 'wide', 'panel', '+']
inch_list = ['-inch', '(in)', 'in.', 'in']
cm_list = ['(cm)', 'cm.', 'cm']
mm_list = ['(mm)', 'mm.', 'mm']
ft_list = ['(ft)', 'ft.', 'ft']

conversions = {
    1: inch_list,
    .393: cm_list,
    .0393: mm_list,
    12: ft_list,
    39.3: ['(m)']
}


def clean_value(value):
    if not value:
        return None
    conversion = 1
    print('initial ', value)
    value = str(value).strip().lower()
    for k in rmv_list:
        if k in value:
            value = value.replace(k, '')
    for con, vlist in conversions.items():
        for val in vlist:
            if val in value:
                value = value.replace(val, '')
                conversion = con
    if '/' in value:
        value = value.strip()
        initial_split = value.split()
        if len(initial_split) > 1:
            left = float(initial_split[0])
            num, den = initial_split[1].split('/')
            right = round(float(num) / float(den), 3)
            value = left + right
            return round(value * conversion, 3)
        num, den = value.split('/')
        value = round(float(num) / float(den), 3)
        value = round(value * conversion, 3)
        return value
    try:
        value = round(float(value) * conversion, 3)
        return value
    except ValueError:
        return None

    # if 'in.' in value:
    #     print('in')
    #     value = value.replace('in.', '')


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
    for key in conversion_dict:
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
            rval = str(round((float(num) / float(den) * conversion)), 3)
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
        add = round((float(num) / float(den)), 3)
        nval = add + first
        rval = str(nval * conversion)
        return rval.replace(' .', '')
    _value = _value.replace(' .', '')
    try:
        _value = round((float(_value) * conversion), 3)
        return str(_value)
    except ValueError:
        return _value
