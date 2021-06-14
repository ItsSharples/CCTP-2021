# Copy Objects
import copy
# Multiply Arrays
import math
from typing import Any, NoReturn
"""
["at", "Actor", "A"]
["height", "Actor", "Low"]
["pushable", "Box"] #Always True
["climbable", "Box"] #Always True
["graspable", "Lightbulb"] #Always True
"""

## This System Differs from other Planners, because it combines Qualities together, eg. There is a single object for all "at" values.
## , ("Working", "High") "Working",
StartingState = {
    "at" : [("Actor", "A"),("Broken", "B"), ("Box", "C"), ("Working", "D")],
    "height" : [("Actor", "Low"),("Broken", "High"), ("Box", "Low"), ("Working", "Low")],
    "pushable" : ["Box"], # List of True
    "climbable" : ["Box"], # List of True
    "graspable" : [ "Broken", "Working"] # List of True
    }

## TODO Think about Held Objects following the Holder

Operators = {
# Move Actor from x to y
    "Go" : {"Arguments" : ["x", "y"],
            "Requires": {"at" : [("Actor", "x")], "height" : [("Actor", "Low")]},
            "Effect" : {"at" : [("Actor", "y"), ("Actor", "x", "Not")]}
            },
# Push "push" from x to y
    "Push" : {"Arguments" : ["push", "x", "y"],
              "Requires":{"at" : [("Actor","x"), ("push","x")], "height" : [("Actor","Low"), ("push", "Low")], "pushable" : ["push"]},
              "Effect" : {"at" : [("push","y"), ("Actor","y"), ("push","x", "Not"), ("Actor","x", "Not")]}
              },
# Climb Up "climb"
    "ClimbUp" : {"Arguments" : ["climb"],
          "Requires":{
              "at" : [("Actor","x"), ("climb","x")],
              "height" : [("Actor", "Low"), ("climb", "Low")],
              "climbable" : ["climb"]
              },
          "Effect" : {
              "height" : [("Actor", "High"), ("Actor", "Low", "Not")],
              "on" : [("Actor", "climb")]
              }
          },
# Climb Down "climb"
    "ClimbDown" : {"Arguments" : ["climb"],
          "Requires":{
              "at" : [("Actor","x"), ("climb","x")],
              "height" : [("Actor","High"), ("climb", "Low")],
              "climbable" : ["climb"]
              },
          "Effect" : {
              "height" : [("Actor", "Low"), ("Actor", "High", "Not")],
              "on" : [("Actor", "climb", "Not")]
              }
          },
# Pick up "grab"
    "Grasp" : {"Arguments" : ["grab"],
          "Requires":{
              "at" : [("Actor","x"), ("grab","x")],
              "height" : [("Actor","h"), ("grab", "h")],
              "graspable" : ["grab"]
              },
          "Effect" : {
              "have" : [("Actor", "grab")],
              "at":[("grab", "Inventory"), ("grab", "x", "Not")],
              "height":[("grab", "NA"), ("grab", "h", "Not")]
              }
          }
# Put down "drop"
    # "Drop" : {"Arguments" : ["drop"],
    #       "Requires":{"have" : [("Actor", "drop")]},
    #       "Effect" : {
    #           "have" : [("Actor", "drop", "Not")],
    #           "at" : [("drop","x"), ("drop", "Inventory", "Not")],
    #           "height" : [("drop", "h"), ("drop", "NA", "Not")]
    #           }
    #       },
#TODO These might of been made redundant
# Carry "carry", this is a workaround to get things to follow the Actor's location
#     "Carry" : {"Arguments" : ["carry"],
#           "Requires":{"at" : [("Actor", "x"), ("carry", "y")], "have" : [("Actor", "carry")]},
#           "Effect" : {"at" : [("carry", "x"), ("carry", "y", "Not")]}
#           },
# # Pull down "carry", this is a workaround to get things to follow the Actor's height
#     "Pull Down" : {"Arguments" : ["carry"],
#       "Requires":{"height" : [("Actor", "High"), ("carry", "High")], "have" : [("Actor", "carry")]},
#       "Effect" : {"height" : [("carry", "Low"), ("carry", "Low", "Not")]}
#       }
}
# Have the Actor replace the Broken Lightbulb with a new Lightbulb
OriginalGoal = {
    "have" : [("Actor", "Broken")],
    "at" : [("Actor", "A") ],
    "height" : [("Actor", "Low")]
}

