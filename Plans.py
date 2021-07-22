from Planner import Plan
from Operation import Operation

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
                    # print(f"FOUND GOAL AT For {NewPlan}")
                    # print(NewPlan.ChildOf);
                    BestPlan = NewPlan
                return BestPlan

            BestPlan = oldPlan(NewPlan, BestPlan, operator)

    return BestPlan