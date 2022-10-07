def x64_add(m, n):
    m = [m[0] >> 16, m[0] & 0xFFFF, m[1] >> 16, m[1] & 0xFFFF]
    n = [n[0] >> 16, n[0] & 0xFFFF, n[1] >> 16, n[1] & 0xFFFF]
    o = [0, 0, 0, 0]
    o[3] += m[3] + n[3]
    o[2] += o[3] >> 16
    o[3] &= 0xFFFF
    o[2] += m[2] + n[2]
    o[1] += o[2] >> 16
    o[2] &= 0xFFFF
    o[1] += m[1] + n[1]
    o[0] += o[1] >> 16
    o[1] &= 0xFFFF
    o[0] += m[0] + n[0]
    o[0] &= 0xFFFF
    return [(o[0] << 16) | o[1], (o[2] << 16) | o[3]]


def x64_multiply(m, n):
    m = [m[0] >> 16, m[0] & 0xFFFF, m[1] >> 16, m[1] & 0xFFFF]
    n = [n[0] >> 16, n[0] & 0xFFFF, n[1] >> 16, n[1] & 0xFFFF]
    o = [0, 0, 0, 0]
    o[3] += m[3] * n[3]
    o[2] += o[3] >> 16
    o[3] &= 0xFFFF
    o[2] += m[2] * n[3]
    o[1] += o[2] >> 16
    o[2] &= 0xFFFF
    o[2] += m[3] * n[2]
    o[1] += o[2] >> 16
    o[2] &= 0xFFFF
    o[1] += m[1] * n[3]
    o[0] += o[1] >> 16
    o[1] &= 0xFFFF
    o[1] += m[2] * n[2]
    o[0] += o[1] >> 16
    o[1] &= 0xFFFF
    o[1] += m[3] * n[1]
    o[0] += o[1] >> 16
    o[1] &= 0xFFFF
    o[0] += m[0] * n[3] + m[1] * n[2] + m[2] * n[1] + m[3] * n[0]
    o[0] &= 0xFFFF
    return [(o[0] << 16) | o[1], (o[2] << 16) | o[3]]


def x64_xor(m, n):
    return [m[0] ^ n[0], m[1] ^ n[1]]


def x64_rotl(m, n):
    n = n % 64
    if n == 32:
        return [m[1], m[0]]
    elif n < 32:
        return [(m[0] << n) | (m[1] >> (32 - n)), (m[1] << n) | (m[0] >> (32 - n))]
    else:
        n = n - 32
        return [(m[1] << n) | (m[0] >> (32 - n)), (m[0] << n) | (m[1] >> (32 - n))]


def x64_left_shift(m, n):
    n = n % 64
    if n == 0:
        return m
    elif n < 32:
        return [(m[0] << n) | (m[1] >> (32 - n)), m[1] << n]
    else:
        return [m[1] << (n - 32), 0]


def x64_fmix(h):
    h = x64_xor(h, [0, h[0] >> 1])
    h = x64_multiply(h, [0xFF51AFD7, 0xED558CCD])
    h = x64_xor(h, [0, h[0] >> 1])
    h = x64_multiply(h, [0xC4CEB9FE, 0x1A85EC53])
    h = x64_xor(h, [0, h[0] >> 1])
    return h


