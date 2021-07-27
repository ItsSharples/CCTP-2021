

import copy
from typing import List, Tuple
from Events import PlanEvents
from Planner import NullPlan, Plan
from Operation import Action, Event


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
        
        self.Days : List[Tuple[List[Action], List[Event]]] = list();

        self.StepsPerDay = 6
        self.Day = 0

        self.__clearCache()

    def SetStateToPlan(self, thisPlan : Plan):
        self.CurrentPlan = thisPlan;
        self.CurrentState = self.CurrentPlan.CurrentState;
        self.__clearCache()

    @property
    def StepsSoFar(self) -> int:
        return self.Day * self.StepsPerDay

    @property
    def DaysPassed(self) -> int:
        return self.Day;

    @property
    def ExpectedCount(self) -> Tuple[int, int]:
        return (self.Day * self.StepsPerDay, self.Day - 1)

    @property
    def StepsTaken(self) -> int:
        return sum([day.NumSteps for day in self.Days])

    @property
    def IsJournalComplete(self) -> bool:
        return self.CompletePlan.Completed;
    
    @property
    def NumSteps(self) -> int:
        return self.CompletePlan.TotalOperations

    @property
    def NumActionsTaken(self) -> int:
        return self.CompletePlan.ActionsTaken

    @property
    def EventsEncountered(self) -> int:
        return self.CompletePlan.EventsEncountered

    @property
    def CompletePlan(self) -> Plan:
        if self.__CompletePlan != None:
            return self.__CompletePlan
        # Get all Operations that aren't Start, these happen at the start of every day
        operations = [operation for Day in self.Days for operation in Day[0] if operation.Operator != "Start"]
        # print([repr(operation) for operation in operations])
        self.__CompletePlan = Plan.CreateFromOperations(operations, self.StartingState)
        return self.__CompletePlan

    def __clearCache(self):
        self.__CompletePlan = None
        


    def DoDay(self):
        # Maybe Do the Planning In the background before needing it?
        self.BestPlan = Plans.oldPlan(self.CurrentPlan)

        furthestAbleToGo, newBest = self.BestPlan.SplitByNthStep(self.StepsPerDay)
        # TodaysEndPlan = Plan.MakeEmptyPlan(furthestAbleToGo.CurrentState);
        TodaysEndPlan = Plan(Action("Start", f"Day {self.Day}"), None, furthestAbleToGo.CurrentState)

        self.Days.append((furthestAbleToGo.Operations, None))
        self.SetStateToPlan(TodaysEndPlan)
        self.BestPlan = newBest

        # print("Current Plan");
        # print(furthestAbleToGo)
        
        self.Day += 1

        return

    def DoEvents(self):
        if self.IsJournalComplete:
            return
        EventName, EventActions = PlanEvents(self.CurrentPlan)
        Events = list()
        EventPlan = copy.deepcopy(self.CurrentPlan)
        for action in EventActions:
            EventOf = Event(EventName, action)
            EventPlan = Plan(EventOf, EventPlan)
            Events.append(EventOf)

        self.Days[self.Day-1] = (self.Days[self.Day-1][0], Events)

        # TodaysEndPlan = Plan(Action("Start", f"Day {self.Day - 1}"), None, EventPlan.CurrentState)
        # self.SetStateToPlan(TodaysEndPlan)
        self.SetStateToPlan(EventPlan)
        if self.BestPlan == None:
            self.BestPlan = EventPlan
            return
        # The plan's been messed up, there's no best plan anymore,
        # but here's a corrupted version for the planner to base itself on
        self.BestPlan = self.BestPlan.AttachToPlan(EventPlan)
        return
