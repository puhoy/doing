import logging


def colorize(colors, text):
    """
    colorize terminal output

    :param color: [header, okblue, okgreen, ...]
    :param text: text to colorize
    :return: colorized text, ready to print
    """
    bcolors = {
        "HEADER": '\033[95m',
        "OKBLUE": '\033[94m',
        "OKGREEN": '\033[92m',
        "WARNING": '\033[93m',
        "FAIL": '\033[91m',
        "ENDC": '\033[0m',
        "BOLD": '\033[1m',
        "UNDERLINE": '\033[4m'
    }

    if isinstance(colors, str):
        colors = [colors]
    for color in colors:
        if color.upper() in bcolors.keys():
            text = '%s%s%s' % (bcolors[color.upper()], text, bcolors["ENDC"])
        else:
            logging.debug('%s not found in colors' % color)
    return text
