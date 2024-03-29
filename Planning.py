from __future__ import annotations
# Copy Objects
import copy
# Multiply Arrays
import math

import itertools
import random

import State
from Operation import Action, Event
from State import EventType, IsSpecialLocation, Special_Locations, StateType, Operators, Known_Fudges



def find_things(State : StateType, Goal : StateType):
    Known_Things = set();
    Known_Locations = set();
    for Dict in [State, Goal]:
        for List in Dict:
            for thing in Dict[List]:
                if(type(thing) == tuple):
                    Known_Things.add(thing[0])
                    if List == "at":
                        Known_Locations.add(thing[1])
                else:
                    Known_Things.add(thing)
    return (Known_Things, Known_Locations);

def build_state(State: StateType):
    """
    Find States of things that don't exist in the Initial State, but can exist
    For example, Grasp affects "have", but "have" is not in the Initial State
    """
    for Operator in Operators:
        for Effect in Operators[Operator]["Effect"]:
            if Effect not in State:
                #print(f"Adding: \"{Effect}\"")
                State[Effect] = []
    return State

def build_goal(State : StateType, Goal : StateType) -> StateType:
    """
    Convert the Current State into one that complies with the goal
    """
    Goal_State = copy.deepcopy(State)
    # Search Score
    score = 0
    # Similar to Fudging Operations, but this time Fudging the State itself
    for Type in Goal:
        for thing in Goal[Type]: # (Object, Value) or Object (Implied True)
            Goal_Fudge = Goal_State[Type] if Type in Goal else []
            if thing in Goal_Fudge:
                continue # I don't need to do anything more
            else:
                score += 1
                Goal_State[Type].append(thing)

    return Goal_State

def distance_between(State_A, State_B ) -> int:
    score = 0
    missing = []
    ## TODO Make the Score more aware of When a value is altered instead of missing
    for Type in State_A:
        for thing in State_A[Type]:
            if thing not in State_B[Type]:
                missing.append(thing)
                score += 1

        for thing in State_B[Type]:
            if thing not in State_A[Type] and thing not in missing:
                missing.append(thing)
                score += 1

    return len(missing)

def check_goal(State : StateType, Goal : StateType) -> bool:
    """If all goal outcomes are in the current state.
    return all([True for outcome in Goal[kind] if outcome in State[kind]] for kind in Goal)
    """

    ## Find any things that are not true
    for operator in Goal:
        for thing in Goal[operator]:
            if(thing not in State[operator]):
                return False
    ## If there are no false things, it must be true
    return True
## TODO, Join Check and Do Together
def Check_Operation(State, Operation : Action):
    """
    Check if a certain Operation is Valid on the given State

    """
    # Define Substitutions
    Substitutions = Operation.Substitutions
    Requires = Operation.Requires

    # Find any Fudges
    for Type in Requires:
        for req in Requires[Type]:
            # Substitute any Known Values
            req = Operation.check_and_substitute(req)
            # Find any unknown values left over
            unknowns = [val in Known_Fudges for val in req]
            # If they're all unknown, I have no clue what it should be
            if all(unknowns):
                continue
            # If some are unknown, Find them out
            if any(unknowns):
                for x in req:
                    x = Operation.check_and_substitute_value(x)
                    if x in Known_Fudges:
                        # Find the Value
                        thing = [val for val in State[Type] if req[0] == val[0]]
                        # If we can't find it
                        if len(thing) == 0:
                            return False
                        # Update the Substitutions
                        Substitutions[x] = thing[0][1]
                continue
            # There are no unknowns here
            continue


    # Check Requirements
    for require_type in Requires:
        for req in Requires[require_type]:
            req = Operation.check_and_substitute(req)
            if req not in State[require_type]:
                return False

    return True

def DoOperation(OriginalState : dict[str, dict], Operation : Action, already_checked = False) -> StateType:
    """
    Apply an Operation to a Given State, optionally bypassing validity checks
    """
    State = copy.deepcopy(OriginalState)
    # Define Substitutions
    Substitutions = Operation.Substitutions
    Requires = Operation.Requires
    Effect = Operation.Effect

    # Find any Fudges
    for List in [Requires, Effect]:
        if List is None: continue
        for Type in List:
            for req in List[Type]:
                # Substitute any Known Values
                req = Operation.check_and_substitute(req)
                # Find any unknown values left over
                unknowns = [val in Known_Fudges for val in req]
                # If they're all unknown, I have no clue what it should be
                if all(unknowns):
                    continue
                # If some are unknown, Guess that they're fudges
                if any(unknowns):
                    for x in req:
                        x = Operation.check_and_substitute_value(x)
                        if x in Known_Fudges:
                            # Find the Value
                            thing = [val for val in State[Type] if req[0] == val[0]][0]
                            # Update the Substitutions
                            Substitutions[x] = thing[1]
                    continue
                # There are no unknowns here
                continue

    if not already_checked:
    # Check Requirements
        for require_type in Requires:
            for req in Requires[require_type]:
                req = Operation.check_and_substitute(req)
                if req not in State[require_type]:
                    try:
                        print(f"Cannot Complete Act Requirement")
                        print(f"Requirement: {req}")
                        print(f"Current State: {[val for val in State[require_type] if req[0] == val[0]][0]}")
                        print(Substitutions)
                    except:
                        pass
                    return OriginalState

    # Act Out the Operation
    for action_type in Effect:
        for action in Effect[action_type]:
            thing, Not = Operation.check_and_substitute_tuple(action, True)
            compare = State[action_type]
            # If In But is Not
            if thing in compare:
                if Not:
                    compare.remove(thing)

            if thing not in compare:
                if not Not:
                    compare.append(thing)

    return State

