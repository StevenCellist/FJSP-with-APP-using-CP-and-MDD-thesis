# Expanded list of machines with added functionalities
machines = {
    0 : ["input"],
    1 : ["print_A4"],
    2 : ["print_A4", "print_A3"],
    3 : ["snij_A3"],
    4 : ["bind_A4"],
    5 : ["print_A3", "snij_A3"],
    6 : ["print_A4", "print_A3"],
    7 : ["bind_A4", "bind_A3"],
    8 : ["print_A4", "laminate"],
    9 : ["laminate"],
    10: ["quality_check"],
    11: ["output"]
}

# Expanded travel times matrix
travel = [
    [ 0,  1,  2, -1, -1,  1, -1,  2, -1, -1, -1,  0],
    [ 0,  0, -1, -1,  2, -1, -1, -1,  3,  2, -1, -1],
    [ 0, -1,  0,  1, -1, -1,  1, -1, -1,  2, -1, -1],
    [-1, -1,  1,  0,  1, -1,  2, -1,  2, -1,  2, -1],
    [-1,  2, -1,  1,  0,  1, -1,  3,  2, -1, -1, -1],
    [ 0, -1, -1, -1,  1,  0, -1,  2, -1, -1, -1, -1],
    [-1, -1,  1,  2, -1, -1,  0, -1, -1,  2,  3, -1],
    [ 0, -1, -1, -1,  3,  2, -1,  0,  1, -1, -1, -1],
    [-1,  3, -1,  2,  2, -1, -1,  1,  0, -1, -1, -1],
    [-1,  2,  2, -1, -1, -1,  2, -1, -1,  0,  2, -1],
    [-1, -1, -1,  2, -1, -1,  3, -1, -1,  2,  0, -1],
    [ 0,  1,  3,  1,  1,  3,  1,  2,  1,  3,  1,  0]
]

# Expanded setup times matrix
setup = [
    [[1]],                                   # Machine 0 (input only)
    [[1]],                                   # Machine 1 (print_A4 only)
    [[1, 5], [5, 1]],                        # Machine 2 (print_A4 and print_A3)
    [[1]],                                   # Machine 3 (snij_A3 only)
    [[1]],                                   # Machine 4 (bind_A4 only)
    [[1, 2], [2, 1]],                        # Machine 5 (print_A3 and snij_A3)
    [[1, 3], [3, 1]],                        # Machine 6 (input and output)
    [[1, 4], [4, 1]],                        # Machine 7 (bind_A4 and bind_A3)
    [[1, 3], [3, 1]],                        # Machine 8 (print_A4 and laminate)
    [[1]],                                   # Machine 9 (laminate only)
    [[1]],                                   # Machine 10 (quality_check only)
    [[1]]                                    # Machine 11 (output only)
]
