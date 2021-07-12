

from Disaster import DoDistaster
from Planner import Plan
from Operation import Operation

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
        self.CurrentPlan =  CurrentPlan if CurrentPlan != None else Plan(Operation("Start"), None);
        self.BestPlan = deepcopy(self.CurrentPlan)

        self.StepsPerDay = 4
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
        return self.CurrentPlan.Steps;

    @property
    def IsJournalComplete(self) -> bool:
        return self.CurrentPlan.Completed;

    def DoDay(self):
        # Maybe Do the Planning In the background before needing it?
        self.BestPlan = Plans.oldPlan(self.CurrentPlan, self.BestPlan)

        furthestAbleToGo = self.BestPlan.GetNthStep(self.StepsSoFar)
        self.SetStateToPlan(furthestAbleToGo)

        print("Current Plan");
        print(furthestAbleToGo)
        self.Day += 1

        return

    def DoDisaster(self):
        DisasterState = DoDistaster(self.CurrentState)
        self.CurrentState = DisasterState
        self.CurrentPlan.UpdateState(self.CurrentState)
        return
