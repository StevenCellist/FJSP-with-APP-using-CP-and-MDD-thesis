# available machines with their functionalities
machines = {
    0 : ["input"],
    1 : ["print_A4"],
    2 : ["print_A4", "print_A3"],
    3 : ["snij_A3"],
    4 : ["bind_A4"],
    5 : ["output"]
}

# travel times between machines
travel = [
    [ 0, -1, -1, -1, -1,  0],
    [ 0,  0, -1, -1, -1, -1],
    [ 0, -1,  0,  1, -1, -1],
    [-1, -1,  1,  0,  0, -1],
    [-1,  3,  4,  2,  0, -1],
    [ 0,  2,  2,  2,  2,  0]
]

# setup/switch times between machine functions
setup = [
    [[1]],
    [[1]],
    [[1, 5],
     [5, 1]],
    [[1]],
    [[1]],
    [[1]]
]