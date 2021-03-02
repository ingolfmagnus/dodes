def blocktest():
    print("encrypting ", hex(0x0123456789ABCDEF), " ...")
    C = encrypt([0x0123456789ABCDEF], 0x133457799BBCDFF1)
    print("encrypted to: ", hex(C[0]))
    print("decrypting ", hex(C[0]), " ...")
    D = decrypt(C, 0x133457799BBCDFF1)
    print("decrypted to: ", hex(D[0]))
    return


def main(inputfile, outputfile):
    infile = open(inputfile, "rb")
    intext = infile.read()
    infile.close()

    while (True):
        passphrase = input("Enter DES passphrase: ")
        if (len(bytes(passphrase)) >= 7):
            break
        print("Too short!")

    bytesblock = pad8(intext)
    inblocks = []
    for blocknum in range(len(intext) // 8):
        block = 0
        for bytenum in range(8):
            block <<= 8
            block += bytesblock[blocknum*8 + bytenum]
        inblocks.append(block)

    keybytes = pad8(passphrase)
    key = 0
    for keybyte in range(7):
        key <<= 8
        key += keybytes[keybyte]

    outblocks = encrypt(inblocks, key)

    outfile = open(outputfile, "wb")


def pad8(text):
    bytesarr = bytearray(text, "UTF-8")
    numbytes = len(bytesarr)
    if (numbytes % 8 != 0):
        for i in range(8 - numbytes % 8):
            bytesarr.append(0)
    return bytesarr


def decrypt(MBlocks, K):
    return encrypt(MBlocks, K, reverse=True)


def encrypt(MBlocks, K, reverse=False):
    """
    Applies DES encryption to 64-bit block of data
    :param M: 64-bit data blocks, binary coded in integer array
    :param K: 56-bit key block, binary coded in integer
    :param reverse: When true, applies subkeys in reverse, thus decrypting the data
    :return: the resulting data blocks, binary coded in integer array
    """
    subkeys = generateroundkeys(K)
    if (reverse):
        subkeys.reverse()
    Cblocks = []
    for M in MBlocks:
        MIP = permute(M, IP, wordsize=64)

        L, R = splitbits(MIP, wordsize=64)
        for SK in subkeys:
            Lprev = L
            Rprev = R
            L = Rprev
            R = Lprev ^ f(Rprev, SK)
        RL = (R << 32) + L
        C = permute(RL, IPR, wordsize=64)
        Cblocks.append(C)

    return Cblocks


def f(v32, k48):
    v48 = permute(v32, E, wordsize=32)
    kxv48 = v48 ^ k48
    result32 = 0
    for b in range(8):
        block6 = getbits(kxv48, b * 6 + 1, 6, wordsize=48)
        srow = (getbit(block6, 1, wordsize=6) << 1) + getbit(block6, 6, wordsize=6)
        scol = getbits(block6, 2, 4, wordsize=6)
        block4 = S[b][srow][scol]
        result32 = (result32 << 4) + block4
    result32 = permute(result32, P, wordsize=32)
    return result32


def generateroundkeys(K):
    keys = []
    CD = 0

    Kplus = permute(K, PC1, wordsize=64)

    C, D = splitbits(Kplus, wordsize=56)

    for i in KeyShifts:
        for j in range(i):
            C = ((C << 1) + getbit(C, 1, wordsize=28)) & 0xfffffff
            D = ((D << 1) + getbit(D, 1, wordsize=28)) & 0xfffffff
        CD = (C << 28) + D
        keys.append(permute(CD, PC2, wordsize=56))
    return keys


def permute(V, permutation, wordsize):
    P = 0
    for i in permutation:
        P <<= 1
        P += getbit(V, i, wordsize)
    return P


def splitbits(bits, wordsize):
    halfsize = wordsize // 2
    L = bits >> (halfsize)
    R = bits & ((1 << halfsize) - 1)
    return L, R


def getbit(value, bit, wordsize=64):
    return getbits(value, bit, 1, wordsize)


def getbits(value, startbit, numbits, wordsize):
    return value >> (wordsize - startbit - numbits + 1) & ((1 << numbits) - 1)


KeyShifts = [1, 1, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 1]

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

S = [
    # S1
    [
        [14, 4, 13, 1, 2, 15, 11, 8, 3, 10, 6, 12, 5, 9, 0, 7],
        [0, 15, 7, 4, 14, 2, 13, 1, 10, 6, 12, 11, 9, 5, 3, 8],
        [4, 1, 14, 8, 13, 6, 2, 11, 15, 12, 9, 7, 3, 10, 5, 0],
        [15, 12, 8, 2, 4, 9, 1, 7, 5, 11, 3, 14, 10, 0, 6, 13]
    ],

    # S2
    [
        [15, 1, 8, 14, 6, 11, 3, 4, 9, 7, 2, 13, 12, 0, 5, 10],
        [3, 13, 4, 7, 15, 2, 8, 14, 12, 0, 1, 10, 6, 9, 11, 5],
        [0, 14, 7, 11, 10, 4, 13, 1, 5, 8, 12, 6, 9, 3, 2, 15],
        [13, 8, 10, 1, 3, 15, 4, 2, 11, 6, 7, 12, 0, 5, 14, 9],
    ],

    # S3
    [
        [10, 0, 9, 14, 6, 3, 15, 5, 1, 13, 12, 7, 11, 4, 2, 8],
        [13, 7, 0, 9, 3, 4, 6, 10, 2, 8, 5, 14, 12, 11, 15, 1],
        [13, 6, 4, 9, 8, 15, 3, 0, 11, 1, 2, 12, 5, 10, 14, 7],
        [1, 10, 13, 0, 6, 9, 8, 7, 4, 15, 14, 3, 11, 5, 2, 12],
    ],

    # S4
    [
        [7, 13, 14, 3, 0, 6, 9, 10, 1, 2, 8, 5, 11, 12, 4, 15],
        [13, 8, 11, 5, 6, 15, 0, 3, 4, 7, 2, 12, 1, 10, 14, 9],
        [10, 6, 9, 0, 12, 11, 7, 13, 15, 1, 3, 14, 5, 2, 8, 4],
        [3, 15, 0, 6, 10, 1, 13, 8, 9, 4, 5, 11, 12, 7, 2, 14],
    ],

    # S5
    [
        [2, 12, 4, 1, 7, 10, 11, 6, 8, 5, 3, 15, 13, 0, 14, 9],
        [14, 11, 2, 12, 4, 7, 13, 1, 5, 0, 15, 10, 3, 9, 8, 6],
        [4, 2, 1, 11, 10, 13, 7, 8, 15, 9, 12, 5, 6, 3, 0, 14],
        [11, 8, 12, 7, 1, 14, 2, 13, 6, 15, 0, 9, 10, 4, 5, 3],
    ],

    # S6
    [
        [12, 1, 10, 15, 9, 2, 6, 8, 0, 13, 3, 4, 14, 7, 5, 11],
        [10, 15, 4, 2, 7, 12, 9, 5, 6, 1, 13, 14, 0, 11, 3, 8],
        [9, 14, 15, 5, 2, 8, 12, 3, 7, 0, 4, 10, 1, 13, 11, 6],
        [4, 3, 2, 12, 9, 5, 15, 10, 11, 14, 1, 7, 6, 0, 8, 13],
    ],

    # S7
    [
        [4, 11, 2, 14, 15, 0, 8, 13, 3, 12, 9, 7, 5, 10, 6, 1],
        [13, 0, 11, 7, 4, 9, 1, 10, 14, 3, 5, 12, 2, 15, 8, 6],
        [1, 4, 11, 13, 12, 3, 7, 14, 10, 15, 6, 8, 0, 5, 9, 2],
        [6, 11, 13, 8, 1, 4, 10, 7, 9, 5, 0, 15, 14, 2, 3, 12],
    ],

    # S8
    [
        [13, 2, 8, 4, 6, 15, 11, 1, 10, 9, 3, 14, 5, 0, 12, 7],
        [1, 15, 13, 8, 10, 3, 7, 4, 12, 5, 6, 11, 0, 14, 9, 2],
        [7, 11, 4, 1, 9, 12, 14, 2, 0, 6, 10, 13, 15, 3, 5, 8],
        [2, 1, 14, 7, 4, 10, 8, 13, 15, 12, 9, 0, 3, 5, 6, 11],
    ]
]

P = [16, 7, 20, 21,
     29, 12, 28, 17,
     1, 15, 23, 26,
     5, 18, 31, 10,
     2, 8, 24, 14,
     32, 27, 3, 9,
     19, 13, 30, 6,
     22, 11, 4, 25]

IPR = [40, 8, 48, 16, 56, 24, 64, 32,
       39, 7, 47, 15, 55, 23, 63, 31,
       38, 6, 46, 14, 54, 22, 62, 30,
       37, 5, 45, 13, 53, 21, 61, 29,
       36, 4, 44, 12, 52, 20, 60, 28,
       35, 3, 43, 11, 51, 19, 59, 27,
       34, 2, 42, 10, 50, 18, 58, 26,
       33, 1, 41, 9, 49, 17, 57, 25
       ]
blocktest()
