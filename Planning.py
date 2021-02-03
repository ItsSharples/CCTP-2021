# Copy Objects
import copy
# Multiply Arrays
import math
"""
["at", "Monkey", "A"]
["height", "Monkey", "Low"]
["pushable", "Box"] #Always True
["climable", "Box"] #Always True
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
          }
    }

Goal = {"have" : [("Monkey", "Bananas")], "at" : [("Monkey", "A")]}

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
##        Reqs = Op["Requires"]
##        Efcts = Op["Effect"]
##
##        for Req in Reqs.values():
##            print(Req)
##        for Efct in Efcts.values():
##            print(Efct)

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
    if Name == "": Name = str(len(Saved_States))
    Saved_States[Name] = copy.deepcopy(State)
    return Saved_States[Name]

def load_state(Name):
    State = Saved_States[Name]
    return State

def check_goal():
    # If all goal outcomes are in the current state
    return all([True for outcome in Goal[kind] if outcome in State[kind]] for kind in Goal)


## TODO, Join Check and Do Together
def Check_Operation(Operator, Arguments = []):
     #print(f"Operation: {Operator}")
    Op = Operators[Operator]
    Args = Op["Arguments"]
    Substitutions = {}
    Reqs = Op["Requires"]

    # Fulfil Requirements
    if len(Args) != len(Arguments):
        #print("Uh oh")
        return False

    # Define Substitutions
    # = {What to Substitute : To What} for each thing to substitute
    Substitutions = {Args[index] : Arguments[index] for index in range(len(Args))}

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
    for Type in Reqs:
        for req in Reqs[Type]:
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
                            #print(f"Cannot find {req}")
                            return False
                        # Update the Substitutions
                        Substitutions[x] = thing[0][1]
                continue
            # There are no unknowns here
            continue


    # Check Requirements
    for require_type in Reqs:
        for req in Reqs[require_type]:
            req = check_and_substitute(req)
            if req not in State[require_type]:
                #print("Cannot Complete Check Requirement")
                #print(f"Requirement: {req}")
                #current_value = [val for val in State[require_type] if req[0] == val[0]]
                #print(f"Current State: {current_value[:]}")
                return False

    return True


def Operation(Operator, Arguments = []):
    #print(f"Operation: {Operator}")
    Op = Operators[Operator]
    Args = Op["Arguments"]
    Substitutions = {}
    Reqs = Op["Requires"]
    Efct = Op["Effect"]

    # Fulfil Requirements
    if len(Args) != len(Arguments):
        print("Uh oh")
        return False

    # Define Substitutions
    # = {What to Substitute : To What} for each thing to substitute
    Substitutions = {Args[index] : Arguments[index] for index in range(len(Args))}

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
    for List in [Reqs, Efct]:
        for Type in List:
            for req in List[Type]:
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
                            # Find the Value
                            thing = [val for val in State[Type] if req[0] == val[0]][0]
                            # Update the Substitutions
                            Substitutions[x] = thing[1]
                    continue
                # There are no unknowns here
                continue

    
    # Check Requirements
    for require_type in Reqs:
        for req in Reqs[require_type]:
            req = check_and_substitute(req)
            if req not in State[require_type]:
                print("Cannot Complete Act Requirement")
                print(f"Requirement: {req}")
                print(f"Current State: {[val for val in State[require_type] if req[0] == val[0]][0]}")
                print(Substitutions)
                return False


    # Act Out the Operation
    #print(f"Act out {Operator}")
    for action_type in Efct:
        for action in Efct[action_type]:
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

def get_at(Thing = "Monkey"):
    return [pair[1] for pair in State["at"] if Thing in pair][0]

build_state()
save_state(State, "Start")
build_goal(State)
#print(distance_between(State, Saved_States["Goal"]))

def find_options():
    current_options = {}
    ## Assemble List of Possible Actions in this current state
    for operator in Operators:
        #print("Checking", operator)
        args = Operators[operator]["Arguments"]
        #print(args)

        ## I can guess what things I can put into each Arg Spot
        # X is the Monkey's Position
        monkey_pos = get_at("Monkey")
        # Y is not the Monkey's Position
        not_monkey_pos = [loc for loc in Known_Locations if loc != monkey_pos]
        # Things
        things = Known_Things

        Guessimoto = []
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

        # Try each good arg
        valid_args = []
        for args in good_args:
            if Check_Operation(operator, args):
                valid_args.append(args)

        current_options[operator] = valid_args


    return current_options

          
save_state(State, "Last")
ls = get_at("Monkey")
print("Monkey is currently at:", get_at("Monkey"))
Possible_New_Locations = [loc for loc in Known_Locations if loc != ls]
for new_loc in Possible_New_Locations:
    
    Operation("Go", ["A", new_loc]);build_goal(State)
    #print(f"Score if Go from \"A\" to \"{new_loc}\": {distance_between(State, Saved_States['Goal'])}")
    save_state(State, f"Go {'A'},{new_loc}")
    State = load_state("Last")

print("End Search")

def debug_text():
    print("----------------")
    print("Monkey is currently at:", get_at("Monkey"))
    print(f"Current Options: {find_options()}")
    print("Score", distance_between(State, Saved_States["Goal"]))

State = load_state("Start")
Operation("Go", ["A", "C"]);build_goal(State)
debug_text()
Operation("Push", ["Box", "C", "B"]);build_goal(State)
debug_text()
Operation("ClimbUp", ["Box"]);build_goal(State)
debug_text()
Operation("Grasp", ["Bananas"]);build_goal(State)
debug_text()
Operation("ClimbDown", ["Box"]);build_goal(State)
debug_text()
Operation("Go", ["B", "A"]);build_goal(State)
debug_text()
Operation("Carry", ["Bananas"]);build_goal(State)
debug_text()
print(check_goal())
#print(State)

