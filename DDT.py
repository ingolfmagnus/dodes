

S = [14,4,13,1,2,15,11,8,3,10,6,12,5,9,0,7]

def SBox(x):
    return S[x]

XRANGE = 16
YRANGE = 16

DDT = [[] for i in range(XRANGE)]

def main():
    buildDDT()
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