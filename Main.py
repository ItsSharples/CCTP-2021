
from Planner import Plan, Operation
from Planning import *
from State import OriginalGoal, StartingState
import State

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