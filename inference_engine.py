def parse_input(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    
    tell_index = lines.index("TELL\n")
    ask_index = lines.index("ASK\n")
    
    kb = lines[tell_index + 1:ask_index]
    kb = " ".join(kb).replace("\n", "").split(";")
    kb = [clause.strip() for clause in kb if clause.strip()]
    
    query = lines[ask_index + 1].strip()
    
    return kb, query

def extract_symbols(clauses):
    symbols = set()
    for clause in clauses:
        for symbol in clause.replace("(", "").replace(")", "").split():
            if symbol not in ['&', '||', '=>', '<=>', '~']:
                symbols.add(symbol)
    return list(symbols)

def pl_true(clause, model):
    clause = clause.replace(' ', '')
    if '=>' in clause:
        premise, conclusion = clause.split('=>')
        return not pl_true(premise, model) or pl_true(conclusion, model)
    elif '&' in clause:
        return all(pl_true(part, model) for part in clause.split('&'))
    elif '||' in clause:
        return any(pl_true(part, model) for part in clause.split('||'))
    elif '<=>' in clause:
        part1, part2 = clause.split('<=>')
        return pl_true(part1, model) == pl_true(part2, model)
    elif '~' in clause:
        return not pl_true(clause[1:], model)
    else:
        return model.get(clause, False)

def tt_check_all(kb, query, symbols, model):
    if not symbols:
        if all(pl_true(clause, model) for clause in kb):
            return pl_true(query, model), 1
        else:
            return True, 0
    P, rest = symbols[0], symbols[1:]
    true_branch, true_count = tt_check_all(kb, query, rest, {**model, **{P: True}})
    false_branch, false_count = tt_check_all(kb, query, rest, {**model, **{P: False}})
    return (true_branch and false_branch), (true_count + false_count)

def tt_entails(kb, query):
    symbols = extract_symbols(kb + [query])
    result, count = tt_check_all(kb, query, symbols, {})
    return result, count

def forward_chaining(kb, query):
    known = set()
    inferred = {symbol: False for symbol in extract_symbols(kb)}
    count = {clause: len(clause.split('&')) for clause in kb if '=>' in clause}

    while True:
        something_inferred = False
        for clause in kb:
            if '=>' in clause:
                premise, conclusion = clause.split('=>')
                premise = premise.strip()
                conclusion = conclusion.strip()

                if all(symbol in known for symbol in premise.split('&')):
                    if not inferred[conclusion]:
                        inferred[conclusion] = True
                        known.add(conclusion)
                        something_inferred = True
                        if conclusion == query:
                            return True, known
        if not something_inferred:
            break
    return False, known

def backward_chaining(kb, query):
    inferred = {symbol: False for symbol in extract_symbols(kb)}
    return bc_or(kb, query, inferred, [])

def bc_or(kb, goal, inferred, path):
    if goal in path:
        return False, inferred
    if goal in inferred and inferred[goal]:
        return True, inferred
    
    for clause in kb:
        if '=>' in clause:
            premise, conclusion = clause.split('=>')
            conclusion = conclusion.strip()
            if conclusion == goal:
                premises = premise.split('&')
                premises = [p.strip() for p in premises]
                
                if all(bc_and(kb, p, inferred, path + [goal])[0] for p in premises):
                    inferred[goal] = True
                    return True, inferred
    return False, inferred

def bc_and(kb, goal, inferred, path):
    res, inferred = bc_or(kb, goal, inferred, path)
    if res:
        inferred[goal] = True
    return res, inferred
