ALENA_SKINS = {
    0: "@character/alena_start",
    1: "@character/alena", # alena_bob
    2: "@character/alena_long_hair",
    3: "@character/alena_veil",
}

LOCATION_ALENA_SKIN_SEQUENCE = {
    1: (0, 1),
    2: (1,),
    3: (0, 2),
    4: (2,),
    5: (2,),
    6: (2,),
    7: (0,),
    8: (0,),
    9: (0,),
    10: (0,),
    11: (0,),
    12: (0,),
    13: (0, 3, 0),
    14: (0,),
    15: (0,),
    16: (0,),
    17: (0,),
    18: (0,),
    19: (0,),
    20: (0,),
    21: (0,),
    22: (0,),
    23: (0,),
}


def get_expected_alena_skin_sequence(location_id):
    skin_ids = LOCATION_ALENA_SKIN_SEQUENCE.get(location_id)

    if skin_ids is None:
        return None

    return tuple(ALENA_SKINS[skin_id] for skin_id in skin_ids)


def get_allowed_alena_skins(location_id):
    skin_sequence = get_expected_alena_skin_sequence(location_id)

    if skin_sequence is None:
        return None

    return set(skin_sequence)
