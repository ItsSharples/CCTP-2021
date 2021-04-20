# Copy Objects
import copy
# Multiply Arrays
import math
"""
["at", "Monkey", "A"]
["height", "Monkey", "Low"]
["pushable", "Box"] #Always True
["climbable", "Box"] #Always True
["graspable", "Bananas"] #Always True
"""

## This System Differs from other Planners, because it combines Qualities together, eg. There is a single object for all "at" values.

State = {
    "at" : [("Monkey", "A"),("Bananas", "B"), ("Box", "C")],
    "height" : [("Monkey", "Low"),("Bananas", "High"), ("Box", "Low")],
    "pushable" : ["Box"], # List of True
    "climbable" : ["Box"], # List of True
    "graspable" : ["Bananas"] # List of True
    }

## TODO Think about Held Objects following the Holder

Operators = {
    "Go" : {"Arguments" : ["x", "y"],
            "Requires": {"at" : [("Monkey", "x")], "height" : [("Monkey", "Low")]},
            "Effect" : {"at" : [("Monkey", "y"), ("Monkey", "x", "Not")]}
            },

    "Push" : {"Arguments" : ["push", "x", "y"],
              "Requires":{"at" : [("Monkey","x"), ("push","x")], "height" : [("Monkey","Low"), ("push", "Low")], "pushable" : ["push"]},
              "Effect" : {"at" : [("push","y"), ("Monkey","y"), ("push","x", "Not"), ("Monkey","x", "Not")]}
              },

    "ClimbUp" : {"Arguments" : ["climb"],
          "Requires":{"at" : [("Monkey","x"), ("climb","x")], "height" : [("Monkey","Low"), ("climb", "Low")], "climbable" : ["climb"]},
          "Effect" : {"height" : [("Monkey", "High"), ("Monkey", "Low", "Not")], "on" : [("Monkey", "climb")]}
          },

    "ClimbDown" : {"Arguments" : ["climb"],
          "Requires":{"at" : [("Monkey","x"), ("climb","x")], "height" : [("Monkey","High"), ("climb", "Low")], "climbable" : ["climb"]},
          "Effect" : {"height" : [("Monkey", "High", "Not"), ("Monkey", "Low")], "on" : [("Monkey", "climb", "Not")]}
          },

    "Grasp" : {"Arguments" : ["grab"],
          "Requires":{"at" : [("Monkey","x"), ("grab","x")], "height" : [("Monkey","h"), ("grab", "h")], "graspable" : ["grab"]},
          "Effect" : {"have" : [("Monkey", "grab")]}
          },

    "Carry" : {"Arguments" : ["carry"],
          "Requires":{"at" : [("Monkey", "x"), ("carry", "y")], "have" : [("Monkey", "carry")]},
          "Effect" : {"at" : [("carry", "x"), ("carry", "y", "Not")]}
          },

    "Pull Down" : {"Arguments" : ["carry"],
      "Requires":{"height" : [("Monkey", "High"), ("carry", "High")], "have" : [("Monkey", "carry")]},
      "Effect" : {"height" : [("carry", "Low"), ("carry", "Low", "Not")]}
      }
    }

Goal = {"have" : [("Monkey", "Bananas")], "at" : [("Monkey", "A")], "height" : [("Monkey", "Low")]}

# Things that aren't arguments, but can be used to make Operations more generic
Known_Fudges = ["x", "y", "c", "h"]

Known_Things = set()
Known_Locations = set()
def find_things():
    for Dict in [State, Goal]:
        for List in Dict:
            for thing in Dict[List]:
                if(type(thing) == tuple):
                    Known_Things.add(thing[0])
                    if List == "at":
                        Known_Locations.add(thing[1])
                else:
                    Known_Things.add(thing)
    ## For Now, Don't care about Operations, The State and Goal is all we care about
##    for Op in Operators.values():
##        #print(Op)
##        Args = Op["Arguments"]
##        Substitutions = {}
##        Requires = Op["Requires"]
##        Effects = Op["Effect"]
##
##        for Req in Requires.values():
##            print(Req)
##        for Effect in Effects.values():
##            print(Effect)

find_things()

Saved_States = {}

# Find State Kinds that don't exist in the Initial State, but will exist
# For example, Grasp effects "have", but "have" is not in the Initial State
def build_state():
    for Operator in Operators:
        for Effect in Operators[Operator]["Effect"]:
            if Effect not in State:
                #print(f"Adding: \"{Effect}\"")
                State[Effect] = []

