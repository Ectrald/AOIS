def implication(p, q):
    return not p or q

def equivalence(p, q):
    return p == q

def generate_truth_values(n):
    values = []
    for i in range(2 ** n):
        values.append([bool(int(x)) for x in bin(i)[2:].zfill(n)])
    return values

def precedence(op):
    if op == '!':
        return 3
    if op in ('&', '|'):
        return 2
    if op in ('->', '~'):
        return 1
    return 0

def infix_to_postfix(expression):
    output = []
    stack = []
    i = 0
    while i < len(expression):
        if expression[i].isalpha():
            output.append(expression[i])
        elif expression[i] in "!&|":
            while stack and precedence(stack[-1]) >= precedence(expression[i]):
                output.append(stack.pop())
            stack.append(expression[i])
        elif expression[i] == '-' and i + 1 < len(expression) and expression[i + 1] == '>':
            while stack and precedence(stack[-1]) >= precedence('->'):
                output.append(stack.pop())
            stack.append("->")
            i += 1
        elif expression[i] == '~':
            while stack and precedence(stack[-1]) >= precedence('~'):
                output.append(stack.pop())
            stack.append("~")
        elif expression[i] == '(':
            stack.append(expression[i])
        elif expression[i] == ')':
            while stack and stack[-1] != '(':
                output.append(stack.pop())
            stack.pop()
        i += 1
    while stack:
        output.append(stack.pop())
    return output

def evaluate_postfix(postfix_tokens, values):
    stack = []
    operators = {"&": lambda a, b: a and b, "|": lambda a, b: a or b,
                 "!": lambda a: not a, "->": implication, "~": equivalence}
    for token in postfix_tokens:
        if token in values:
            stack.append(values[token])
        elif token in operators:
            if token == "!":
                operand = stack.pop()
                stack.append(operators[token](operand))
            else:
                b = stack.pop()
                a = stack.pop()
                stack.append(operators[token](a, b))
        else:
            raise ValueError(f"Неизвестный токен: {token}")
    return stack.pop()


def generate_sdnf_sknf(truth_table, variables):
    sdnf = []
    sknf = []
    sdnf_indices = []
    sknf_indices = []
    for i, row in enumerate(truth_table):
        values, result = row[:-1], row[-1]
        term = []
        clause = []
        for var, val in zip(variables, values):
            if val:
                term.append(var)
                clause.append(f"!{var}")
            else:
                term.append(f"!{var}")
                clause.append(var)
        if result:
            sdnf.append(f"({' & '.join(term)})")
            sdnf_indices.append(str(i))
        else:
            sknf.append(f"({' | '.join(clause)})")
            sknf_indices.append(str(i))
    return " | ".join(sdnf), " & ".join(sknf), sdnf_indices, sknf_indices


def truth_table(expression, variables):
    postfix_tokens = infix_to_postfix(expression)
    table = []
    print(" | ".join(variables) + " | Result")
    print("-" * (len(variables) * 4 + 10))

    for values in generate_truth_values(len(variables)):
        values_dict = dict(zip(variables, values))
        result = evaluate_postfix(postfix_tokens, values_dict)
        row = [int(values_dict[var]) for var in variables] + [int(result)]
        table.append(row)
        print(" | ".join(map(str, row)))

    sdnf, sknf, sdnf_indices, sknf_indices = generate_sdnf_sknf(table, variables)

    index_bits = [str(row[-1]) for row in table]  # Берём последний столбец (результат)
    index_binary = ''.join(index_bits)  # Получаем бинарное представление
    index_decimal = int(index_binary, 2)  # Переводим в десятичное число

    index_form = f"{index_decimal} - {index_binary}"

    print("\nСДНФ:", sdnf)
    print("Числовая форма СДНФ:", ", ".join(sdnf_indices))
    print("СКНФ:", sknf)
    print("Числовая форма СКНФ:", ", ".join(sknf_indices))
    print("Индексная форма функции:", index_form)
    return index_form
if __name__ == "__main__":
    expression = input("Введите логическое выражение (a, b, c, d, e, &, |, !, ->, ~): ")
    variables = sorted(set(filter(str.isalpha, expression)))
    truth_table(expression, variables)