#  , ("Working", "B") , ("Working", "High")
# Things that aren't arguments, but can be used to make Operations more generic
Known_Fudges = ["x", "y", "c", "h"]
# x is where the Actor is currently, y are Locations the Actor can go to, c is climb, h is height
def find_things(State : dict[str, Any], Goal):
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

class Operation:
    def __init__(this, Operator : str, Args : list = []):
        this.Operator = Operator;
        this.Args = Args;

    def __str__(self) -> str:
        return f"{self.Operator} {self.Args}"

class Plan:
    def __init__(self, First_Operation, parent):
        
        if First_Operation.Operator == "Start":
            self.Parent = None
            self.Operations = [First_Operation]
            self.CurrentState = StartingState
            self.ChildOf = 0;
            self.BasicScore = 9999999999;
            return;

        self.Parent : Plan = parent
        self.ChildOf = self.Parent.ChildOf + 1
        self.Operations = parent.Operations + [First_Operation];
        self.CurrentState = DoOperation(self.Parent.CurrentState, First_Operation);
        self.BasicScore = self.Operations.__len__();

        self.Goal = build_goal(self.CurrentState);
        self.Completed = check_goal(self.CurrentState, self.Goal);

        # if(this.Completed):
        #     print(f"Optimizing: {str(this.Parent)}")
        #     this.Optimize()

        #print(this.Completed);

    def Add(this, operation: Operation):
        this.Operations.append(operation)
        return this

    def Optimize(this):
        # Go through the Children to find identical states
        parent_states = {}
        
        Parent = this.Parent
        while(Parent != None):
            strState = str(Parent.CurrentState)
            if strState in parent_states:
                parent_states[strState].append(Parent)
            else:
               parent_states[strState] = [Parent]

            Parent = Parent.Parent

        for state in parent_states.values():
                if len(state) > 1:
                    best_parent = this;
                    best_age = this.ChildOf;
                    for Plan in state:
                        if best_age > Plan.ChildOf:
                            best_age = Plan.ChildOf
                            best_parent = Plan

                    this = best_parent
                    print("Optimised")
                    return;

    def __str__(self) -> str:
        return " ".join([str(op) for op in self.Operations])

    def __len__(self) -> int:
        return self.BasicScore

StartPlan = Plan(Operation("Start"), None)

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

(Known_Things, Known_Locations) = find_things(StartingState, OriginalGoal)


Saved_States = {}

# Find States of things that don't exist in the Initial State, but can exist
# For example, Grasp affects "have", but "have" is not in the Initial State
def build_state(State):
    for Operator in Operators:
        for Effect in Operators[Operator]["Effect"]:
            if Effect not in State:
                #print(f"Adding: \"{Effect}\"")
                State[Effect] = []
    return State

def build_goal(State = StartingState, Goal = OriginalGoal):
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

def save_state(State, Name : str = ""):
    #print(f"Saving State with name: \"{Name}\"")
    if Name == "": Name = str(len(Saved_States))
    #if Name in Saved_States.keys(): print(f"Overriding \"{Name}\"")
    Saved_States[Name] = copy.deepcopy(State)

    #print(f"State \"{Name}\" now looks like: {State}")
    return Saved_States[Name]

def load_state(Name : str):
    #print(f"Loading State with name: \"{Name}\"")
    State = copy.deepcopy(Saved_States[Name])

    #print(f"State \"{Name}\" looks like: {State}")
    return State

def check_goal(State : StartingState, Goal : StartingState) -> bool:
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

def DoOperation(OriginalState : StartingState, Operation : Operation, already_checked = False) -> StartingState:
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
    

StartingState = build_state(StartingState)
#save_state(StartingState, StartPlan)
BuiltGoal = build_goal(StartingState)
#print(distance_between(State, Saved_States["Goal"]))

