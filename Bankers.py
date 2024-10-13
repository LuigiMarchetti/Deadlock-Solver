class Info:
    def __init__(self, process_name, has, max):
        self.process_name = process_name
        self.has = has
        self.max = max

    def __repr__(self):
        return f"Info(process_name={self.process_name}, has={self.has}, max={self.max})"

resource_amount = 10
original_state = [Info("A", 3, 9), Info("B", 2, 4), Info("C", 2, 7)]

def main():
    run(original_state)

def run(state):
    allocated_resources = calc_allocated_resources(state)
    remaining_resources = resource_amount - allocated_resources
    print_state(state, remaining_resources)

    try:
        info = find_desired(state, remaining_resources)
        print(f"Adicionando {info.max - info.has} recursos ao Processo {info.process_name} e assim permitindo que ele rode")
        run(remove(state, info))
    except ValueError:
        if not state:
            print("Sem Deadlock :)")
        else:
            print("Deadlock")

def find_desired(state, remaining_resources):
    for info in state:
        if info.has + remaining_resources >= info.max:
            return info
    raise ValueError("No process can proceed")

def calc_allocated_resources(state):
    return sum(info.has for info in state)

def print_state(state, balance):
    print("")
    for info in state:
        print(f"{info.process_name} | {info.has} | {info.max}")
    print(f"Saldo: {balance}")
    print("")

def remove(state, target):
    return [info for info in state if info.process_name != target.process_name]

if __name__ == "__main__":
    main()
