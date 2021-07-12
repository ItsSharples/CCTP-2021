class Operation:
    '''
        A Basic Operation. Stores the Operator Performed, and any Arguments given for it.\n
        Does not check if the Operation is valid, or available to be performed at creation.
    '''
    def __init__(this, Operator : str, Args : list = []):
        this.Operator = Operator;
        this.Args = Args;

    def __str__(self) -> str:
        return f"{self.Operator} {self.Args}"
