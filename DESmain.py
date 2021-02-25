def main():
    C = encrypt(0x0123456789ABCDEF, 0x133457799BBCDFF1)
    print(C)
    return


def encrypt(M, K):
    L, R = getlr(M)
    Kp = getkplus(K)

    return 0


def getlr(M):
    L = M >> 32
    R = M & 0xffffffff
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
        print (i)
        Kplus <<= 1
        Kplus += getbit(K,i)
    return Kplus


def getbit(value, bit):
    return value >> (64 - bit) & 1


def bin32(value):
    s = ""
    # vfor i in range(8):
    #    s +=  bin((value >> (8-i)) & 0xf)
    return bin(value)

main()