from problem import make_problem
from metrics import run, print_table

ALGORITHMS = []

if __name__ == "__main__":
    problem = make_problem()
    print("State space size:", problem.state_space_size())
    results = [run(algo, problem) for algo in ALGORITHMS]
    if results:
        print_table(results)