import os, math, sys, logging

from luxplus.game import Game
from luxplus.game_map import Cell, RESOURCE_TYPES
from lux.constants import Constants
from lux.game_constants import GAME_CONSTANTS
from lux import annotate

DIRECTIONS = Constants.DIRECTIONS
game_state = None

def init_logging():
    logs_dirs = './logs/'
    if not os.path.isdir(logs_dirs):
        os.mkdir(logs_dirs)
    logs = os.listdir( logs_dirs )
    
    if len(logs) <= 0:
        os.mkdir( logs_dirs + str(len(logs)) )
        logs.append( str( len(logs) ) )
        
    newest_logs_dir = logs_dirs + logs[-1] + '/'
    
    newest_logs = os.listdir( newest_logs_dir )
    
    if not len(newest_logs) < 2:
        os.mkdir( logs_dirs + str(len(logs)) )
        logs.append( str( len(logs) ) )
        
        newest_logs_dir = logs_dirs + logs[-1] + '/'
    
        newest_logs = os.listdir( newest_logs_dir )
        
    logfile = newest_logs_dir + str( len(newest_logs) ) + '.log'
        
    logging.basicConfig(filename=logfile, level=logging.INFO)

init_logging()



def init_game_state(observation):
    global game_state
    
    ### Do not edit ###
    if observation["step"] == 0:
        game_state = Game()
        game_state._initialize(observation["updates"])
        game_state._update(observation["updates"][2:])
        game_state.id = observation.player
    else:
        game_state._update(observation["updates"])


def get_resource_cells():
    global game_state

    width, height = game_state.map.size

    resource_cells = []
    for y in range(height):
        for x in range(width):
            cell = game_state.map.get_cell(x, y)
            if cell.has_resource():
                resource_cells.append(cell)
    return resource_cells
    
def get_adjacent_cells( cell ):
    global game_state
    
    width, height = game_state.map.size
    
    resource_adjacent_tiles = []
    
    for y in range(height):
        for x in range(width):
            new_cell = game_state.map.get_cell(x, y)
            if cell.pos.is_adjacent(new_cell.pos):
                resource_adjacent_tiles.append(new_cell)
    
    return resource_adjacent_cells

def get_resource_adjacent_cells( resource_cells ):
    global game_state

    width, height = game_state.map.size

    resource_adjacent_cells = []
    for y in range(height):
        for x in range(width):
            cell = game_state.map.get_cell(x, y)
            for resource_cell in resource_cells:
                if cell.pos.is_adjacent( resource_cell.pos ):
                    resource_adjacent_cells.append( cell )
    return resource_adjacent_cells
    
def get_closest_buildable_resource_adjacent_cell(unit, resource_adjacent_cells):
    closest_dist = math.inf
    closest_resource_adjacent_cell = None
    for resource_adjacent_cell in resource_adjacent_cells:
        if not resource_adjacent_cell.resource:
            if resource_adjacent_cell.citytile == None:
                dist = resource_adjacent_cell.pos.distance_to(unit.pos)
                if dist < closest_dist:
                    closest_dist = dist
                    closest_resource_adjacent_cell = resource_adjacent_cell
    return closest_resource_adjacent_cell
    
def get_closest_resource_cell(unit, resource_cells, player):
    closest_dist = math.inf
    closest_resource_cell = None
    for resource_tile in resource_cells:
        if resource_tile.resource.type == Constants.RESOURCE_TYPES.COAL and not player.researched_coal(): continue
        if resource_tile.resource.type == Constants.RESOURCE_TYPES.URANIUM and not player.researched_uranium(): continue
        dist = resource_tile.pos.distance_to(unit.pos)
        if dist < closest_dist:
            closest_dist = dist
            closest_resource_cell = resource_tile
    return closest_resource_cell
    
def get_closest_city(unit, player):
    closest_dist = math.inf
    closest_city_tile = None
    for _, city in player.cities.items():
        for city_tile in city.citytiles:
            dist = city_tile.pos.distance_to(unit.pos)
            if dist < closest_dist:
                closest_dist = dist
                closest_city_tile = city_tile
    return closest_city_tile

def agent(observation, configuration):
    global game_state

    init_game_state(observation)
    
    logging.info(f"Turn: {game_state.turn}")
    
    actions = []

    ### AI Code goes down here! ### 
    player = game_state.players[observation.player]
    opponent = game_state.players[(observation.player + 1) % 2]
    map_width, map_height = game_state.map.width, game_state.map.height

    logging.info(f"{player.cities}")

    resource_cells = get_resource_cells( )

    resource_adjacent_cells = get_resource_adjacent_cells( resource_cells )

    # we iterate over all our units and do something with them
    for unit in player.units:
        if unit.is_worker() and unit.can_act():
            if unit.get_cargo_space_left() > 0:
                closest_resource_tile = get_closest_resource_cell(unit, resource_cells, player)
                
                if closest_resource_tile is not None:
                    actions.append(unit.move(unit.pos.direction_to(closest_resource_tile.pos)))
            else:
                if len(player.cities) > 0:
                    closest_buildable_resource_adjacent_cell = get_closest_buildable_resource_adjacent_cell(unit, resource_adjacent_cells)
                    if closest_buildable_resource_adjacent_cell is not None:
                        move_dir = unit.pos.direction_to(closest_buildable_resource_adjacent_cell.pos)
                        if unit.pos != closest_buildable_resource_adjacent_cell.pos:
                            actions.append(unit.move(move_dir))
                        else:
                            actions.append( unit.build_city() )

    # you can add debug annotations using the functions in the annotate object
    # actions.append(annotate.circle(0, 0))
    
    return actions
