class Memory:
    def __init__(self, size=1024):
        self.memory = bytearray(size)

    def grow(self, size):
        self.memory += bytearray(size)

    def read_int(self, addr):
        return int.from_bytes(self.memory[addr:addr+4], 'little')

    def write_int(self, addr, value):
        self.memory[addr:addr+4] = value.to_bytes(4, 'little')

    def read_float(self, addr):
        import struct
        return struct.unpack('f', self.memory[addr:addr+4])[0]

    def write_float(self, addr, value):
        import struct
        self.memory[addr:addr+4] = struct.pack('f', value)


class CallFrame:
    def __init__(self, return_address, local_vars):
        self.return_address = return_address
        self.locals = local_vars


class StackMachine:
    def __init__(self, instructions):
        self.instructions = instructions
        self.pc = 0
        self.stack = []
        self.memory = Memory()
        self.globals = {}
        self.frames = []
        self.labels = self.find_labels()

    def find_labels(self):
        labels = {}
        for i, instr in enumerate(self.instructions):
            if instr.opcode == 'LABEL':
                labels[instr.arg] = i
        return labels

    def run(self):
        while self.pc < len(self.instructions):
            instr = self.instructions[self.pc]
            self.pc += 1
            self.execute(instr)

    def execute(self, instr):
        op = instr.opcode
        arg = instr.arg

        if op == 'CONSTI':
            self.stack.append(int(arg))
        elif op == 'CONSTR':
            self.stack.append(float(arg))
        elif op == 'CONSTB':
            self.stack.append(bool(arg))
        elif op == 'LOCAL_SET':
            self.current_frame().locals[arg] = self.stack.pop()
        elif op == 'LOCAL_GET':
            self.stack.append(self.current_frame().locals[arg])
        elif op == 'GLOBAL_SET':
            self.globals[arg] = self.stack.pop()
        elif op == 'GLOBAL_GET':
            self.stack.append(self.globals[arg])

        elif op == 'ADDI':
            b, a = self.stack.pop(), self.stack.pop()
            self.stack.append(a + b)
        elif op == 'SUBI':
            b, a = self.stack.pop(), self.stack.pop()
            self.stack.append(a - b)
        elif op == 'MULI':
            b, a = self.stack.pop(), self.stack.pop()
            self.stack.append(a * b)
        elif op == 'DIVI':
            b, a = self.stack.pop(), self.stack.pop()
            self.stack.append(a // b)

        elif op == 'AND':
            b, a = self.stack.pop(), self.stack.pop()
            self.stack.append(a and b)
        elif op == 'OR':
            b, a = self.stack.pop(), self.stack.pop()
            self.stack.append(a or b)
        elif op == 'EQ':
            b, a = self.stack.pop(), self.stack.pop()
            self.stack.append(a == b)
        elif op == 'NE':
            b, a = self.stack.pop(), self.stack.pop()
            self.stack.append(a != b)

        elif op == 'JUMP':
            self.pc = self.labels[arg]
        elif op == 'JUMP_IF_FALSE':
            cond = self.stack.pop()
            if not cond:
                self.pc = self.labels[arg]

        elif op == 'LABEL':
            pass

        elif op == 'CALL':
            self.frames.append(CallFrame(self.pc, {}))
            self.pc = self.labels[f"FUNC_{arg}"] + 1

        elif op == 'RETURN':
            frame = self.frames.pop()
            self.pc = frame.return_address

        elif op == 'PRINT':
            value = self.stack.pop()
            if isinstance(value, str):
                print(value, end='')
            elif isinstance(value, int) and 0 <= value <= 255:
                print(chr(value), end='')
            else:
                print(value, end='')

        elif op == 'GROW':
            self.memory.grow(arg)

        elif op == 'POKEI':
            value = self.stack.pop()
            addr = self.stack.pop()
            self.memory.write_int(addr, value)
        elif op == 'PEEKI':
            addr = self.stack.pop()
            self.stack.append(self.memory.read_int(addr))
        elif op == 'POKEF':
            value = self.stack.pop()
            addr = self.stack.pop()
            self.memory.write_float(addr, value)
        elif op == 'PEEKF':
            addr = self.stack.pop()
            self.stack.append(self.memory.read_float(addr))

        elif op == 'CAST':
            value = self.stack.pop()
            if arg == 'char':
                if isinstance(value, int):
                    self.stack.append(value)
                elif isinstance(value, str):
                    self.stack.append(ord(value))
                else:
                    raise Exception("CAST char: tipo no soportado")
            else:
                raise Exception(f"CAST no soportado: {arg}")

        else:
            raise Exception(f"Instrucción no soportada: {op}")

    def current_frame(self):
        return self.frames[-1] if self.frames else CallFrame(-1, self.globals)
