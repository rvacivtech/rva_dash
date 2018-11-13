from backend.utilities.street_types import street_direction_abbreviations, street_type_abbreviations

def format_address_street_type(address):
    split_address = address.lower().split()
    try:
        split_address[-1] = street_type_abbreviations[split_address[-1]]
    except KeyError:
        pass
    formatted_address = ' '.join(split_address)
    return formatted_address


def format_address_direction(address):
    split_address = address.lower().split()
    try:
        split_address[1] = street_direction_abbreviations[split_address[1]]
    except KeyError:
        pass
    formatted_address = ' '.join(split_address)
    return formatted_address