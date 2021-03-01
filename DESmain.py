def main():
    C = encrypt(0x0123456789ABCDEF, 0x133457799BBCDFF1)
    print("encrypted to: ", C)
    return


PC1 = [57, 49, 41, 33, 25, 17, 9,
       1, 58, 50, 42, 34, 26, 18,
       10, 2, 59, 51, 43, 35, 27,
       19, 11, 3, 60, 52, 44, 36,
       63, 55, 47, 39, 31, 23, 15,
       7, 62, 54, 46, 38, 30, 22,
       14, 6, 61, 53, 45, 37, 29,
       21, 13, 5, 28, 20, 12, 4]

PC2 = [14, 17, 11, 24, 1, 5,
       3, 28, 15, 6, 21, 10,
       23, 19, 12, 4, 26, 8,
       16, 7, 27, 20, 13, 2,
       41, 52, 31, 37, 47, 55,
       30, 40, 51, 45, 33, 48,
       44, 49, 39, 56, 34, 53,
       46, 42, 50, 36, 29, 32]

IP = [58, 50, 42, 34, 26, 18, 10, 2,
      60, 52, 44, 36, 28, 20, 12, 4,
      62, 54, 46, 38, 30, 22, 14, 6,
      64, 56, 48, 40, 32, 24, 16, 8,
      57, 49, 41, 33, 25, 17, 9, 1,
      59, 51, 43, 35, 27, 19, 11, 3,
      61, 53, 45, 37, 29, 21, 13, 5,
      63, 55, 47, 39, 31, 23, 15, 7
      ]

E = [32, 1, 2, 3, 4, 5,
     4, 5, 6, 7, 8, 9,
     8, 9, 10, 11, 12, 13,
     12, 13, 14, 15, 16, 17,
     16, 17, 18, 19, 20, 21,
     20, 21, 22, 23, 24, 25,
     24, 25, 26, 27, 28, 29,
     28, 29, 30, 31, 32, 1]


def f(v32, k48):
    e48 = permute(v32, E)
    ke48 = e48 ^ k48

    pass


def encrypt(M, K):
    subkeys = generateroundkeys(K)

    MIP = permute(M, IP)

    L, R = getlr32(MIP)

    for SK in subkeys:
        Lprev = L
        Rprev = R
        L = Rprev
        R = Lprev ^ f(Rprev, SK)

    return 0


def generateroundkeys(K):
    keys = []
    CD = 0
    shifts = [1, 1, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 1]

    Kplus = permute(K, PC1)

    C, D = getlr28(Kplus)

    for i in range(16):
        for j in range(shifts[i]):
            C = ((C << 1) + getbit(C, 1, wordsize=28)) & 0xfffffff
            D = ((D << 1) + getbit(D, 1, wordsize=28)) & 0xfffffff
        CD = C * 2 ** 28 + D
        keys.append(permute(CD, PC2))
    return keys


def permute(V, permutation):
    P = 0
    for i in permutation:
        P <<= 1
        P += getbit(V, 1)
    return V


def splithalves(bits, halfsize):
    L = bits >> halfsize
    R = bits & ((1 << halfsize) - 1)
    return L, R


def getlr32(bits):
    L = bits >> 32
    R = bits & 0xffffffff
    return L, R


def getlr28(bits):
    L = bits >> 28
    R = bits & 0xfffffff
    return L, R


def getbit(value, bit, wordsize=64):
    return value >> (wordsize - bit) & 1


def bin32(value):
    s = ""
    # vfor i in range(8):
    #    s +=  bin((value >> (8-i)) & 0xf)
    return bin(value)


main()
