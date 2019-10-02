from sys import argv
import numpy as np


class OptimalReached(StopIteration):
    pass

class ManyOptimum(StopIteration):
    pass 

class UnboundedProblem(StopIteration):
    pass

def pick_pivot_col(canonical_tableau, non_basic_cols):
    # " If all the entries in the objective row are less than or equal to 0 
    # then no choice of entering variable can be made and the solution is in fact optimal. "
    is_optimal = np.all(canonical_tableau[0, non_basic_cols] < 0)
    if is_optimal:
        raise OptimalReached()
    elif np.all(canonical_tableau[0, non_basic_cols] <= 0):
        raise ManyOptimum()

    return non_basic_cols[np.argmax(canonical_tableau[0, non_basic_cols])]

def pick_pivot_row(canonical_tableau, col_to_pick, ineq_rows):
    """
    ==> Performs `minimum ratio test` according to wikipedia:
    " Next, the pivot row must be selected so that all the other basic variables remain positive. 
    A calculation shows that this occurs when the resulting value of the entering variable is at a minimum. 
    In other words, if the pivot column is c, then the pivot row r is chosen so that

    b_{r}/a_{rc}

    is the minimum over all r so that arc > 0. This is called the minimum ratio test.
    If there is more than one row for which the minimum is achieved then a dropping variable choice rule
    can be used to make the determination. "

    argmin(r, b_{r}/a_{rc}) <=> argmax(r, a_{rc}/b_{r}) but the example in wikipedia looks at a_{rc}/b_{r}, not
    b_{r}/a_{rc} for some reason...
    """

    # " First, only positive entries in the pivot column are considered since this guarantees 
    # that the value of the entering variable will be nonnegative. 
    # If there are no positive entries in the pivot column then the entering variable 
    # can take any nonnegative value with the solution remaining feasible. 
    # In this case the objective function is unbounded below and there is no minimum. "
    #
    # TL;DR: Discards rows indices with negative values
    non_negative_mask = np.where(canonical_tableau[ineq_rows, col_to_pick] >= 0)[0]

    # +1 'cause we ignore the first row of `canonical_tableau`
    rows_to_consider = ineq_rows[np.in1d(ineq_rows, non_negative_mask+1)]
    assert np.all(canonical_tableau[rows_to_consider, col_to_pick] >= 0), "Whoopsi doopsi non-negative values only !"

    if len(rows_to_consider) == 0:
        raise UnboundedProblem()

    row_idx_to_pick = np.argmax(
        # a_{rc}/b_{r}
        canonical_tableau[rows_to_consider, col_to_pick]/canonical_tableau[rows_to_consider, -1]
    )
    return rows_to_consider[row_idx_to_pick]

def perform_pivot(canonical_tableau, pivot_row, pivot_col):
    pivotted_canonical_tableau = canonical_tableau.copy().astype(np.float64)

    # Divide the pivot row by the pivot's value so that the pivot value is now 1
    pivotted_canonical_tableau[pivot_row] /= pivotted_canonical_tableau[pivot_row, pivot_col]

    # Find the coeffs of the pivot col
    column_coeffs = pivotted_canonical_tableau[:, pivot_col]
    # Casts those coeffs to a columns vector
    column_coeffs = column_coeffs[:, None]
    # Multiply the pivot row by those coeffs to create a matrix which, whenn added to the `pivotted_canonical_tableau`
    # will nullify the coeffs of the pivot col
    add_mult_ops = column_coeffs * pivotted_canonical_tableau[pivot_row]
    add_mult_ops[pivot_row] *= 0  # Make sure not to affect the pivot row itself

    # Perform the nullification of the col
    pivotted_canonical_tableau -= add_mult_ops

    return pivotted_canonical_tableau


def find_col_exiting_base(canonical_tableau, pivot_row):
    # Returns the index of the column which all values are null except for the pivot row1
    return np.where(
            np.all(
                np.delete(canonical_tableau.copy(), pivot_row, axis=0) == 0
            , axis=0)
        )[0][0]

def get_current_summit(canonical_tableau, non_basic_cols):
    vals = []
    for j in range(1, canonical_tableau.shape[1]-1):
        if j in non_basic_cols:
            vals.append(0)
            continue
        id_index = np.where(canonical_tableau[:, j] != 0)[0]
        vals.append((canonical_tableau[id_index, j] * canonical_tableau[id_index, -1])[0])

    return np.array(vals)