# Convert the Current State into one that complies with the goal
def build_goal(State = State):
    Goal_State = save_state(State, "Goal")
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
                    for fudge in Goal_Fudge:
                        if(fudge[0] == thing[0]):
                            # Better way to do this?
                            Goal_Fudge[Goal_Fudge.index(fudge)] = thing
                            fudged = True

                            break
                    
                    if not fudged:  
                        Goal_State[Type].append(thing)

                else:
                    Goal_State[Type].append(thing)

    return distance_between(State, Goal_State)
    
def distance_between(State_A, State_B):
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

def save_state(State, Name = ""):
    #print(f"Saving State with name: \"{Name}\"")
    if Name == "": Name = str(len(Saved_States))
    #if Name in Saved_States.keys(): print(f"Overriding \"{Name}\"")
    Saved_States[Name] = copy.deepcopy(State)

    #print(f"State \"{Name}\" now looks like: {State}")
    return Saved_States[Name]

def load_state(Name):
    #print(f"Loading State with name: \"{Name}\"")
    State = copy.deepcopy(Saved_States[Name])

    #print(f"State \"{Name}\" looks like: {State}")
    return State

def check_goal(State):
    # If all goal outcomes are in the current state
    return all([True for outcome in Goal[kind] if outcome in State[kind]] for kind in Goal)


## TODO, Join Check and Do Together
def Check_Operation(State, Operator, Args = []):

    #print(f"Operation: {Operator}, Args: {Args}")
    Op = Operators[Operator]
    Arguments = Op["Arguments"]
    Substitutions = {}
    Requires = Op["Requires"]

    # Fulfil Requirements
    if len(Arguments) != len(Args):
        #print("Uh oh")
        return False

    # Define Substitutions
    # = {What to Substitute : To What} for each thing to substitute
    Substitutions = {Arguments[index] : Args[index] for index in range(len(Arguments))}

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


def Operation(State, Operator, Args = [], already_checked = False):
    #print(f"Operation: {Operator}")
    Operation = Operators[Operator]
    Arguments = Operation["Arguments"]
    Substitutions = {}
    Requires = Operation["Requires"]
    Effect = Operation["Effect"]

    # Fulfil Requirements
    if len(Arguments) != len(Args):
        print("Uh oh")
        return False

    # Define Substitutions
    # = {What to Substitute : To What} for each thing to substitute
    Substitutions = {Arguments[index] : Args[index] for index in range(len(Arguments))}

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
                    return False


    # Act Out the Operation
    #print(f"Act out {Operator}")
    for action_type in Effect:
        for action in Effect[action_type]:
            thing, Not = check_and_substitute_tuple(action, True)

            compare = State[action_type]
            # If In But is Not
            if thing in compare:
                if Not:
                    compare.remove(thing)

            if thing not in compare:
                if not Not:
                    compare.append(thing)

    # Return Success
    return True

def get_at(State, Thing = "Monkey"):
    var = [pair[1] for pair in State["at"] if Thing in pair]
    if var == []: return ""
    else: return var[0]
    

build_state()
save_state(State, "Start")
build_goal(State)
#print(distance_between(State, Saved_States["Goal"]))


## TODO Reduce the Cost of Polling this Multiple Times
global state_hash, current_options
state_hash = 0
current_options = {}

def find_options(State):
    global state_hash, current_options
    ## NOTE str(dict) may not be stable, however, this will just mean that this function happens
    ## Stability is only required if the performance requirement dictates it.

    # Probably the same
    if state_hash == hash(str(State)):
        return current_options

    # Else, find the new stuff
    current_options = {}
    state_hash = hash(str(State))

    ## Assemble List of Possible Actions in this current state
    for operator in Operators:
        #print("Checking", operator)
        args = Operators[operator]["Arguments"]
        #print(args)

        ## I can guess what things I can put into each Arg Spot
        # X is the Monkey's Position
        monkey_pos = get_at(State, "Monkey")
        # Y is not the Monkey's Position
        not_monkey_pos = [loc for loc in Known_Locations if loc != monkey_pos]
        # Things
        things = Known_Things

        Guesses = []
        for index in range(len(args)):
            arg = args[index]
            Guesses.append(None)

            if arg == "x":
                Guesses[index] = monkey_pos
                
            if arg == "y":
                Guesses[index] = not_monkey_pos

            if arg not in ["x","y"]:
                Guesses[index] = list(things)
            
            continue

        complete_guesses = [None] * len(Guesses)

        # Get the Number of Guesses for each Index
        count = [len(Guess) for Guess in Guesses]
        # Adjust each Guess Index to be equal in length
        for index in range(len(count)):
            # Remove it from the Number of Guesses
            tmp = copy.deepcopy(count)
            del tmp[index]
            # Compute and Apply the amount to multiply to make all Indices the same length
            complete_guesses[index] = list(Guesses[index]) * math.prod(tmp)

        good_args = []
        # For the total length of arguments
        for index in range(math.prod(count)):
            # Transfer Guesses from n x m arrays, to m x n arrays
            out = []
            # For each index
            for jndex in range(len(complete_guesses)):
                out.append(complete_guesses[jndex][index])
            good_args.append(out)

        #print(f"{operator}\n{get_at(State,'Monkey')}") 
        #print(f"Good: {good_args}")
        # Try each good arg
        valid_args = []
        for args in good_args:
            if Check_Operation(State, operator, args):
                valid_args.append(args)

        #print(f"Args: {valid_args}")

        current_options[operator] = valid_args

    return current_options

