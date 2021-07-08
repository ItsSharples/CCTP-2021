from __future__ import annotations
# Copy Objects
import copy
# Multiply Arrays
import math

import State
from Operation import Operation
from State import StateType, Operators, Known_Fudges


# x is where the Actor is currently, y are Locations the Actor can go to, c is climb, h is height
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

# Find States of things that don't exist in the Initial State, but can exist
# For example, Grasp affects "have", but "have" is not in the Initial State
def build_state(State: StateType):
    for Operator in Operators:
        for Effect in Operators[Operator]["Effect"]:
            if Effect not in State:
                #print(f"Adding: \"{Effect}\"")
                State[Effect] = []
    return State

def build_goal(State : StateType, Goal : StateType):
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
                if type(thing) == tuple:
                    fudged = False
                    # Find Values to Fudge
                    # for fudge in Goal_Fudge:
                    #     if(fudge[0] == thing[0]):
                    #         # Better way to do this?
                    #         Goal_Fudge[Goal_Fudge.index(fudge)] = thing
                    #         fudged = True

                    #         break
                    
                    if not fudged:  
                        Goal_State[Type].append(thing)

                else:
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

    #print(missing)
    return len(missing)

def check_goal(State : StateType, Goal : StateType) -> bool:
    # If all goal outcomes are in the current state
    #return all([True for outcome in Goal[kind] if outcome in State[kind]] for kind in Goal)

    ## Find any things that are not true
    for operator in Goal:
        for thing in Goal[operator]:
            if(thing not in State[operator]):
                return False
    ## If there are no false things, it must be true
    return True
## TODO, Join Check and Do Together
def Check_Operation(State, Operation : Operation):
    """
    Check if a certain Operation is Valid on the given State

    """
    #print(f"Operation: {Operator}, Args: {Args}")
    Op = Operators[Operation.Operator]
    Arguments = Op["Arguments"]
    Substitutions = {}
    Requires = Op["Requires"]

    # Fulfil Requirements
    if len(Arguments) != len(Operation.Args):
        #print("Uh oh")
        return False

    # Define Substitutions
    # = {What to Substitute : To What} for each thing to substitute
    Substitutions = {Arguments[index] : Operation.Args[index] for index in range(len(Arguments))}

    def check_and_substitute(x):
        if type(req) != tuple:
            return check_and_substitute_value(req)
        else:
            return check_and_substitute_tuple(req)

    def check_and_substitute_value(x):
        # Return the Substitution if there is one, else return the original value
        return Substitutions[x] if x in Substitutions else x
    
    def check_and_substitute_tuple(Tuple, out_Not = False):
        outlist = [Substitutions[x] if x in Substitutions else x for x in Tuple]
        Not = False
        # Remove all modifier values ("Not")
        for val in outlist:
            if val == "Not":
                Not = True
                del outlist[outlist.index(val)]
                
        Tuple = tuple(outlist)
        if len(Tuple) == 1:
            Tuple = (Tuple[0])

        # If I want to out Not, create a List, else just return the tuple
        return Tuple if not out_Not else [Tuple, Not]

    # Find any Fudges
    for Type in Requires:
        for req in Requires[Type]:
            # Substitute any Known Values
            req = check_and_substitute(req)

            # Find any unknown values left over
            unknowns = [val in Known_Fudges for val in req]
            # If they're all unknown, I have no clue what it should be
            if all(unknowns):
                #print("Many Unknowns")
                continue
            # If some are unknown, Find them out
            if any(unknowns):
                #print("Some Unknowns")
                for x in req:
                    x = check_and_substitute_value(x)
                    if x in Known_Fudges:
                        
                        #print(x)
                        #print(State[Type])
                        
                        # Find the Value
                        thing = [val for val in State[Type] if req[0] == val[0]]
                        if len(thing) == 0:
                            # print(f"Cannot find {req}")
                            return False
                        # Update the Substitutions
                        Substitutions[x] = thing[0][1]
                continue
            # There are no unknowns here
            continue


    # Check Requirements
    for require_type in Requires:
        for req in Requires[require_type]:
            req = check_and_substitute(req)
            if req not in State[require_type]:
                #current_value = [val for val in State[require_type] if req[0] == val[0]]
                #print(f"""Cannot Complete Check Requirement\n\tRequirement: {req}\n\tCurrent State: {current_value[:]}""")
                return False

    return True