def main():
    # Wikipedia Example
    # min -2*x1 -3*x2 -4*x3
    # <=> max +2*x1 +3*x2 +4*x3

    # objective = lambda X: -2*X[0] - 3*X[1] - 4*X[2]
    # canonical_tableau = np.array([
    #     [1, 2, 3, 4, 0, 0, 0],
    #     [0, 3, 2, 1, 1, 0, 10],
    #     [0, 2, 5, 3, 0, 1, 15]
    # ])
    # non_basic_cols = [1, 2, 3]

    ############################################

    # Course example
    # max +3*x1 +4*x2

    objective = lambda X: 3*X[0] + 4*X[1]
    canonical_tableau = np.array([
        [1,  3,  4,  0,  0,  0, 0, 0, 0],
        [0,  1,  0,  1,  0,  0, 0, 0, 8],
        [0,  0,  1,  0,  1,  0, 0, 0, 6],
        [0, -1,  1,  0,  0,  1, 0, 0, 4],
        [0,  1, -1,  0,  0,  0, 1, 0, 7],
        [0,  1,  2,  0,  0,  0, 0, 1, 16],
    ])
    non_basic_cols = [1, 2]

    ############################################

    # Course many optimum (dégénerescence 1ere espèce)
    # max x1 + x2

    # objective = lambda X: X[0] + X[1]
    # canonical_tableau = np.array([
    #     [1,  1,  1,  0,  0,  0, 0],
    #     [0,  1,  1,  1,  0,  0, 12],
    #     [0,  3, -2,  0, -1,  0, 6],
    #     [0, -1,  4,  0,  0, -1, 8],
    # ])
    # non_basic_cols = [1, 2]

    ############################################

    # Course choix de base ambigue (dégénerescence 2eme espèce)
    # max x1 + 2*x2

    # objective = lambda X: X[0] + 2*X[1]
    # canonical_tableau = np.array([
    #     [1,  1,  2,  0,  0,  0, 0, 0],
    #     [0,  1,  1,  1,  0,  0, 0, 12],
    #     [0,  3, -2,  0, -1,  0, 0, 6],
    #     [0, -1,  4,  0,  0, -1, 0, 8],
    #     [0,  0,  1,  0,  0,  0, 1, 6],
    # ])
    # non_basic_cols = [1, 2]

    ############################################

    # Unbounded
    # max x1 + 2*x2

    # objective = lambda X: X[0] + 2*X[1]
    # canonical_tableau = np.array([
    #     [1,  1,  2,  0,  0, 0],
    #     [0,  3, -2, -1,  0, 6],
    #     [0, -1,  4,  0, -1, 8],
    # ])
    # non_basic_cols = [1, 2]

    ############################################

    INEQ_ROWS = np.arange(canonical_tableau.shape[0])[1:] # This should be a constant
    MAX_ITERATION = 1000

    for iteration in range(1, MAX_ITERATION+1):
        print("#"*70 + "\nIteration #", iteration)
        print("non_basic_cols: ", non_basic_cols)
        print(canonical_tableau.round(3))
        print("X = ", get_current_summit(canonical_tableau, non_basic_cols))
        iteration += 1
        try:
            col_to_pick = pick_pivot_col(canonical_tableau, non_basic_cols)
        except (OptimalReached, ManyOptimum) as e:
            if isinstance(e, OptimalReached):
                print("Optimal reached ! Hurray !")
            else:
                print("Many optimum reached ! Double hurray !")

            if np.sum(canonical_tableau[1:, -1] == 0) > 0:
                inter_count = np.sum(canonical_tableau[1:, -1] == 0) + len(non_basic_cols)
                print(f"Degeneresence type 2 ! {inter_count} intersection")

            print("Optimal value = ", objective(get_current_summit(canonical_tableau, non_basic_cols)))
            exit(0)

        print("col_to_pick :", col_to_pick)

        try:
            row_to_pick = pick_pivot_row(canonical_tableau, col_to_pick, INEQ_ROWS)
        except UnboundedProblem:
            print("Unbounded problem")
            exit(0)

        print("row_to_pick :", row_to_pick)

        col_exiting_base = find_col_exiting_base(canonical_tableau, pivot_row=row_to_pick)
        print("col_exiting_base: ", col_exiting_base)

        canonical_tableau = perform_pivot(canonical_tableau, row_to_pick, col_to_pick)

        non_basic_cols.remove(col_to_pick)
        non_basic_cols.append(col_exiting_base)

        if len(argv) > 1 and "-v" in argv[1]:
            input("Press enter for next iteration...")

    print(f"Max iteration exceeded ! (>{MAX_ITERATION})")
    exit(1)

if __name__ == '__main__':
    main()
