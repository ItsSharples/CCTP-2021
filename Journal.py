

import copy
from Disaster import DoDistaster, MoveRandomThing
from Planner import NullPlan, Plan
from Operation import Operation, Action

from copy import deepcopy
from Planning import build_state, build_goal
from State import StateType

import Plans

class Journal:
    def __init__(self, BaseState: StateType, GoalState: StateType, CurrentPlan : Plan = None):
        self.a = 1

        self.StartingState = build_state(BaseState)
        self.BuiltGoal = build_goal(self.StartingState, GoalState)

        self.CurrentState = deepcopy(self.StartingState)
        self.CurrentPlan =  CurrentPlan if CurrentPlan != None else NullPlan;
        self.BestPlan = deepcopy(self.CurrentPlan)

        self.Days : list[Plan] = list();

        self.StepsPerDay = 6
        self.Day = 1

    def SetStateToPlan(self, thisPlan : Plan):
        self.CurrentPlan = thisPlan;
        self.CurrentState = self.CurrentPlan.CurrentState;

    @property
    def StepsSoFar(self) -> int:
        return self.Day * self.StepsPerDay

    @property
    def DaysPassed(self) -> int:
        return self.Day - 1;

    @property
    def StepsTaken(self) -> int:
        return sum([day.NumSteps for day in self.Days])

    @property
    def IsJournalComplete(self) -> bool:
        return self.CurrentPlan.Completed;

    @property
    def CompletePlan(self) -> Plan:
        # Get all Operations that aren't Start, these happen at the start of every day
        operations = [operation for Day in self.Days for operation in Day.Operations if operation.Operator != "Start"]
        print([repr(operation) for operation in operations])
        completePlan = Plan.CreateFromOperations(operations, self.StartingState)

        return completePlan
        


    def DoDay(self):
        # Maybe Do the Planning In the background before needing it?
        self.BestPlan = Plans.oldPlan(self.CurrentPlan)

        furthestAbleToGo, newBest = self.BestPlan.SplitByNthStep(self.StepsPerDay)
        # TodaysEndPlan = Plan.MakeEmptyPlan(furthestAbleToGo.CurrentState);
        TodaysEndPlan = Plan(Action("Start", f"Day {self.Day}"), None, furthestAbleToGo.CurrentState)

        self.Days.append(furthestAbleToGo)
        self.SetStateToPlan(TodaysEndPlan)
        self.BestPlan = newBest

        print("Current Plan");
        print(furthestAbleToGo)
        
        self.Day += 1

        return

    def DoDisaster(self):
        if self.IsJournalComplete:
            return
        DisasterPlan = DoDistaster(self.CurrentPlan)
        self.SetStateToPlan(DisasterPlan)
        # The plan's been messed up, there's no best plan anymore,
        # but here's a corrupted version for the planner to base itself on
        self.BestPlan = self.BestPlan.AttachToPlan(DisasterPlan)
        return
