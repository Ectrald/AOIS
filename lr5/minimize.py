import re
from itertools import combinations, product


def get_variables_from_expression(expr):
    """Извлекает список переменных из выражения (например, 'A', 'B' из 'A & !B')"""
    return sorted(set(c for c in expr if c.isalpha()))


def parse_logic_expression(expr, is_dnf=True):
    """
    Разбирает логическое выражение на список термов.
    Для DNF: разбивает по ИЛИ, затем по И
    Для KNF: разбивает по И, затем по ИЛИ
    """
    variables = get_variables_from_expression(expr)
    if is_dnf:
        # Разбиваем на конъюнкты по ИЛИ
        conjunctions = [t.strip('() ') for t in re.split(r'\s*\|\s*', expr)]
        # Разбиваем каждый конъюнкт на литералы по И
        term_lists = [re.split(r'\s*&\s*', conj) for conj in conjunctions if conj]
    else:
        # Разбиваем на дизъюнкты по И
        disjunctions = [t.strip('() ') for t in re.split(r'\s*&\s*', expr)]
        # Разбиваем каждый дизъюнкт на литералы по ИЛИ
        term_lists = [re.split(r'\s*\|\s*', disj) for disj in disjunctions if disj]

    # Нормализуем термы (добавляем недостающие переменные как '-')
    for term in term_lists:
        present_vars = {re.sub(r'^!', '', lit) for lit in term}
        missing_vars = set(variables) - present_vars
        for var in missing_vars:
            term.append('-')

    return term_lists, variables


def term_to_string(term, is_dnf=True):
    """Преобразует терм в строковое представление"""
    if is_dnf:
        return ' & '.join(lit for lit in term if lit != '-')
    else:
        return ' | '.join(lit for lit in term if lit != '-')


def implicants_to_string(implicants, is_dnf=True):
    """Преобразует список импликант в строку"""
    if is_dnf:
        return ' | '.join(f"({term_to_string(imp, True)})" for imp in implicants)
    else:
        return ' & '.join(f"({term_to_string(imp, False)})" for imp in implicants)


def find_term_differences(term1, term2):
    """Находит количество различий между двумя термами"""
    return sum(1 for t1, t2 in zip(term1, term2) if t1 != t2)


def combine_terms(term1, term2):
    """Объединяет два терма с одним различием"""
    return [t1 if t1 == t2 else '-' for t1, t2 in zip(term1, term2)]


def minimize_boolean_expression(expr, is_dnf=True):
    """
    Минимизирует логическое выражение методом Квайна-МакКласки
    Возвращает (минимизированное_выражение, переменные)
    """
    terms, variables = parse_logic_expression(expr, is_dnf)
    prime_implicants = []
    current_terms = terms.copy()

    # Этап нахождения всех простых импликант
    while True:
        new_terms = []
        used_indices = set()

        for i, j in combinations(range(len(current_terms)), 2):
            if find_term_differences(current_terms[i], current_terms[j]) == 1:
                combined = combine_terms(current_terms[i], current_terms[j])
                if combined not in new_terms:
                    new_terms.append(combined)
                used_indices.add(i)
                used_indices.add(j)

        # Добавляем термы, которые не удалось объединить
        prime_implicants.extend(
            term for idx, term in enumerate(current_terms)
            if idx not in used_indices
        )

        if not new_terms:
            break

        current_terms = new_terms

    # Удаляем дубликаты
    unique_primes = []
    seen = set()
    for term in prime_implicants:
        term_key = tuple(term)
        if term_key not in seen:
            seen.add(term_key)
            unique_primes.append(term)

    # Этап удаления избыточных импликант
    essential_implicants = remove_redundant_implicants(unique_primes, variables, is_dnf)

    minimized_expr = implicants_to_string(essential_implicants, is_dnf)
    return minimized_expr, variables


def generate_assignments_for_term(term, variables):
    """Генерирует все возможные назначения переменных для терма"""
    fixed = {}
    free_vars = []

    for var, lit in zip(variables, term):
        if lit == '-':
            free_vars.append(var)
        elif lit.startswith('!'):
            fixed[var] = False
        else:
            fixed[var] = True

    assignments = []
    for values in product([False, True], repeat=len(free_vars)):
        assignment = fixed.copy()
        assignment.update(zip(free_vars, values))
        assignments.append(assignment)

    return assignments


def evaluate_dnf_term(term, assignment, variables):
    """Проверяет, выполняется ли терм ДНФ для данного назначения"""
    for var, lit in zip(variables, term):
        if lit == '-':
            continue
        expected = not lit.startswith('!')
        actual = assignment.get(var.replace('!', ''))
        if actual != expected:
            return False
    return True


def evaluate_knf_clause(clause, assignment, variables):
    """Проверяет, выполняется ли клауза КНФ для данного назначения"""
    for var, lit in zip(variables, clause):
        if lit == '-':
            return True
        expected = not lit.startswith('!')
        actual = assignment.get(var.replace('!', ''))
        if actual == expected:
            return True
    return False


def remove_redundant_implicants(implicants, variables, is_dnf):
    """Удаляет избыточные импликанты"""
    essential = implicants.copy()

    for term in implicants:
        others = [t for t in essential if t != term]
        is_redundant = True

        for assignment in generate_assignments_for_term(term, variables):
            if is_dnf:
                # Для ДНФ проверяем, покрывается ли другими импликантами
                covered = any(evaluate_dnf_term(t, assignment, variables) for t in others)
                if not covered:
                    is_redundant = False
                    break
            else:
                # Для КНФ проверяем, удовлетворяется ли другими клаузами
                satisfied = all(evaluate_knf_clause(t, assignment, variables) for t in others)
                if satisfied:
                    is_redundant = False
                    break

        if is_redundant and term in essential:
            essential.remove(term)

    return essential