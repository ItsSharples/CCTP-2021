
from typing import Dict, List
from State import Disasters, Operators, StateType


class Operation:
    '''
        A Basic Operation. Stores the Operator Performed, and any Arguments given for it.\n
        Does not check if the Operation is valid in the current state.
    '''
    def __init__(this, ChosenActionSheet, OperatorName : str, Args : list = []):
        this.Operator = OperatorName;
        this.Arguments = Args;
        this.Requires = None;
        this.Substitutions = None;
        this.Format = "{}"

        # This is just a Null Operation
        if OperatorName == "Start" or OperatorName == None:
            this.Format = str()
            return
        # A Disaster Operation
        if OperatorName == "Disaster":
            return

        this.OperatorSheet = ChosenActionSheet[OperatorName]
        this.Arguments : list[str] = this.OperatorSheet["Arguments"]

        # Fulfil Requirements
        if len(Args) != len(this.Arguments):
            raise ValueError(f"Args does not match Number of Arguments for this Operation (Needs {len(this.Arguments)}, Has {len(Args)}).")

        this.Substitutions : Dict[str, str] = {this.Arguments[index] : Args[index] for index in range(len(this.Arguments))}
        this.Arguments = Args
        # Fetch the Values
        this.OperatorSheet.setdefault(None)
        this.Requires: StateType = this.OperatorSheet.get("Requires")
        this.Effect: StateType = this.OperatorSheet.get("Effect")
        this.Format: str = this.OperatorSheet.get("Format")
        if this.Format == None:
            this.Format = "{}" * this.Arguments.__len__()

    def check_and_substitute(this, req: (tuple or str)):
        if type(req) != tuple:
            return this.check_and_substitute_value(req)
        else:
            return this.check_and_substitute_tuple(req)

    def check_and_substitute_tuple(this, Tuple: tuple, out_Not = False) -> tuple or 'list[tuple]':
        outlist = [this.Substitutions[x] if x in this.Substitutions else x for x in Tuple]
        Not = False
        # Remove all modifier values ("Not")
        for val in outlist:
            if val == "Not":
                Not = True
                del outlist[outlist.index(val)]
                
        Tuple = tuple(outlist)
        if len(Tuple) == 1:
            Tuple = (Tuple[0])

        # If I want to out Not, create a List, else just return the tuple
        return Tuple if not out_Not else [Tuple, Not]

    def check_and_substitute_value(this, x: str) -> str:
        # Return the Substitution if there is one, else return the original value
        return this.Substitutions[x] if x in this.Substitutions else x
    
    def __str__(self) -> str:
        return f"{self.Operator} {self.Format.format(*self.Arguments)}"
    
    def __repr__(self) -> str:
        return f"{self.__str__()} ({self.__class__.__name__})"


class Action(Operation):
    def __init__(this, Operator : str, Args : list = []):
        super().__init__(Operators, Operator, Args);


class Event(Operation):
    def __init__(this, Operator : str, Args : list = []):
        super().__init__(Disasters, Operator, Args);