def simple_score(State):
    opt = find_options(State)
    return len([thing for option in opt for thing in opt[option]])

def debug_text():
    #print("-------------------")
    print("Monkey is currently at:", get_at(State, "Monkey"))
    print(f"Current Options: {find_options(State)}")
    print(f"Num Options {simple_score(State)}")
    print("Score", distance_between(State, Saved_States["Goal"]))

          
save_state(State, "Last")
#ls = get_at("Monkey")
print("Monkey is currently at:", get_at(State, "Monkey"))

options = find_options(State)
print("--- Start State ---")
debug_text()
print("------Options------")
global best_plan, plans, done
plans = 0
done = False
best_plan = ""

def plan(State, Name, limit = 8, best_len = 99999, tried_go = False):
    global best_plan, plans, done, last_3_operators, last_operator_iter
    last_3_operators = ["", "", ""]
    last_operator_iter = 0

        # last_3_operators[last_operator_iter % 3] = value
        # last_operator_iter += 1



    plans += 1
    if limit < 0:
        #print("At Limit")
        best_plan = Name
        best_len = len(Name)
        return best_len
    if done:
        return best_len

    if limit < 4:
        # Start Caring about The Scores
        simple = simple_score(State)
        distance = distance_between(State, Saved_States["Goal"])
        #score = simple + distance
        if simple > 3:
            if distance > 3:
                return best_len

    save_state(State, Name)
    State = load_state(Name)
    build_goal(State)

    new_hash = hash(str(State))
    options = find_options(State)

    for operator in options:
        if operator == "Go" and tried_go:
            continue
        for args in options[operator]:
            State = load_state(Name)
            # Perform the Operation
            Operation(State, operator, args, True)
            Plan_Name = f"{Name} {operator} {args}"

            # TODO Work out if we've been in this State before
            escape = False
            for state_name in Saved_States:
                # Ignore the Markers
                if state_name in ["Start", "Goal", "Last"]:
                    continue

                other_state = Saved_States[state_name]
                if (State.items() == other_state.items()):
                    #print("I remember this place...", state_name, ",", Plan_Name)
                    if Plan_Name == state_name: # We're already checking from here
                        bad = "Yes"
                    elif len(Plan_Name) < len(state_name):
                        # This plan gets to this state quicker
                        del Saved_States[state_name]
                        save_state(State, Plan_Name)
                        # But We're already checking from here
                    else:
                        # This is worse than older states
                        Plan_Name = state_name
                    escape = True
                    break

            print(Plan_Name, escape)
            if escape:
                continue

            # Save this new state
            save_state(State, Plan_Name)

            # If fulfils the goal
            if check_goal(State):
                new_len = len(Plan_Name)
                #if new_len < best_len:
                print(f"FOUND GOAL AT For {Name} {operator} {args}")
                best_len = new_len
                best_plan = Plan_Name

                done = True
                return best_len
            # Else continue planning
            best_len = plan(State, Plan_Name, limit - 1, best_len, operator == "Go")

    #print("Eh")
    return best_len

print(State)
print("-----PLANNING------")
current_state = State
best_plan = "Start"
while not done:
    length = plan(current_state, best_plan, 5, 9999)
    current_state = Saved_States[best_plan]

    #build_goal(State)
    #print("Distance:", distance_between(Goal, Saved_States["Goal"]))
    #print("Length:", length)

    print("Plan:", best_plan)
print("----End Options----")
print("End Search")

print(plans)

##Possible_New_Locations = [loc for loc in Known_Locations if loc != ls]
##for new_loc in Possible_New_Locations:
##    
##    Operation("Go", ["A", new_loc]);build_goal(State)
##    #print(f"Score if Go from \"A\" to \"{new_loc}\": {distance_between(State, Saved_States['Goal'])}")
##    save_state(State, f"Go {'A'},{new_loc}")
##    State = load_state("Last")