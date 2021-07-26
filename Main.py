
from Journal import Journal
from Planning import *
import State

def main():
    StartingState = State.StartingState
    OriginalGoal = State.OriginalGoal

    
    StartingState = build_state(StartingState)
    BuiltGoal = build_goal(StartingState, OriginalGoal)


    print(find_things(StartingState, OriginalGoal))

    # print("Actor is currently at:", get_at(StartingState, "Actor"))

    print("--- Start State ---")
    debug_text(StartingState)
    print("------Options------")

    currentJournal = Journal(StartingState, OriginalGoal);


    #print(StartingState)
    print("-----PLANNING------")
    while not currentJournal.IsJournalComplete:
        currentJournal.DoDay();
        currentJournal.DoDisaster();

    print(f"Took {currentJournal.DaysPassed} Days ({currentJournal.StepsTaken} Steps) to complete the Task")
    print([day.__repr__() for day in currentJournal.Days])
    print(currentJournal.CompletePlan)
    # BestPlan = Plans.oldPlan(StartPlan, StartPlan)
    # print("Len", BestPlan.Operations.__len__())
    # print(BestPlan.CurrentState)
    # print(BestPlan)
    # plan = BestPlan.GetNthStep(4)
    # plan.CurrentState = DoDistaster(plan.CurrentState)

    # BestPlan = Plans.oldPlan(plan, StartPlan)
    # print("Len", BestPlan.Operations.__len__())
    # print(BestPlan.CurrentState)
    # print(BestPlan)
    # plan = BestPlan.GetNthStep(4)
    # newState = DoDistaster(plan.CurrentState)
    # print(OriginalGoal)
    # print(BestPlan.Goal)
    #print(Saved_States)
    #print(Saved_States[best_plan])
    print("----End Options----")
    #print(Known_Locations)
    print("End Search")

if __name__ == "__main__":
    main()