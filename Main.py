
from Journal import Journal
from Planning import *
import State

def main():
    StartingState = build_state(State.StartingState)
    OriginalGoal = State.OriginalGoal

    # BuiltGoal = build_goal(StartingState, OriginalGoal)

    print(find_things(StartingState, OriginalGoal))

    print("--- Start State ---")
    debug_text(StartingState)
    print("------Options------")

    currentJournal = Journal(StartingState, OriginalGoal);

    print("-----PLANNING------")
    while not currentJournal.IsJournalComplete:
        currentJournal.DoDay();
        currentJournal.DoEvents();

    print(f"Took {currentJournal.DaysPassed} Days ({currentJournal.NumSteps}: {currentJournal.NumActionsTaken} Steps [{currentJournal.EventsEncountered} Events]) to complete the Task")
    print(f"Expects ({currentJournal.ExpectedCount})")
    print([day.__repr__() for day in currentJournal.Days])
    print(currentJournal.CompletePlan)

    print("----End Options----")
    #print(Known_Locations)
    print("End Search")

if __name__ == "__main__":
    main()