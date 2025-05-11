import argparse

# Parser pentru argumente din linia de comandă
parser = argparse.ArgumentParser(description="SAT solver")
parser.add_argument('--method', choices=['dp', 'dpll', 'resolution'], required=True,
                    help='Metoda de rezolvare (dp, dpll sau resolution)')
parser.add_argument('cnf_file', help='Calea către fișierul CNF (DIMACS)')
args = parser.parse_args()

def parse_dimacs(file_path):
    cnf = []
    with open(file_path, 'r') as f:
        for line in f:
            if line.startswith('c') or line.startswith('p'):
                continue
            clause = [int(x) for x in line.strip().split() if x != '0']
            if clause:
                cnf.append(set(clause))
    return cnf

# Funcție pentru rezolvare cu metoda de rezoluție
def resolution(cnf):
    # Creăm o mulțime de clauze pentru a evita duplicarea
    clauses = set(frozenset(clause) for clause in cnf)

    while True:
        new_clauses = set()
        # Comparăm fiecare pereche de clauze pentru a căuta literă opusă
        for clause1 in clauses:
            for clause2 in clauses:
                if clause1 == clause2:
                    continue
                # Căutăm litere opuse
                resolvent = resolve(clause1, clause2)
                if resolvent is None:
                    continue
                if not resolvent:
                    return False  # Satisfiabilitatea nu este posibilă, am găsit o clauză goală
                new_clauses.add(frozenset(resolvent))
        
        # Dacă nu am găsit noi clauze, algoritmul s-a terminat
        if new_clauses.issubset(clauses):
            break
        clauses.update(new_clauses)

    return True

def resolve(clause1, clause2):
    for lit in clause1:
        if -lit in clause2:
            # Formează rezolvarea fără literalul opus
            new_clause = (clause1 - {lit}) | (clause2 - {-lit})
            return new_clause
    return None  # Nu s-a găsit literal opus, nu se poate rezolva


def dp_sat(cnf):
    cnf = set(frozenset(c) for c in cnf)
    if not cnf:
        return True
    if frozenset() in cnf:
        return False
    all_lits = {abs(l) for cl in cnf for l in cl}
    if not all_lits:
        return True
    var = next(iter(all_lits))
    c_pos = {c for c in cnf if var in c}
    c_neg = {c for c in cnf if -var in c}
    c_other = cnf - c_pos - c_neg
    new_clauses = set()
    for c1 in c_pos:
        for c2 in c_neg:
            resolvent = (c1 - {var}) | (c2 - {-var})
            if any(l in resolvent and -l in resolvent for l in resolvent):
                continue
            new_clauses.add(frozenset(resolvent))
    cnf_new = c_other | new_clauses
    return dp_sat([set(c) for c in cnf_new])

def dpll(cnf):
    cnf = [set(c) for c in cnf]
    if not cnf:
        return True
    if any(len(c) == 0 for c in cnf):
        return False
    for clause in cnf:
        if len(clause) == 1:
            unit = next(iter(clause))
            new_cnf = []
            for c in cnf:
                if unit in c:
                    continue
                if -unit in c:
                    new_c = c.copy()
                    new_c.remove(-unit)
                    new_cnf.append(new_c)
                else:
                    new_cnf.append(c.copy())
            return dpll(new_cnf)
    all_lits = {l for c in cnf for l in c}
    for lit in list(all_lits):
        if -lit not in all_lits:
            new_cnf = [c.copy() for c in cnf if lit not in c]
            return dpll(new_cnf)
    lit = next(iter(cnf[0]))
    new_cnf = []
    for c in cnf:
        if lit in c:
            continue
        if -lit in c:
            new_c = c.copy()
            new_c.remove(-lit)
            new_cnf.append(new_c)
        else:
            new_cnf.append(c.copy())
    if dpll(new_cnf):
        return True
    new_cnf = []
    for c in cnf:
        if -lit in c:
            continue
        if lit in c:
            new_c = c.copy()
            new_c.remove(lit)
            new_cnf.append(new_c)
        else:
            new_cnf.append(c.copy())
    return dpll(new_cnf)

if __name__ == "__main__":
    cnf = parse_dimacs(args.cnf_file)

    if args.method == "dp":
        result = dp_sat(cnf)
    elif args.method == "dpll":
        result = dpll(cnf)
    elif args.method == "resolution":
        result = resolution(cnf)
    else:
        print("Metoda aleasă nu este validă.")
        exit(1)

    print("Satisfiabilă" if result else "Nesatisfiabilă")
