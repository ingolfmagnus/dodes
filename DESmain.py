def main():
    C = encrypt(0x0123456789ABCDEF, 0x133457799BBCDFF1)
    print("encrypted to: ", C)
    return


def encrypt(M, K):
    keys = generateroundkeys(K)

    return 0


def generateroundkeys(K):
    Clist = []
    Dlist = []
    keys = []
    CD = 0
    shifts = [1, 1, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 1]

    Kplus = getkplus(K)
    C, D = getlr28(Kplus)
    Clist.append(C)
    Dlist.append(D)

    for i in range(16):
        C = Clist[i]
        D = Dlist[i]
        for j in range(shifts[i]):
            C = ((C << 1) + getbit(C, 1, wordsize=28)) & 0xfffffff
            D = ((D << 1) + getbit(D, 1, wordsize=28)) & 0xfffffff
        Clist.append(C)
        Dlist.append(D)
        CD = C * 2**28 + D
        keys.append(getsubkey(CD))
    return keys


def getlr32(bits):
    L = bits >> 32
    R = bits & 0xffffffff
    return L, R


def getlr28(bits):
    L = bits >> 28
    R = bits & 0xfffffff
    return L, R


def getkplus(K):
    PC1 = [57, 49, 41, 33, 25, 17, 9,
           1, 58, 50, 42, 34, 26, 18,
           10, 2, 59, 51, 43, 35, 27,
           19, 11, 3, 60, 52, 44, 36,
           63, 55, 47, 39, 31, 23, 15,
           7, 62, 54, 46, 38, 30, 22,
           14, 6, 61, 53, 45, 37, 29,
           21, 13, 5, 28, 20, 12, 4]
    Kplus = 0
    for i in PC1:
        Kplus <<= 1
        Kplus += getbit(K, i)
    return Kplus


def getsubkey(CD):
    PC2 = [14, 17, 11, 24, 1, 5,
           3, 28, 15, 6, 21, 10,
           23, 19, 12, 4, 26, 8,
           16, 7, 27, 20, 13, 2,
           41, 52, 31, 37, 47, 55,
           30, 40, 51, 45, 33, 48,
           44, 49, 39, 56, 34, 53,
           46, 42, 50, 36, 29, 32]
    K = 0
    for i in PC2:
        K <<= 1
        K += getbit(CD, i, wordsize=56)
    return K


def getbit(value, bit, wordsize=64):
    return value >> (wordsize - bit) & 1


def bin32(value):
    s = ""
    # vfor i in range(8):
    #    s +=  bin((value >> (8-i)) & 0xf)
    return bin(value)


main()
