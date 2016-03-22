import locale

icons_as_dict = {
    'check': ("\N{CHECK MARK}", '[check]'),
    'inf': ("\N{INFINITY}", '[inf]'),
    'right_triangle': ("\N{BLACK RIGHT-POINTING TRIANGLE}", '>'),
    'right_arrowhead': ("\N{BLACK RIGHTWARDS ARROWHEAD}", '->'),
    'multiplication_x': ("\N{HEAVY MULTIPLICATION X}", 'x'),
    'ballot_x': ("\N{BALLOT X}", 'X'),
    'star': ("\N{BLACK STAR}", '*'),
    #'' "\N{}"
}

support = False
if 'utf-8' in locale.getdefaultlocale()[1].lower():
    print('got support')
    support = True


class Icons():
    """
    instanciate with a dict, then get the utf-8 by the key

    icon = Icons(icons_as_dict)
    print(icon.inf + icon.*)

    """
    def __init__(self, dp_dict=None):
        self.utf_dict = dp_dict

    def __getattribute__(self, name):
        if support:
            return icons_as_dict[name][0]
        else:
            return icons_as_dict[name][1]

icon = Icons(icons_as_dict)
