import textwrap


def message(game_state, text):
    """Displays text"""
    messages = game_state['messages']
    width = game_state['message-width']
    height = game_state['message-height']
    for fragment in reversed(textwrap.wrap(text, width)):
        padding = width - len(fragment)
        if padding <= 0:
            padding = ''
        else:
            padding = ' ' * padding
        fragment = fragment + padding
        messages.insert(0, fragment)
    messages = messages[0:height]
