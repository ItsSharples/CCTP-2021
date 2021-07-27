from typing import List, Tuple
import copy
from Planner import Plan

from Planning import find_events
from State import IsSpecialLocation, StateType
import State
import random
import Operation

def PlanEvents(CurrentPlan : Plan) -> Tuple[str, List[Operation.Event]]:

    # at = CurrentState["at"]
    # new_at: StateContents = list()
    # for pair in at:
    #     if pair[0] != "Scarecrow":
    #         new_at.append(pair)
    # new_at.append(("Scarecrow", "Far Away"))
    # CurrentState["at"] = new_at

    CurrentState = CurrentPlan.CurrentState

    DisasterName = "Move"
    SelectedDisaster = State.Events[DisasterName]
    # Find Valid Arguments
    DisasterActions = [find_events(CurrentState, SelectedDisaster)]
    return (DisasterName, DisasterActions)



def PickRandomThingAt(inputState: StateType) -> Tuple[Tuple[str,str], int]:
    locations: list[tuple[str,str]] = inputState["at"];
    index = random.randint(0, len(locations) - 1)
    chosen_tuple = locations[index]
    return (chosen_tuple, index)


def MoveItem(inputState: StateType, index: int, new_tuple: Tuple[str, str]) -> StateType:
    # Update the Arrays 
    inputState["at"][index] = new_tuple
    return inputState

def MoveRandomThing(inputState: StateType, whereTo: str) -> StateType:
    '''
    Randomly selects a Random Thing, and changes it's location to {whereTo}
    '''
    chosen_tuple, index = PickRandomThingAt(inputState)
    while IsSpecialLocation(chosen_tuple[1]):
        chosen_tuple, index = PickRandomThingAt(inputState)
    
    return MoveItem(inputState, index, (chosen_tuple[0], whereTo))

def MoveRandomThingSafe(inputState: StateType, whereTo: str) -> StateType:
    '''
    Randomly selects a Random Thing that's not at {whereTo}, and changes it's location to {whereTo}
    '''
    chosen_tuple, index = PickRandomThingAt(inputState)
    # while Invalid or Already there
    while IsSpecialLocation(chosen_tuple[1]) or (chosen_tuple[1] == whereTo):
        chosen_tuple, index = PickRandomThingAt(inputState)

    return MoveItem(inputState, index, (chosen_tuple[0], whereTo))

