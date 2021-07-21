
from typing import Dict, List
from State import Operators


class Action:
    '''
        A Basic Operation. Stores the Operator Performed, and any Arguments given for it.\n
        Does not check if the Operation is valid in the current state.
    '''
    def __init__(this, Operator : str, Args : list = []):
        this.Operator = Operator;
        this.Arguments = Args;
        this.Requires = None;
        this.Substitutions = None;

        # This is just a Null Operation
        if Operator == "Start":
            return
        # A Disaster Operation
        if Operator == "Disaster":
            return

        this.OperatorSheet: Operator = Operators[Operator]
        this.Arguments : list[str] = this.OperatorSheet["Arguments"]

        # Fulfil Requirements
        if len(Args) != len(this.Arguments):
            raise ValueError(f"Args does not match Number of Arguments for this Operation (Needs {len(this.Arguments)}, Has {len(Args)}).")

        this.Substitutions : Dict[str, str] = {this.Arguments[index] : Args[index] for index in range(len(this.Arguments))}
        this.Arguments = Args    
        this.Requires = this.OperatorSheet["Requires"]
        this.Effect = this.OperatorSheet["Effect"]

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
        return f"{self.Operator} {self.Arguments}"


class Operation(Action):
    pass

class Disaster(Action):
    pass
