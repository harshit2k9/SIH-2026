VERHOEFF_D = [
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9], [1, 2, 3, 4, 0, 6, 7, 8, 9, 5],
    [2, 3, 4, 0, 1, 7, 8, 9, 5, 6], [3, 4, 0, 1, 2, 8, 9, 5, 6, 7],
    [4, 0, 1, 2, 3, 9, 5, 6, 7, 8], [5, 9, 8, 7, 6, 0, 1, 2, 3, 4],
    [6, 5, 9, 8, 7, 1, 0, 4, 3, 2], [7, 6, 5, 9, 8, 2, 1, 0, 4, 3],
    [8, 7, 6, 5, 9, 3, 2, 1, 0, 4], [9, 8, 7, 6, 5, 4, 3, 2, 1, 0]
]
VERHOEFF_P = [
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9], [1, 5, 7, 6, 2, 8, 3, 0, 9, 4],
    [5, 8, 0, 3, 7, 9, 6, 1, 4, 2], [8, 9, 1, 6, 0, 4, 3, 5, 2, 7],
    [9, 4, 5, 3, 1, 2, 6, 8, 7, 0], [4, 2, 8, 6, 5, 7, 3, 9, 0, 1],
    [2, 7, 9, 3, 8, 0, 6, 4, 1, 5], [7, 0, 4, 6, 9, 1, 3, 2, 5, 8]
]

import random

def generate_valid_aadhaar():
    # Generate 11 random digits (first digit 2-9 to bypass the '0'/'1' check)
    first_11 = [str(random.randint(2, 9))] + [str(random.randint(0, 9)) for _ in range(10)]
    
    # Brute-force the 12th digit until the Verhoeff algorithm returns True
    for d in range(10):
        test_num = "".join(first_11) + str(d)
        clean_num = test_num
        c = 0
        for i, item in enumerate(reversed(clean_num)):
            c = VERHOEFF_D[c][VERHOEFF_P[i % 8][int(item)]]
        if c == 0:
            return test_num

print("Your valid test Aadhaar number is:", generate_valid_aadhaar())