# print(f"This works?: {check_goal(BuiltGoal, BuiltGoal)}")
# GoodPlan = Plan(Operation("Go", ["A", "C"]), StartPlan)
# GoodPlan = Plan(Operation("Push", ["Box", "C", "B"]), GoodPlan)
# GoodPlan = Plan(Operation("ClimbUp", ["Box"]), GoodPlan)
# GoodPlan = Plan(Operation("Grasp", ["Broken"]), GoodPlan)
# GoodPlan = Plan(Operation("ClimbDown", ["Box"]), GoodPlan)
# GoodPlan = Plan(Operation("Go", ["B", "A"]), GoodPlan)
# Goal = build_goal(GoodPlan.Current)
# print(f"This works?: {check_goal(GoodPlan.Current, Goal)}")
# print(GoodPlan.Current)
# print(Goal)

## TODO Reduce the Cost of Polling this Multiple Times
global state_hash, current_options
state_hash = 0
current_options = {}


def find_options(State) -> current_options:
    """
    Find Options

    State : dict
        The current State
    Returns : dict 
        Keys: operators that you can do
        Values: List - Values that you can pass to the operator
    """
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

        #print(f"{operator}\n{get_at(State,'Actor')}") 
        #print(f"Good: {good_args}")
        # Try each good arg
        valid_args = []
        for args in good_args:
            if Check_Operation(State, Operation(operator, args)):
                valid_args.append(args)

        #print(f"Args: {valid_args}")

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

          
#save_state(State, "Last")
#ls = get_at("Actor")
print("Actor is currently at:", get_at(StartingState, "Actor"))

options = find_options(StartingState)
print("--- Start State ---")
debug_text(StartingState)
print("------Options------")
#global best_plan, plans, done
# plans = 0
# done = False
# best_plan = ""




def oldPlan(CurrPlan : Plan, limit = 20, BestPlan : Plan = None, last_operator = "") -> Plan:
    #global best_plan, plans
    #plans += 1
    if limit <= 0:
        #print("At Limit")
        return BestPlan

    State = CurrPlan.CurrentState
    GoalState = build_goal(State, BuiltGoal)
    options = find_options(State)

    if limit < 4:
        # Start Caring about The Scores
        simple = simple_score(State)
        distance = distance_between(State, GoalState)
        score = simple + distance
        if simple > 3:
            #print("Scores:", distance, simple)
            #print("State:", Name)
            if distance > 5:
                return BestPlan

    # #print(f"Planning {Name}")
    # save_state(State, str(CurrPlan))
    # State = load_state(str(CurrPlan))

    #print("Monkey is currently at:", get_at(State, "Monkey"))
    #print(options)
    #print(State)

    for operator in options:
        if operator == last_operator:
            continue
        for args in options[operator]:
            #print(f"Operation: {operator} {args}")
            op = Operation(operator, args)
            # State = load_state(str(CurrPlan))
            # DoOperation(State, op)
            NewPlan = Plan(op, CurrPlan)
            #print(str(NewPlan))
            # save_state(State, str(CurrPlan))

            if NewPlan.Completed:
                #print(best_len, new_len)
                # itemThing = ""
                # for item in Goal:
                #     itemThing += item + ": ["
                #     for thing in Goal[item]:
                #         itemThing += str(thing) + ", "
                        
                #         print(thing)
                #         print(thing in State[item])
                #     itemThing = itemThing[:-2] + "]\n"

                # print(itemThing)
                if len(NewPlan) < len(BestPlan):
                    print(f"FOUND GOAL AT For {NewPlan}")
                    BestPlan = NewPlan
                    BestPlan.Optimize()
                return BestPlan

            BestPlan = oldPlan(NewPlan, limit - 1, BestPlan, operator)
            #print(f"""For {Name} {operator} {args}\n\tSimple Score: {simple_score(State)}\n\tScore: distance_between(State, {Saved_States["Goal"]}""")


                
            
            
            #print("Build Goal")
            #build_goal(State)
            #print("Goal Built")
            #debug_text()
    return BestPlan


