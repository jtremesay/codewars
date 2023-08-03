def simulate(asm, argv):
    r0, r1 = None, None
    stack = []
    for ins in asm:
        if ins[:2] == "IM" or ins[:2] == "AR":
            ins, n = ins[:2], int(ins[2:])
        if ins == "IM":
            r0 = n
        elif ins == "AR":
            r0 = argv[n]
        elif ins == "SW":
            r0, r1 = r1, r0
        elif ins == "PU":
            stack.append(r0)
        elif ins == "PO":
            r0 = stack.pop()
        elif ins == "AD":
            r0 += r1
        elif ins == "SU":
            r0 -= r1
        elif ins == "MU":
            r0 *= r1
        elif ins == "DI":
            r0 /= r1

    return r0
