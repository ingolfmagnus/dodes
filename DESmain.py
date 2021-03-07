import sys


def blocktest():
    M = [0x0123456789ABCDEF, 0x0123456789ABCDEF]
    K = 0x133457799BBCDFF1
    V = 0x7A65B3757269A47E

    print("encrypting   ", ' '.join(map(hex,M)), "...")
    C = encrypt(M, K, IV=V)
    print("encrypted to:", ' '.join(map(hex,C)))
    print("decrypting   ", ' '.join(map(hex,C)), "...")
    D = decrypt(C, K, IV=V)
    print("decrypted to:", ' '.join(map(hex,D)))
    return


def main(inputfile, outputfile, reverse=False):
    # The CDC mode Initial Vector (IV) given in the assignment
    DEFAULT_IV=0x7A65B3757269A47E

    # Read entire file into bytes object
    infile = open(inputfile, "rb")
    inbytes = infile.read()
    infile.close()

    # Pad data to 64 bits (8 bytes) and put into 64-bit blocks (integers)
    bytesblock = padto8bytes(inbytes)
    inblocks = []
    for blocknum in range(len(bytesblock) // 8):
        block = 0
        for bytenum in range(8):
            block <<= 8
            block += bytesblock[blocknum * 8 + bytenum]
        inblocks.append(block)

    # Read and pad the passphrase. Non-ASCII chars are more than 1 byte each.
    while (True):
        passphrase = input("Enter DES passphrase: ")
        passbytes = bytes(passphrase, "UTF-8")
        if (len(passbytes) >= 8):
            break
        else:
            print("Too short!")
    #keybytes = padto8bytes(bytes(passphrase, "UTF-8"))
    #keybytes = bytes(passphrase, "UTF-8")

    # Construct the key from passphrase bytes (the first 8 of them)
    key = 0
    for keybyte in range(8):
        key <<= 8
        key += passbytes[keybyte]

    # Encrypt or decrypt the padded data with the padded key
    if not reverse:
        outblocks = encrypt(inblocks, key, IV=DEFAULT_IV)
    else:
        outblocks = decrypt(inblocks, key, IV=DEFAULT_IV)

    outfile = open(outputfile, "wb")

    # Convert int64s to bytes and write to output file
    outbytes = bytearray()
    for block64 in outblocks:
        for b in range(8):
            byte = getbits(block64, b * 8 + 1, 8, wordsize=64)
            outbytes.append(byte)
    outfile.write(outbytes)
    outfile.close()
    return


def decrypt(MBlocks, K, IV=0):
    return encrypt(MBlocks, K, reverse=True, IV=IV)


def encrypt(MBlocks, K, reverse=False, IV=0):
    """
    Applies DES encryption to 64-bit blocks of data. Multiple blocks are encrypted in CBC mode, one single block in ECB mode.
    :param MBlocks: 64-bit data blocks, binary coded in integer array
    :param K: 64-bit key block (56 significant and 8 parity bits), binary coded in integer
    :param reverse: When true, applies subkeys in reverse, thus decrypting the data
    :param IV: 64-bit Initial Vector for CBC mode. Ignored if data is only one block.
    :return: the resulting data blocks, binary coded in integer array
    """

    # Ensure CBC is not employed on single-block data. XOR with 0 has no effect.
    if len(MBlocks) < 2:
        IV = 0

    subkeys = generateroundkeys(K)
    if reverse:
        subkeys.reverse()
    Cblocks = []
    XV = IV
    for M in MBlocks:
        # Do CBC encryption xor
        if (not reverse):
            M ^= XV
        # Initial permutation
        MIP = permute(M, IP, wordsize=64)
        L, R = splitbits(MIP, wordsize=64)
        for SK in subkeys:
            Lprev = L
            Rprev = R
            L = Rprev
            R = Lprev ^ f(Rprev, SK)
        RL = (R << 32) + L
        C = permute(RL, IPR, wordsize=64)
        if not reverse:
            XV = C # Use as vector in next block
        else:
            C ^= XV # Decryption xor
            XV = M  # Update vector for next block
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

    for i in KEYSHIFTS:
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

def padto8bytes(block64):
    """
    Return a 8byte padded bytes object
    :param block64: A bytes object to be padded
    :return: An 8-byte padded bytes object
    """
    localblock = bytearray(block64)
    try:
        numbytes = len(localblock)
        if (numbytes % 8 != 0):
            for i in range(8 - numbytes % 8):
                localblock.append(0)
    except:
        e = sys.exc_info()[0]
    return bytes(localblock)

KEYSHIFTS = [1, 1, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 1]

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

if __name__ == '__main__':
    print (__name__, sys.argv)
    if len(sys.argv) != 4:
        print("Usage: DESmain -encrypt|-decrypt source destination")
        exit(0)
    if sys.argv[1].lower() == "-encrypt":
        main(sys.argv[2], sys.argv[3], False)
    elif sys.argv[1].lower() == "-decrypt":
        main(sys.argv[2], sys.argv[3], True)
    else:
        print("Usage: DESmain -encrypt|-decrypt source destination")