#print(StartingState)
print("-----PLANNING------")
BestPlan = oldPlan(StartPlan, 15, StartPlan)
print("Len", BestPlan.Operations.__len__())
print(BestPlan.CurrentState)
print(BestPlan)
#print(Saved_States)
#print(Saved_States[best_plan])
print("----End Options----")
print("End Search")

quit()





# def plan(State, Name, steps_left = 8, best_len = 99999, tried_go = False):
#     global best_plan, plans, done, last_3_operators, last_operator_iter
#     last_3_operators = ["", "", ""]
#     last_operator_iter = 0

#         # last_3_operators[last_operator_iter % 3] = value
#         # last_operator_iter += 1



#     plans += 1
#     if steps_left < 0:
#         #print("At Limit")
#         best_plan = Name
#         best_len = len(Name)
#         return best_len
#     if done:
#         return best_len

#     if steps_left < 4:
#         # Start Caring about The Scores
#         simple = simple_score(State)
#         distance = distance_between(State, Saved_States["Goal"])
#         #score = simple + distance
#         if simple > 3:
#             if distance > 3:
#                 return best_len

#     save_state(State, Name)
#     State = load_state(Name)
#     build_goal(State)

#     #new_hash = hash(str(State))
#     options = find_options(State)

#     for operator in options:
#         # Don't try Go twice in a row, you can just Go from a to c, instead of a to b to c
#         if operator == "Go" and tried_go: 
#             continue
#         for args in options[operator]:
#             State = load_state(Name)
#             # Perform the Operation
#             Operation(State, operator, args, True)
#             Plan_Name = f"{Name} {operator} {args}"

#             # TODO Work out if we've been in this State before
#             """
#             escape = False
#             for state_name in Saved_States:
#                 # Ignore the Markers
#                 if state_name in ["Start", "Goal", "Last"]:
#                     continue

#                 other_state = Saved_States[state_name]
#                 if (State.items() == other_state.items()):
#                     #print("I remember this place...", state_name, ",", Plan_Name)
#                     if Plan_Name == state_name: # We're already checking from here
#                         break#bad = "Yes"
#                     elif len(Plan_Name) < len(state_name):
#                         # This plan gets to this state quicker
#                         del Saved_States[state_name]
#                         save_state(State, Plan_Name)
#                         # But We're already checking from here
#                     else:
#                         # This is worse than older states
#                         Plan_Name = state_name
#                     escape = True
#                     break

#             print(Plan_Name, escape)
#             if escape:
#                 continue
#             """
#             # Save this new state
#             save_state(State, Plan_Name)

#             # If fulfils the goal
#             if check_goal(State):
#                 new_len = len(Plan_Name)
#                 #if new_len < best_len:
#                 print(f"FOUND GOAL AT For {Name} {operator} {args}")
#                 best_len = new_len
#                 best_plan = Plan_Name

#                 done = True
#                 return best_len
#             # Else continue planning
#             best_len = plan(State, Plan_Name, steps_left - 1, best_len, operator == "Go")

#     #print("Eh")
#     return best_len







# print(State)
# print("-----PLANNING------")
# current_state = State
# best_plan = "Start"
# while not done:
#     length = oldPlan(current_state, best_plan, 5, 9999)
#     current_state = Saved_States[best_plan]

#     #build_goal(State)
#     #print("Distance:", distance_between(Goal, Saved_States["Goal"]))
#     #print("Length:", length)

#     #print("Plan:", best_plan)
#     done = True
# print("----End Options----")
# print("End Search")

# print(plans)
# print("Plan:", best_plan)
# print([state + "\n" for state in Saved_States])
# ##Possible_New_Locations = [loc for loc in Known_Locations if loc != ls]
# ##for new_loc in Possible_New_Locations:
# ##    
# ##    Operation("Go", ["A", new_loc]);build_goal(State)
# ##    #print(f"Score if Go from \"A\" to \"{new_loc}\": {distance_between(State, Saved_States['Goal'])}")
# ##    save_state(State, f"Go {'A'},{new_loc}")
# ##    State = load_state("Last")