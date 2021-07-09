

from State import StateType


def DoDistaster(CurrentState : StateType) -> StateType:

    at : list = CurrentState["at"]
    new_at = list()
    for pair in at:
        if pair[0] != "Scarecrow":
            new_at.append(pair)
    new_at.append(("Scarecrow", "Far Away"))
    CurrentState["at"] = new_at
    return CurrentState