def get_at(State, Thing = "Actor"):
    """
    Returns
        All the Things that are in the same location as Thing
    """
    var = [pair[1] for pair in State["at"] if Thing in pair]
    if var == []: return None
    else: return var[0]

def get_at_notAt(State, Thing = "Actor"):
    thing_pos = get_at(State, Thing);
    return (thing_pos, [loc for loc in Known_Locations if (loc != thing_pos and loc not in Special_Locations)])

def find_options(State: StateType) -> StateType:
    """
    Find Options

    State : dict
        The current State
    Returns : dict 
        Keys: operators that you can do
        Values: List - Values that you can pass to the operator
    """
    current_options = {}

    ## Assemble List of Possible Actions in this current state
    for operator in Operators:
        args = Operators[operator]["Arguments"]
        actor_pos, where_actor_is_not = get_at_notAt(State, "Actor")

        Guesses = []
        for index in range(len(args)):
            arg = args[index]
            Guesses.append(None)

            if arg == "x":
                Guesses[index] = actor_pos
                
            if arg == "y":
                Guesses[index] = where_actor_is_not

            if arg not in ["x","y"]:
                Guesses[index] = list(Known_Things)
            
            continue

        complete_guesses = [None] * len(Guesses)

        # Get the Number of Guesses for each Index
        count = [len(Guess) if type(Guess) == list else 1 for Guess in Guesses]
        # Adjust each Guess Index to be equal in length
        for index in range(len(count)):
            # Remove it from the Number of Guesses
            tmp = copy.deepcopy(count)
            del tmp[index]
            # Compute and Apply the amount to multiply to make all Indices the same length
            value = list(Guesses[index]) if type(Guesses[index]) == list else [Guesses[index]]
            complete_guesses[index] = value * math.prod(tmp)

        good_args = []
        # For the total length of arguments
        for index in range(math.prod(count)):
            # Transfer Guesses from n x m arrays, to m x n arrays
            out = []
            # For each index
            for jndex in range(len(complete_guesses)):
                out.append(complete_guesses[jndex][index])
            good_args.append(out)

        # Try each good arg
        valid_args = []
        for args in good_args:
            if Check_Operation(State, Action(operator, args)):
                valid_args.append(args)

        current_options[operator] = valid_args

    return current_options

def find_events(State: StateType, Event : EventType) -> StateType:
    """
    Find Events

    State : dict
        The current State
    Returns : dict 
        Keys: operators that you can do
        Values: List - Values that you can pass to the operator
    """
    current_options = {}


    ThingArgsList = list()
    ## Assemble List of Possible Actions in this current state
    for thing in Known_Things:

        # Actor Events will be explicit
        if thing == "Actor":
            continue

        args = Event["Arguments"]
        thing_pos, where_thing_is_not = get_at_notAt(State, thing)

        if thing_pos == None:
            continue

        if IsSpecialLocation(thing_pos):
            continue

        Guesses = []
        for index in range(len(args)):
            arg = args[index]

            if arg == "x":
                Guesses.append(thing_pos)
                
            if arg == "y":
                Guesses.append(where_thing_is_not)

            if arg not in ["x","y"]:
                Guesses.append(thing)#list(Known_Things))
            
            continue #End For

        complete_guesses = [None] * len(Guesses)

        # Get the Number of Guesses for each Index
        count = [len(Guess) if type(Guess) == list else 1 for Guess in Guesses]
        # Adjust each Guess Index to be equal in length
        for index in range(len(count)):
            # Remove it from the Number of Guesses
            tmp = copy.deepcopy(count)
            del tmp[index]
            # Compute and Apply the amount to multiply to make all Indices the same length
            value = list(Guesses[index]) if type(Guesses[index]) == list else [Guesses[index]]
            complete_guesses[index] = value * math.prod(tmp)

        good_args = list()
        # For the total length of arguments
        for index in range(math.prod(count)):
            # Transfer Guesses from n x m arrays, to m x n arrays
            out = []
            # For each index
            for jndex in range(len(complete_guesses)):
                out.append(complete_guesses[jndex][index])
            good_args.append(out)

        ThingArgsList.append(good_args)


        # #print(f"Args: {valid_args}")

        # #print(f"{operator}:\n{Guesses}\n{complete_guesses}\n{good_args}\n{valid_args}")

        # current_options[operator] = valid_args

    # Take one from each Thing List and make a new list of these lists
    combinations = itertools.product(*ThingArgsList)
    # Make a choice
    choice = random.choice(list(combinations))
    # Make sure there's only Unique actions
    # Do it now, as it's the least expensive time to
    unique_actions = list()
    for action in choice:
        if action not in unique_actions:
            unique_actions.append(action)
    # 
    return random.choice(unique_actions)

def simple_score(State):
    opt = find_options(State)
    return len([thing for option in opt for thing in opt[option]])

def debug_text(State):
    #print("-------------------")
    print("Actor is currently at:", get_at(State, "Actor"))
    print(f"Current Options: {find_options(State)}")
    print(f"Num Options {simple_score(State)}")
    #print("Score", distance_between(State, Saved_States["Goal"]))

(Known_Things, Known_Locations) = find_things(State.StartingState, State.OriginalGoal)
