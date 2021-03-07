# The SBox
S = [14, 4, 13, 1, 2, 15, 11, 8, 3, 10, 6, 12, 5, 9, 0, 7]
# The output 8-bit permutation
PERM     = [7, 5, 3, 1, 0, 2, 4, 6]
PERM_REV = [4, 3, 5, 2, 6, 1, 7, 0]

KNOWNS = [[[0b00000000, 0b10010000], [0b10111011, 0b10010101]],
          [[0b00000001, 0b11010010], [0b10111010, 0b00010111]],
          [[0b00011111, 0b11011100], [0b10100111, 0b00011001]]
          ]


def SBox(x):
    return S[x]


def permute(V, permutation, wordsize):
    P = 0
    for i in permutation:
        P <<= 1
        P += getbit(V, i, wordsize)
    return P


# Assumes rightmost bit is bit 0
def permuteReverse(V, permutation, wordsize):
    R = 0
    for i in range(wordsize):
        R += getbit(V, wordsize - i - 1, wordsize) << PERM[i]
    return R


def splitbits(bits, wordsize):
    halfsize = wordsize // 2
    L = bits >> (halfsize)
    R = bits & ((1 << halfsize) - 1)
    return L, R


def getbit(value, bit, wordsize=64):
    return getbits0onleft(value, bit, 1, wordsize)


# If bits are numbered with bit 0 as the rightmost
def getbits0onright(value, startbit, numbits, wordsize):
    return value >> (startbit - numbits + 1) & ((1 << numbits) - 1)


# If bits are numbered with bit 1 as the leftmost
def getbits1onleft(value, startbit, numbits, wordsize):
    return value >> (wordsize - startbit - numbits + 1) & ((1 << numbits) - 1)

# If bits are numbered with bit 0 as the leftmost
def getbits0onleft(value, startbit, numbits, wordsize):
    return value >> (wordsize - startbit - numbits) & ((1 << numbits) - 1)

def checkK1(x,y,k1):
    xl, xr = splitbits(x, 8)
    y0 = permute(y, PERM_REV,wordsize=8)
    y0test = SBox(xl ^ k1)
    return y0test == y0

def checkkey(x,y,k):
    k1, k2 = splitbits(k, 8)
    xl, xr = splitbits(x, 8)
    yl = SBox(xl ^ k1)
    yr = SBox(xr ^ k2)
    y0 = (yl << 4) + yr
    y1 = permute(y, PERM,wordsize=8)
    return y1 == y



XRANGE = 16
YRANGE = 16

DDT = [[] for i in range(XRANGE)]
SOLUTIONS_LEFT  = [set(), set(), set()]
SOLUTIONS_RIGHT = [set(), set(), set()]

def main():
    global SOLUTIONS_RIGHT, SOLUTIONS_LEFT
    buildDDT()
    for c in range(len(KNOWNS)):
        case = KNOWNS[c]
        x1l, x1r = splitbits(case[0][0], wordsize=8)
        x2l, x2r = splitbits(case[1][0], wordsize=8)
        y1 = permute(case[0][1], PERM_REV, wordsize=8)
        y1l, y1r = splitbits(y1, wordsize=8)
        y2 = permute(case[1][1], PERM_REV, wordsize=8)
        y2l, y2r = splitbits(y2, wordsize=8)
        xdl = x1l ^ x2l
        xdr = x1r ^ x2r
        ydl = y1l ^ y2l
        ydr = y1r ^ y2r

        xinputset_left  = DDT[xdl][ydl]
        xinputset_right = DDT[xdr][ydr]

        for x in xinputset_left:
            SOLUTIONS_LEFT[c].add(x1l ^ x)
        for x in xinputset_right:
            SOLUTIONS_RIGHT[c].add(x1r ^ x)

    K1_xset = set()
    K1_xset.update(SOLUTIONS_LEFT[0])
    K1_xset.intersection_update(SOLUTIONS_LEFT[1])
    K1_xset.intersection_update(SOLUTIONS_LEFT[2])
    if len(K1_xset) == 1:
        print("K1 found:", K1_xset)
    else:
        print("K1 Candidates:", K1_xset)


    K2_xset = set()
    K2_xset.update(SOLUTIONS_RIGHT[0])
    K2_xset.intersection_update(SOLUTIONS_RIGHT[1])
    K2_xset.intersection_update(SOLUTIONS_RIGHT[2])
    if len(K2_xset) == 1:
        print("K2 found:", K2_xset)
    else:
        print("K2 Candidates:", K2_xset)

    for k1 in K1_xset:
        for k2 in K2_xset:
            key = (k1 << 4) + k2
            if checkkey(KNOWNS[0][0][0], KNOWNS[0][0][1], key):
                print("K1 found:", key)

    return

def printDDT():
    for x in range(XRANGE):
        for y in range(YRANGE):
            print(len(DDT[x][y]), end=" ")
        print()


def buildDDT():
    for xdiff in range(XRANGE):
        for j in range(YRANGE):
            DDT[xdiff].append([])
        for x in range(XRANGE):
            y = SBox(x)
            y2 = SBox(x ^ xdiff)
            ydiff = y ^ y2
            DDT[xdiff][ydiff].append(x)


if __name__ == '__main__':
    main()
