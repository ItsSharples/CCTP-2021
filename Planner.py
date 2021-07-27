from __future__ import annotations
# Copy Objects
import copy
from typing import List, Tuple

from Planning import *
from Operation import Operation
import State, sys


class Plan:
    maxPlanDepth = 20
    childrenBeforeEndCheck = 5
    worstSimpleScore = 10
    worstGoalDistance = 10


    def MakeEmptyPlan(CurrentState: StateType) -> Plan:
        self = Plan(Action(None), None)
        self.Parent = None
        self.Operations = []
        self.CurrentState = CurrentState
        self.ParentCount = 0;
        self.DeadEnd = False;

        self.UpdateState(CurrentState)

        # self.Options = find_options(self.CurrentState)
        # Operators = [x.Operator for x in self.Operations]
        # self.SortedOperators = sorted(self.Options, key=Operators.count, reverse=True)
        # self.StateHash = hash(str(self.CurrentState))

        # self.Goal = build_goal(self.CurrentState, State.OriginalGoal);
        # self.Completed = False;
        return self;

    def __init__(self, First_Operation: Operation, parent: Plan, CurrentState: StateType = None):
        if First_Operation.Operator == None:
            return
        
        self.ThisOperation = First_Operation

        if self.ThisOperation.Operator == "Start":
            self.Parent = None
            self.Operations = [self.ThisOperation]
            self.CurrentState = State.StartingState if CurrentState == None else CurrentState
            self.ParentCount = 0;
            self.DeadEnd = False;

            self.UpdateState(self.CurrentState)
            return;

        self.Parent : Plan = parent
        self.ParentCount = self.Parent.ParentCount + 1
        self.Operations : list[Operation] = self.Parent.Operations + [self.ThisOperation];

        self.Type = self.ThisOperation.__class__.__name__

        if CurrentState == None:
            if self.Type == Event.__name__:
                self.CurrentState = State.SortState(DoOperation(self.Parent.CurrentState, self.ThisOperation, True));
            else:
                self.CurrentState = State.SortState(DoOperation(self.Parent.CurrentState, self.ThisOperation, False));

                # The Operation Failed, rip
                if self.CurrentState == self.Parent.CurrentState:
                    self.DeadEnd = True
                    self.UpdateState(self.CurrentState)
                    self = None
                    return

        else:
            self.CurrentState = CurrentState

        self.UpdateState(self.CurrentState);
        
        self.DeadEnd = (self.ParentCount >= Plan.maxPlanDepth) or ((self.ParentCount >= Plan.childrenBeforeEndCheck) and (self.SimpleScore >= Plan.worstSimpleScore) and (self.DistanceToGoal >= Plan.worstGoalDistance))

        # optimised = self.Optimise()
        # while self.StateHash != optimised.StateHash:
        #     optimised = self.Optimise()
        # self = optimised

        #print(f"Plan: {self.ThisOperation}\nCurrent Options: {self.Options}\n\n")

    def UpdateState(self, newState: StateType):
        self.Options = find_options(newState)
        self.UpdateOptions();

        self.StateHash: int = hash(str(newState))

        self.Goal = build_goal(newState, State.OriginalGoal);
        self.Completed = check_goal(newState, self.Goal);

        self.SimpleScore = simple_score(newState)
        self.DistanceToGoal = distance_between(newState, self.Goal)
        return

    def UpdateOptions(self):
        # Sort the Options based on the already actioned Operations
        # The idea being that less common Options should be tried first
        Operators = [x.Operator for x in self.Operations]
        self.SortedOperators = sorted(self.Options, key=Operators.count, reverse=True)

    def Add(self, operation: Action):
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
        (oldestPlan, jumpToPlan) = sorted(biggest_pair, key=lambda plan: plan.ParentCount)
        ## Reconstruct the plan, with three (or four) markers;
        ## Start -> oldestPlan | jumpToPlan -> thisPlan
        newPlan = copy.deepcopy(oldestPlan)
        index = jumpToPlan.ParentCount + 1
        operationsToDo = self.Operations[index:]
        completeOperations = newPlan.Operations + operationsToDo
        
        for operation in operationsToDo:
            newPlan = Plan(operation, newPlan)

        return newPlan.Optimise()

    def __str__(self) -> str:
        return ", ".join([str(op) for op in self.Operations])
    def __repr__(self) -> str:
        return self.__str__()

    def __len__(self) -> int:
        return self.TotalOperations

    @property
    def TotalOperations(self) -> int:
        if self.Parent == None:
            return sys.maxsize;
        else:
            return self.ActionsTaken + self.EventsEncountered;

    @property
    def ActionsTaken(self) -> int:
        if self.Parent == None: return 0
        return self.Parent.ActionsTaken + int(self.Type == Action.__name__)
       
    
    @property
    def EventsEncountered(self) -> int:
        if self.Parent == None: return 0
        return self.Parent.EventsEncountered + int(self.Type == Event.__name__)

    def AgeDistance(self, other: Plan) -> int:
        return abs(self.ParentCount - other.ParentCount);

    def GetNthStep(self, n: int) -> Plan:
        currPlan = self;
        while currPlan.ParentCount > (n + currPlan.EventsEncountered):
            currPlan = currPlan.Parent
        return currPlan
    
    def NthStepReverse(self, n: int, split: bool):
        nthPlan = self.GetNthStep(n)
        newOpList = self.Operations[len(nthPlan.Operations):]
        # Construct a new Plan from here
        newPlan = Plan.MakeEmptyPlan(CurrentState = nthPlan.CurrentState)
        for op in newOpList:
            newPlan = Plan(op, newPlan)

        if newOpList.__len__() == 0:
            newPlan = None
        
        if split:
            return (nthPlan, newPlan)
        else:
            return newPlan

    
    def GetNthStepReverse(self, n: int) -> Plan:
        return self.NthStepReverse(n, False)

    def SplitByNthStep(self, n: int) -> Tuple[Plan, Plan]:
        return self.NthStepReverse(n, True)

    def AttachToPlan(self, newPlan: Plan):
        operations = self.Operations
        for operation in operations:
            tmpNewPlan = Plan(operation, newPlan)
            if tmpNewPlan.DeadEnd:
                break
            
            newPlan = tmpNewPlan
            if newPlan.Completed:
                break
        return newPlan

    def Append(self, Operation: Action):
        return Plan(Operation, self)

    def CreateFromOperations(Operations: List[Action], OriginalState: StateType):
        plan = Plan(Action("Start"), None, OriginalState)
        for operation in Operations:
            plan = Plan(operation, plan)
        return plan

        

    

NullPlan = Plan(Action("Start"), None)
