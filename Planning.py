from __future__ import annotations
# Copy Objects
import copy
# Multiply Arrays
import math
from typing import Any, NoReturn

####################################################

StartingState = {
	"at" : [("Actor", "Home"), ("Scarecrow", "Field"), ("Tools", "Shed"), ("Seeds", "Shed")],
	"graspable" : ["Tools", "Seeds"],
	"farmable" : ["Crops"]
}

Operators = {
	"Go" : {
	"Arguments" : ["x", "y"],
	"Requires": {
		"at" : [("Actor", "x")]
	},
	"Effect" : {
		"at" : [("Actor", "y"), ("Actor", "x", "Not")]
	}
	},
# General Interaction
	"Grasp" : {
	"Arguments" : ["grab"],
	"Requires":{
		"at" : [("Actor","x"), ("grab","x")],
		"graspable" : ["grab"]
	},
	"Effect" : {
		"have" : [("Actor", "grab")],
		"at":[("grab", "Inventory"), ("grab", "x", "Not")]
	}
	},
	"Drop" : {
	"Arguments" : ["drop"],
	"Requires":{
        "at" : [("Actor", "x"), ("drop", "Inventory")]
        },
	"Effect" : {
		"at" : [("drop", "x"), ("drop", "Inventory", "Not")]
	}
	},
# Farming Stuff
	"Grow" : {
	"Arguments" : ["seed"],
	"Requires" : {
		"at" : [("Actor", "Field"), ("seed", "Inventory")]
	},
	"Effect" : {
		"at" : [("Crops", "Field"), ("seed", "Inventory", "Not")]
	}
	},

	"Farm" : {
	"Arguments" : ["crop"],
	"Requires" : {
		"at" : [("crop", "x"), ("Tools", "Inventory"), ("Actor", "Field")],
		"farmable" : ["crop"]
	},
	"Effect" : {
		"at" : [("crop", "x", "Not"), ("crop", "Inventory")]
	}
	}
}

OriginalGoal = {
	"at" : [("Actor", "Field"), ("Crops", "Home"), ("Tools", "Shed")],
}

####################################################

# Things that aren't arguments, but can be used to make Operations more generic
Known_Fudges = ["x", "y", "c", "h"]
# x is where the Actor is currently, y are Locations the Actor can go to, c is climb, h is height
def find_things(State : 'dict[str, Any]', Goal):
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

(Known_Things, Known_Locations) = find_things(StartingState, OriginalGoal)

StartingState = build_state(StartingState)
BuiltGoal = build_goal(StartingState)

class Operation:
    def __init__(this, Operator : str, Args : list = []):
        this.Operator = Operator;
        this.Args = Args;

    def __str__(self) -> str:
        return f"{self.Operator} {self.Args}"

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

def find_options(State) -> 'dict[str, list]':
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

