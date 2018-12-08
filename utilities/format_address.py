from rva_dash.utilities.street_types import street_direction_abbreviations, street_type_abbreviations

def format_address_street_type(address):
    '''
    If the last word in the string is in street_types.py then it will be normalized. (e.g. "13 north main avenue" becomes "13 north main ave")
    '''
    split_address = address.lower().split()
    try:
        split_address[-1] = street_type_abbreviations[split_address[-1].replace('.', '')]
    except (KeyError, IndexError):
        return address
    formatted_address = ' '.join(split_address)
    return formatted_address


def format_address_direction(address):
    '''
    If the second word in the string is a direction in street_types.py then it will be normalized. (e.g. "13 north main avenue" becomes "13 n main ave")
    '''
    split_address = address.lower().split()
    try:
        split_address[1] = street_direction_abbreviations[split_address[1].replace('.', '')]
    except (KeyError, IndexError):
        pass
    formatted_address = ' '.join(split_address)
    return formatted_address