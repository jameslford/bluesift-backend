
emails = [
    'jondoe@hotgmail.com',
    'janedoes@hotgmail.com',
    'burtchrysler@hotgmail.com',
    'seguras@hotgmail.com',
    'custus@hotgmail.com',
    'walden@hotgmail.com'
]

phone_number = '4044335741'

addresses = [
          ['1211 Thornton Rd', 'Lithia Springs', 'GA', '30122'],
          ['1477 Kilchis Falls Way', 'Braselton', 'GA', '30517'],
          ['958 Thomas Powers Rd', 'Newnan', 'GA', '30263'],
          ['577 Martinique Cir', 'Redding', 'CA', '96003'],
          ['9856 W Tompkins Ave', 'Las Vegas', 'NV', '89147'],
          ['236 Union St', 'Spartanburg', 'SC', '29302']
    ]

company_names = [
    'rustic interiors _test',
    'antique finishes _test',
    'southern materials _test',
    'spartan tile _test',
    'elegant flooring _test',
    'crickets woodshop _test'
]




def create_user_data(q):
    email = q[0]
    index = q[1]
    loc_dict = {
        'email': email,
        'password': 'tomatoes',
        'ca_name': comp_accounts[index],
        'locations': []
        }
    for loc in locations[index]:
        location = {
            'nickname': loc[0],
            'number': loc[1],
            'address_line': loc[2],
            'city': loc[3],
            'state': loc[4],
            'zip': loc[5]
        }
        loc_dict['locations'].append(location)
    return loc_dict