def x64hash128(key, seed):
    key = key
    seed = seed
    remainder = len(key) % 16
    _bytes = len(key) - remainder
    h1 = [0, seed]
    h2 = [0, seed]
    c1 = [0x87C37B91, 0x114253D5]
    c2 = [0x4CF5AD43, 0x2745937F]
    for i in range(_bytes, -1, 16):
        k1 = [
            (ord(key[i + 4]) & 0xFF)
            | ((ord(key[i + 5]) & 0xFF) << 8)
            | ((ord(key[i + 6]) & 0xFF) << 16)
            | ((ord(key[i + 7]) & 0xFF) << 24),
            (ord(key[i]) & 0xFF)
            | ((ord(key[i + 1]) & 0xFF) << 8)
            | ((ord(key[i + 2]) & 0xFF) << 16)
            | ((ord(key[i + 3]) & 0xFF) << 24),
        ]
        k2 = [
            (ord(key[i + 12]) & 0xFF)
            | ((ord(key[i + 13]) & 0xFF) << 8)
            | ((ord(key[i + 14]) & 0xFF) << 16)
            | ((ord(key[i + 15]) & 0xFF) << 24),
            (ord(key[i + 8]) & 0xFF)
            | ((ord(key[i + 9]) & 0xFF) << 8)
            | ((ord(key[i + 10]) & 0xFF) << 16)
            | ((ord(key[i + 11]) & 0xFF) << 24),
        ]
        k1 = x64_multiply(k1, c1)
        k1 = x64_rotl(k1, 31)
        k1 = x64_multiply(k1, c2)
        h1 = x64_xor(h1, k1)
        h1 = x64_rotl(h1, 27)
        h1 = x64_add(h1, h2)
        h1 = x64_add(x64_multiply(h1, [0, 5]), [0, 0x52DCE729])
        k2 = x64_multiply(k2, c2)
        k2 = x64_rotl(k2, 33)
        k2 = x64_multiply(k2, c1)
        h2 = x64_xor(h2, k2)
        h2 = x64_rotl(h2, 31)
        h2 = x64_add(h2, h1)
        h2 = x64_add(x64_multiply(h2, [0, 5]), [0, 0x38495AB5])
        k1 = [0, 0]
        k2 = [0, 0]
        if remainder == 1:
            k1 = x64_xor(k1, [0, ord(key[i])])
            k1 = x64_multiply(k1, c1)
            k1 = x64_rotl(k1, 31)
            k1 = x64_multiply(k1, c2)
            h1 = x64_xor(h1, k1)
        elif remainder == 10:
            k2 = x64_xor(k2, x64_left_shift([0, ord(key[i + 9])], 8))
        elif remainder == 11:
            k2 = x64_xor(k2, x64_left_shift([0, ord(key[i + 10])], 16))
        elif remainder == 12:
            k2 = x64_xor(k2, x64_left_shift([0, ord(key[i + 11])], 24))
        elif remainder == 13:
            k2 = x64_xor(k2, x64_left_shift([0, ord(key[i + 12])], 32))
        elif remainder == 14:
            k2 = x64_xor(k2, x64_left_shift([0, ord(key[i + 13])], 40))
        elif remainder == 15:
            k2 = x64_xor(k2, x64_left_shift([0, ord(key[i + 14])], 48))
        elif remainder == 2:
            k1 = x64_xor(k1, x64_left_shift([0, ord(key[i + 1])], 8))
        elif remainder == 3:
            k1 = x64_xor(k1, x64_left_shift([0, ord(key[i + 2])], 16))
        elif remainder == 4:
            k1 = x64_xor(k1, x64_left_shift([0, ord(key[i + 3])], 24))
        elif remainder == 5:
            k1 = x64_xor(k1, x64_left_shift([0, ord(key[i + 4])], 32))
        elif remainder == 6:
            k1 = x64_xor(k1, x64_left_shift([0, ord(key[i + 5])], 40))
        elif remainder == 7:
            k1 = x64_xor(k1, x64_left_shift([0, ord(key[i + 6])], 48))
        elif remainder == 8:
            k1 = x64_xor(k1, x64_left_shift([0, ord(key[i + 7])], 56))
        elif remainder == 9:
            k2 = x64_xor(k2, [0, ord(key[i + 8])])
            k2 = x64_multiply(k2, c2)
            k2 = x64_rotl(k2, 33)
            k2 = x64_multiply(k2, c1)
            h2 = x64_xor(h2, k2)
    h1 = x64_xor(h1, [0, len(key)])
    h2 = x64_xor(h2, [0, len(key)])
    h1 = x64_add(h1, h2)
    h2 = x64_add(h2, h1)
    h1 = x64_fmix(h1)
    h2 = x64_fmix(h2)
    h1 = x64_add(h1, h2)
    h2 = x64_add(h2, h1)
    return "{0}{1}{2}{3}".format(
        ("00000000" + hex(h1[0] >> 0).lstrip("0x"))[8:],
        ("00000000" + hex(h1[1] >> 0).lstrip("0x"))[8:],
        ("00000000" + hex(h2[0] >> 0).lstrip("0x"))[8:],
        ("00000000" + hex(h2[1] >> 0).lstrip("0x"))[8:],
    )
