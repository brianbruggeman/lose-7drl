# -*- coding: utf-8 -*-


def main_setup():
    # Below is code to prove the above actually does something desired.
    from random import choice
    from lose.utils.algorithms.pathing import dijkstra
    from lose.game import initialize_game

    game_state = initialize_game()
    level_map = game_state['current-level']
    tiles = game_state['tiles']

    tiled_map = {}
    non_blocking_tile_map = {}
    for position, node in level_map.items():
        tile_name = node['name']
        tile = tiles.get(tile_name)
        if not tile:
            continue
        tiled_map[position] = tile
        if tile['name'] not in ['wall', 'hidden-door', 'loose-rubble', 'water']:
            non_blocking_tile_map[position] = tile
        pass

    map_to_render = non_blocking_tile_map
    map_width = game_state['map-width']
    map_height = game_state['map-height']
    character_position = choice(list(non_blocking_tile_map.keys()))

    def get_printable_characters():
        chars = ['0']
        chars.extend(chr(_) for _ in range(ord('1'), ord('9')))
        chars.extend(chr(_) for _ in range(ord('A'), ord('Z')))
        chars.extend(chr(_) for _ in range(ord('a'), ord('z')))
        chars.extend(chr(_) for _ in range(579, 677))
        chars.extend(chr(_) for _ in range(913, 999))
        for c in chars:
            if c.isprintable():
                if c.strip():
                    yield c

    def render(level_map, map_width, map_height, center):
        distances = dijkstra(level_map, character_position, include_diagonals=True)
        printable_characters = list(get_printable_characters())
        distances = {k: v for v, k in distances}
        for y in range(map_height):
            for x in range(map_width):
                position = (y, x)
                cost = distances.get(position, None)
                character = ' '
                if cost is not None:
                    character = printable_characters[int(round(cost)) % len(printable_characters)]
                else:
                    tile = level_map.get(position)
                    if tile:
                        character = tile.get('display', {}).get('icon', {}).get('character')
                if position == center:
                    character = '@'
                print(character, end='')
            print()

    def render_map(level):
        for y in range(map_height):
            for x in range(map_width):
                position = (y, x)
                tile = level.get(position)
                character = tile.get('display', {}).get('icon', {}).get('character') or ' '
                print(character, end='')
            print()

    # render(map_to_render, map_width, map_height, character_position)
    return map_to_render, character_position


if __name__ == '__main__':
    import timeit
    from textwrap import dedent as dd

    setup_statement = dd("""
        from pathing import main_setup, dijkstra
        map_to_render, character_position = main_setup()
    """)
    statement_to_test = "[_ for _ in dijkstra(map_to_render, character_position)]"
    print(timeit.timeit(statement_to_test, setup_statement, number=200))
