
from Planner import Plan, Operation
from Planning import *
import State, Plans

def main():
    StartingState = State.StartingState
    OriginalGoal = State.OriginalGoal

    
    StartingState = build_state(StartingState)
    BuiltGoal = build_goal(StartingState, OriginalGoal)


    print(find_things(StartingState, OriginalGoal))
    StartPlan = Plan(Operation("Start"), None)

    print("Actor is currently at:", get_at(StartingState, "Actor"))

    options = find_options(StartingState)
    print("--- Start State ---")
    debug_text(StartingState)
    print("------Options------")



    #print(StartingState)
    print("-----PLANNING------")
    BestPlan = Plans.oldPlan(StartPlan, StartPlan)
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