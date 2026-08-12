#Viktoriia Volkova
import numpy as np

def gdim(n, d):
    r = 1
    for i in range(d):
        r = r * (n + d - i) // (i + 1)
    return r

def fdeg(n, k):
    d = 0
    while gdim(n, d) < k:
        d += 1
    return d

def monoms(n, md):
    res = []
    for d in range(md + 1):
        def gen(rem, idx, cur, res=res, n=n):
            if idx == n - 1:
                cur.append(rem)
                res.append(tuple(cur))
                cur.pop()
                return
            for k in range(rem, -1, -1):
                cur.append(k)
                gen(rem - k, idx + 1, cur)
                cur.pop()
        gen(d, 0, [])
    return res

def evp(cs, ms, x):
    r = 0.
    for c, m in zip(cs, ms):
        if c == 0.:
            continue
        t = c
        for j, e in enumerate(m):
            t *= x[j] ** e
        r += t
    return r

def grp(cs, ms, x, n):
    g = np.zeros(n)
    for c, m in zip(cs, ms):
        if c == 0.:
            continue
        for j in range(n):
            if m[j] == 0:
                continue
            dt = c * m[j]
            for k in range(n):
                if k == j:
                    pw = m[k] - 1
                    if pw > 0:
                        dt *= x[k] ** pw
                    elif pw < 0:
                        dt = 0.
                        break
                else:
                    if m[k] > 0:
                        dt *= x[k] ** m[k]
            g[j] += dt
    return g

def pmul(a, b, N):
    c = np.zeros(N + 1)
    for i in range(N + 1):
        for j in range(N + 1 - i):
            c[i + j] += a[i] * b[j]
    return c

def pinv(m, N):
    c = np.zeros(N + 1)
    c[0] = 1. / m[0]
    for k in range(1, N + 1):
        c[k] = -sum(m[j] * c[k - j] for j in range(1, k + 1)) / m[0]
    return c

def evs(cs, ms, Js, N):
    r = np.zeros(N + 1)
    for c, m in zip(cs, ms):
        if c == 0.:
            continue
        t = np.zeros(N + 1)
        t[0] = 1.
        for j, e in enumerate(m):
            for _ in range(e):
                t = pmul(t, Js[j], N)
        r += c * t
    return r

def main():
    lines = []
    try:
        while True:
            lines.append(raw_input())
    except EOFError:
        pass
    lines = [l for l in lines if l.strip()]
    N = int(lines[0].strip())
    p = np.array([float(x) for x in lines[1].split()])
    n = len(p)
    polys = []
    for i in range(2, len(lines)):
        row = [float(x) for x in lines[i].split()]
        if row:
            polys.append(row)

    fs = []
    for i in range(n):
        Lc = polys[2 * i]
        Mc = polys[2 * i + 1]
        dL = fdeg(n, len(Lc))
        dM = fdeg(n, len(Mc))
        mL = monoms(n, dL)[:len(Lc)]
        mM = monoms(n, dM)[:len(Mc)]
        fs.append((np.array(Lc), mL, np.array(Mc), mM))

    Df = np.zeros((n, n))
    for i, (Lc, mL, Mc, mM) in enumerate(fs):
        Li = evp(Lc, mL, p)
        Mi = evp(Mc, mM, p)
        gL = grp(Lc, mL, p, n)
        gM = grp(Mc, mM, p, n)
        Df[i, :] = (gL * Mi - Li * gM) / (Mi * Mi)

    vals, vecs = np.linalg.eig(Df)
    vals = vals.real
    vecs = vecs.real
    idx = np.argmin(np.abs(vals))
    lam = vals[idx]
    u = vecs[:, idx]
    u = u / np.linalg.norm(u)
    for c in u:
        if abs(c) > 1e-12:
            if c < 0:
                u = -u
            break

    Js = [np.zeros(N + 1) for _ in range(n)]
    for i in range(n):
        Js[i][0] = p[i]
        Js[i][1] = u[i]

    for k in range(2, N + 1):
        Jt = [Js[i].copy() for i in range(n)]
        for i in range(n):
            for j in range(k, N + 1):
                Jt[i][j] = 0.
        Delta = np.zeros(n)
        for i, (Lc, mL, Mc, mM) in enumerate(fs):
            Ls = evs(Lc, mL, Jt, k)
            Ms = evs(Mc, mM, Jt, k)
            fi = pmul(Ls, pinv(Ms, k), k)
            Delta[i] = fi[k]
        lk = lam ** k
        Jk = np.linalg.solve(Df - lk * np.eye(n), -Delta)
        for i in range(n):
            Js[i][k] = Jk[i]

    for i in range(n):
        print ' '.join('%.17e' % Js[i][k] for k in range(N + 1))

main()



