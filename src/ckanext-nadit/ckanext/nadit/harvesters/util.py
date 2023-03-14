'''
util.py

Contains helper functions for harvesting.

'''


def get_single_lang(p_dict: dict, p_order: list = ['en', 'de', 'fr', 'it']):
    """
    Obtains a single language

    :param p_dict: a dictionary object
    :param p_order: list of languages in priority sequence
    :return:
    """
    for lang in p_order:
        if lang in p_dict and p_dict[lang]:
            return p_dict[lang]
    return str(p_dict)
