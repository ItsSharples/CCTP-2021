class Operation:
    def __init__(this, Operator : str, Args : list = []):
        this.Operator = Operator;
        this.Args = Args;

    def __str__(self) -> str:
        return f"{self.Operator} {self.Args}"