# TEST:
# f(x,y) = (1 - x^2 + y, -0.5x) , p=(-2, 1)
# INPUT:
#   8
#   -2.0 1.0
#   1.0 0.0 1.0 -1.0 0.0 0.0
#   1.0
#   0.0 -0.5 0.0
#   1.0
# lambda = 0.129171, u = [0.250130, -0.968212]
# OUTPUT:
#   -2.00000000000000000e+00 2.50130455372283012e-01 -2.40790081057862997e-03 5.28338953332533279e-06 -4.71041783086010985e-09 2.00001401961776272e-12 -4.79385815999818434e-16 7.15766958609483900e-20 -7.07869721657971240e-24
#   1.00000000000000000e+00 -9.68212143744982323e-01 7.21566715767614358e-02 -1.22570082357743512e-03 8.45989993330313844e-06 -2.78081937780031719e-08 5.16010891630289397e-11 -5.96457195799737034e-14 4.56662047444892135e-17
#
# TEST:
# f(x,y) = ((x+y+x^2-5xy-2y^2)/(1+x-4y), (1+2x-y+x^2-4xy+8y^2)/(1-2x+8y))
# INPUT:
#   8
#   0.0 0.5
#   0.0 1.0 1.0 1.0 -5.0 -2.0
#   1.0 1.0 -4.0
#   1.0 2.0 -1.0 1.0 -4.0 8.0
#   1.0 -2.0 8.0
# lambda = 0.415571, u = [0.677910, -0.735145]
# OUTPUT:
#   0.00000000000000000e+00 6.77909863126612833e-01 3.47750984114282247e+00 3.04973874188263565e+01 3.35070577102927814e+02 4.15434724966700651e+03 5.54676226803937316e+04 7.78181743372802855e+05 1.13091536117502581e+07
#   5.00000000000000000e-01 -7.35145031592853160e-01 -3.76460550014192741e+00 -3.17649516078457950e+01 -3.39135075825192303e+02 -4.12961402666120830e+03 -5.45319890830002623e+04 -7.59806183515596204e+05 -1.09929359684497677e+07
#
# TEST: 
# p=(0,0,0), n=3, pelna funkcja wymierna stopnia 3
# INPUT:
#   8
#   0 0 0
#   0 1 2 -1 2 2 -2 -1 1 1 1 -1 -3 2 -1 1 -1 4 6 1
#   1 1 2 1 2 2 3 3 2 4
#   0 1 1 2 1 3 2 -2 -4 1
#   1 1 2 -1 2 2 -2 -1 1 3
#   0 1 2 3 2 2 3 3 2 4
#   1 1 1 2 1 3 -4 -2 -4 -1
# lambda = -0.681331, u = [0.787904, -0.605027, 0.114673]
# OUTPUT:
#   0.00000000000000000e+00 7.87903884904654794e-01 3.68073038852827539e+00 5.13175753380626745e+01 4.88349718239827439e+02 7.47490200976352935e+03 9.49427768632920488e+04 1.51271806867063697e+06 2.21266722549171448e+07
#   0.00000000000000000e+00 -6.05026884077769056e-01 -1.28233614203003055e+00 -3.58531518267618665e+01 -2.36215469802692581e+02 -4.84660259809042145e+03 -5.16471629160246885e+04 -9.37999849678651313e+05 -1.26274824300909229e+07
#   0.00000000000000000e+00 1.14673177750067204e-01 -1.07245149129567174e+00 3.54611819111069781e+00 -8.08275988309783173e+01 9.07352768740644819e+01 -9.84559473136976158e+03 -3.03865798752493793e+04 -1.66473396332354541e+06
#
# TEST: 
# f(x,y) = (0.3x, 0.7y)
# INPUT:
#   4
#   0.0 0.0
#   0.0 0.3 0.0
#   1.0
#   0.0 0.0 0.7
#   1.0
# lambda = 0.300000, u = [1.000000, 0.000000]
# OUTPUT:
#   0.00000000000000000e+00 1.00000000000000000e+00 -0.00000000000000000e+00 -0.00000000000000000e+00 -0.00000000000000000e+00
#   0.00000000000000000e+00 0.00000000000000000e+00 0.00000000000000000e+00 0.00000000000000000e+00 0.00000000000000000e+00
#
# TEST: p=(3, 1), N=6
# INPUT:
#   6
#   3.0 1.0
#   1.0 0.0 1.0 -1.0 0.0 0.0
#   1.0
#   0.0 -0.5 0.0
#   1.0
# lambda = -0.084524, u = [0.166683, 0.986011]
# OUTPUT:
#   3.00000000000000000e+00 1.66683206895831548e-01 -3.65603992780762427e-04 -1.48272944710979844e-07 -8.59386479974389333e-12 9.10807277465976824e-16 -2.08380321984339051e-20
#   1.00000000000000000e+00 9.86010501231564751e-01 2.55870555141346524e-02 -1.22769640072438170e-04 8.41854960691668924e-08 1.05558920166225258e-10 2.85722762292175072e-14