def DoOperation(OriginalState : dict[str, dict], Operation : Operation, already_checked = False) -> StateType:
    """
    Apply an Operation to a Given State, optionally bypassing validity checks
    """
    #print(f"Operation: {Operator}")
    Operator = Operators[Operation.Operator]
    Arguments = Operator["Arguments"]
    Substitutions = {}
    Requires = Operator["Requires"]
    Effect = Operator["Effect"]

    # Fulfil Requirements
    if len(Arguments) != len(Operation.Args):
        print("Uh oh")
        return OriginalState

    State = copy.deepcopy(OriginalState)
    # Define Substitutions
    # = {What to Substitute : To What} for each thing to substitute
    Substitutions = {Arguments[index] : Operation.Args[index] for index in range(len(Arguments))}

    def check_and_substitute(x):
        if type(req) != tuple:
            return check_and_substitute_value(req)
        else:
            return check_and_substitute_tuple(req)

    def check_and_substitute_value(x):
        # Return the Substitution if there is one, else return the original value
        return Substitutions[x] if x in Substitutions else x
    
    def check_and_substitute_tuple(Tuple, out_Not = False):
        outlist = [Substitutions[x] if x in Substitutions else x for x in Tuple]
        Not = False
        # Remove all modifier values ("Not")
        for val in outlist:
            if val == "Not":
                Not = True
                del outlist[outlist.index(val)]
                
        Tuple = tuple(outlist)
        if len(Tuple) == 1:
            Tuple = (Tuple[0])

        # If I want to out Not, create a List, else just return the tuple
        return Tuple if not out_Not else [Tuple, Not]

    # Find any Fudges
    for List in [Requires, Effect]:
        for Type in List:
            for req in List[Type]:
                # Substitute any Known Values
                req = check_and_substitute(req)

                # Find any unknown values left over
                unknowns = [val in Known_Fudges for val in req]
                # If they're all unknown, I have no clue what it should be
                if all(unknowns):
                    continue
                # If some are unknown, Find them out
                if any(unknowns):
                    for x in req:
                        x = check_and_substitute_value(x)
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
                req = check_and_substitute(req)
                if req not in State[require_type]:
                    print("Cannot Complete Act Requirement")
                    print(f"Requirement: {req}")
                    print(f"Current State: {[val for val in State[require_type] if req[0] == val[0]][0]}")
                    print(Substitutions)
                    return OriginalState

    # Act Out the Operation
    #print(f"Act out {Operator}")
    for action_type in Effect:
        for action in Effect[action_type]:
            thing, Not = check_and_substitute_tuple(action, True)
            #print(action, thing, Not)
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
    if var == []: return ""
    else: return var[0]


(Known_Things, Known_Locations) = find_things(State.StartingState, State.OriginalGoal)

def find_options(State) -> StateType:
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
        #print("Checking", operator)
        args = Operators[operator]["Arguments"]
        #print(args)

        ## I can guess what things I can put into each Arg Spot
        # X is the Actor's Position
        actor_pos = get_at(State, "Actor")
        # Y is not the Actor's Position
        where_actor_is_not = [loc for loc in Known_Locations if (loc != actor_pos and loc != "Inventory")]
        # Things
        things = Known_Things


        Guesses = []
        for index in range(len(args)):
            arg = args[index]
            Guesses.append(None)

            if arg == "x":
                Guesses[index] = actor_pos
                
            if arg == "y":
                Guesses[index] = where_actor_is_not

            if arg not in ["x","y"]:
                Guesses[index] = list(things)
            
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

        #print(f"{operator}\n{get_at(State,'Actor')}") 
        #print(f"Good: {good_args}")
        # Try each good arg
        valid_args = []
        for args in good_args:
            if Check_Operation(State, Operation(operator, args)):
                valid_args.append(args)

        #print(f"Args: {valid_args}")

        #print(f"{operator}:\n{Guesses}\n{complete_guesses}\n{good_args}\n{valid_args}")

        current_options[operator] = valid_args

    return current_options

def simple_score(State):
    opt = find_options(State)
    return len([thing for option in opt for thing in opt[option]])

def debug_text(State):
    #print("-------------------")
    print("Actor is currently at:", get_at(State, "Actor"))
    print(f"Current Options: {find_options(State)}")
    print(f"Num Options {simple_score(State)}")
    #print("Score", distance_between(State, Saved_States["Goal"]))