class Plan:
    maxPlanDepth = 20
    childrenBeforeEndCheck = 5
    worstSimpleScore = 10
    worstGoalDistance = 10

    def __init__(self, First_Operation: Operation, parent: Plan):

        self.ThisOperation = First_Operation

        if self.ThisOperation.Operator == "Start":
            self.Parent = None
            self.Operations = [self.ThisOperation]
            self.CurrentState = StartingState
            self.ChildOf = 0;
            self.BasicScore = 9999999999;
            self.DeadEnd = False;

            self.Options = find_options(self.CurrentState)
            Operators = [x.Operator for x in self.Operations]
            self.SortedOperators = sorted(self.Options, key=Operators.count, reverse=True)
            self.StateHash = hash(str(self.CurrentState))

            self.Goal = build_goal(self.CurrentState);
            self.Completed = False;
            return;

        self.Parent : Plan = parent
        self.ChildOf = self.Parent.ChildOf + 1
        self.Operations : list[Operation] = self.Parent.Operations + [self.ThisOperation];
        self.CurrentState = DoOperation(self.Parent.CurrentState, self.ThisOperation);
        self.BasicScore = self.Operations.__len__();

        self.Options = find_options(self.CurrentState)
        # Sort the Options based on the already actioned Operations
        # The idea being that less common Options should be tried first
        Operators = [x.Operator for x in self.Operations]
        self.SortedOperators = sorted(self.Options, key=Operators.count, reverse=True)

        ## Sort State to enable good hash times
        for type in self.CurrentState:
            self.CurrentState[type] = sorted(self.CurrentState[type])

        self.StateHash: int = hash(str(self.CurrentState))

        self.Goal = build_goal(self.CurrentState);
        self.Completed = check_goal(self.CurrentState, self.Goal);

        self.SimpleScore = simple_score(self.CurrentState)
        self.DistanceToGoal = distance_between(self.CurrentState, self.Goal)

        self.DeadEnd = (self.ChildOf >= Plan.maxPlanDepth) or ((self.ChildOf >= Plan.childrenBeforeEndCheck) and (self.SimpleScore >= Plan.worstSimpleScore) and (self.DistanceToGoal >= Plan.worstGoalDistance))

        # optimised = self.Optimise()
        # while self.StateHash != optimised.StateHash:
        #     optimised = self.Optimise()
        # self = optimised

        #print(f"Plan: {self.ThisOperation}\nCurrent Options: {self.Options}\n\n")

    def Add(self, operation: Operation):
        self.Operations.append(operation)
        return self

    def MoveTo(self, newPlan: Plan):
        self = newPlan
        return self;

    def Optimise(self):
        return self.OptimiseDuplicates();

    def OptimiseDuplicates(self):
        # Find Duplicated States and Skip the Steps to go between them
        Parent = self;
        state_list : dict[str, list[Plan]] = dict()
        while Parent != None:
            plan = Parent
            
            if plan.StateHash in state_list:
                state_list[plan.StateHash].append(plan)
            else:
                state_list[plan.StateHash] = [plan]

            Parent = Parent.Parent

        conflicting_states = [plan_list for plan_list in state_list.values() if len(plan_list) > 1]
        # print(f"There are {len(conflicting_states)} states left")
        if len(conflicting_states) <= 0:
            # print(f"Optimised Plan: {this}")
            return self;
        
        biggest_pair : tuple[Plan, Plan] = None
        distance : int = 0

        ## Find the biggest leap to remove
        for array in conflicting_states:
            pairs = list(zip(array, array[1:] + array[:1]))
            pair: tuple[Plan, Plan]
            for pair in pairs:
                current_distance = pair[0].AgeDistance(pair[1]);
                if current_distance > distance:
                    biggest_pair = pair
                    distance = current_distance
        
        ## Update the Plan with this removed from it.
        (oldestPlan, jumpToPlan) = sorted(biggest_pair, key=lambda plan: plan.ChildOf)
        ## Reconstruct the plan, with three (or four) markers;
        ## Start -> oldestPlan | jumpToPlan -> thisPlan
        newPlan = copy.deepcopy(oldestPlan)
        index = jumpToPlan.ChildOf + 1
        operationsToDo = self.Operations[index:]
        completeOperations = newPlan.Operations + operationsToDo
        
        for operation in operationsToDo:
            newPlan = Plan(operation, newPlan)

        return newPlan.Optimise()

    def __str__(self) -> str:
        return " ".join([str(op) for op in self.Operations])

    def __len__(self) -> int:
        return self.BasicScore

    def AgeDistance(self, other: Plan) -> int:
        return abs(self.ChildOf - other.ChildOf);

    def GetNthPlan(self, n: int) -> Plan:
        currPlan = self;
        while currPlan.ChildOf != n:
            currPlan = currPlan.Parent
        return currPlan

def main():
    print(find_things(StartingState, OriginalGoal))
    StartPlan = Plan(Operation("Start"), None)

    print("Actor is currently at:", get_at(StartingState, "Actor"))

    options = find_options(StartingState)
    print("--- Start State ---")
    debug_text(StartingState)
    print("------Options------")

    def oldPlan(CurrPlan : Plan, BestPlan : Plan = None, last_operator = "") -> Plan:
        if CurrPlan.DeadEnd:
            return BestPlan
        if BestPlan.Completed:
            return BestPlan.Optimise()

        #options = find_options(CurrPlan.CurrentState)
        for operator in CurrPlan.SortedOperators:
            if operator == last_operator:
                continue
            for args in CurrPlan.Options[operator]:
                op = Operation(operator, args)
                NewPlan = Plan(op, CurrPlan)

                if NewPlan.DeadEnd:
                    return BestPlan

                if NewPlan.Completed:
                    NewPlan = NewPlan.Optimise();
                    if len(NewPlan) < len(BestPlan):
                        print(f"FOUND GOAL AT For {NewPlan}")
                        print(NewPlan.ChildOf);
                        BestPlan = NewPlan
                    return BestPlan

                BestPlan = oldPlan(NewPlan, BestPlan, operator)

        return BestPlan


    #print(StartingState)
    print("-----PLANNING------")
    BestPlan = oldPlan(StartPlan, StartPlan)
    print("Len", BestPlan.Operations.__len__())
    print(BestPlan.CurrentState)
    print(BestPlan)
    print(BestPlan.GetNthPlan(4))
    # print(OriginalGoal)
    # print(BestPlan.Goal)
    #print(Saved_States)
    #print(Saved_States[best_plan])
    print("----End Options----")
    #print(Known_Locations)
    print("End Search")

if __name__ == "__main__":
    main()