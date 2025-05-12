class IRInstruction:
    def __init__(self, opcode, arg=None):
        self.opcode = opcode
        self.arg = arg

    def __str__(self):
        return f"{self.opcode}" + (f" {self.arg}" if self.arg is not None else "")

    def __repr__(self):
        return str(self)
