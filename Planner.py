from __future__ import annotations
# Copy Objects
import copy

from Planning import *
import State


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
            self.CurrentState = State.StartingState
            self.ChildOf = 0;
            self.BasicScore = 9999999999;
            self.DeadEnd = False;

            self.Options = find_options(self.CurrentState)
            Operators = [x.Operator for x in self.Operations]
            self.SortedOperators = sorted(self.Options, key=Operators.count, reverse=True)
            self.StateHash = hash(str(self.CurrentState))

            self.Goal = build_goal(self.CurrentState, State.OriginalGoal);
            self.Completed = False;
            return;

        self.Parent : Plan = parent
        self.ChildOf = self.Parent.ChildOf + 1
        self.Operations : list[Operation] = self.Parent.Operations + [self.ThisOperation];
        self.CurrentState = State.SortState(DoOperation(self.Parent.CurrentState, self.ThisOperation));
        self.BasicScore = self.Operations.__len__();

        self.Options = find_options(self.CurrentState)
        # Sort the Options based on the already actioned Operations
        # The idea being that less common Options should be tried first
        Operators = [x.Operator for x in self.Operations]
        self.SortedOperators = sorted(self.Options, key=Operators.count, reverse=True)

        self.StateHash: int = hash(str(self.CurrentState))

        self.Goal = build_goal(self.CurrentState, State.OriginalGoal);
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