"""DFT / FFT / NTT 的参考实现。

画面上出现的每一个数值都必须来自这里，并且与 np.fft 对齐后才能用。
直接运行本文件会跑一遍自检：

    python utils/fft.py

约定
----
正变换沿用 numpy 的符号约定：X[k] = Σ_j x[j] * exp(-2πi·jk/n)。
逆变换除不做单位化之外与正变换对偶，最后除以 n（几何上是乘 ω^{-1} 再缩 1/n）。
"""

import numpy as np

TAU = 2 * np.pi


# ---------------------------------------------------------------- 基础工具

def is_power_of_two(n: int) -> bool:
    return isinstance(n, (int, np.integer)) and n > 0 and (n & (n - 1)) == 0


def roots_of_unity(n: int, sign: float = -1.0) -> np.ndarray:
    """n 个单位根 ω_n^k（默认 ω = e^{-2πi/n}，与 numpy 正变换一致）。"""
    return np.exp(sign * TAU * 1j * np.arange(n) / n)


def dft_matrix(n: int, sign: float = -1.0) -> np.ndarray:
    """F[k, m] = ω^{km}，用于把 DFT 摆成矩阵乘法讲清楚。"""
    k = np.arange(n)[:, None]
    m = np.arange(n)[None, :]
    return np.exp(sign * TAU * 1j * k * m / n)


def naive_dft(x, inverse: bool = False) -> np.ndarray:
    """照定义 O(n²) 地算一遍，用来对比 FFT 与教学演示。"""
    x = np.asarray(x, dtype=complex)
    n = x.size
    sign = 1.0 if inverse else -1.0
    return dft_matrix(n, sign) @ x


def bit_reverse_indices(n: int) -> np.ndarray:
    """长度为 n 时的位反转置换：0, 4, 2, 6, 1, 5, 3, 7（n = 8）。"""
    if not is_power_of_two(n):
        raise ValueError(f"n 必须是 2 的幂，收到 n = {n}")
    bits = int(np.log2(n))
    idx = np.arange(n)
    # 第 (i, b) 元是 i 的第 b 位（低位在前），再按权重 2^{bits-1-b} 累加即为位反转
    bits_matrix = (idx[:, None] >> np.arange(bits)[None, :]) & 1
    weights = (1 << np.arange(bits - 1, -1, -1)) if bits else np.zeros(0, dtype=int)
    return (bits_matrix @ weights).astype(int)


# ------------------------------------------------------------------- FFT

def _fft_radix2(x: np.ndarray, sign: float) -> np.ndarray:
    """自底向上迭代的 Cooley–Tukey，n 必须是 2 的幂。"""
    n = x.size
    if not is_power_of_two(n):
        raise ValueError(f"radix-2 FFT 要求 n 是 2 的幂，收到 n = {n}")

    y = x[bit_reverse_indices(n)].astype(complex)

    length = 2
    while length <= n:
        half = length // 2
        # 本层的旋转因子 ω_length^j，j = 0 … half-1
        w_len = np.exp(sign * TAU * 1j * np.arange(half) / length)
        for start in range(0, n, length):
            # 必须 copy：赋值会改写到 y，而 even / odd 是它的视图
            even = y[start:start + half].copy()
            odd = y[start + half:start + length].copy() * w_len
            y[start:start + half] = even + odd
            y[start + half:start + length] = even - odd
        length *= 2

    return y


def fft(x) -> np.ndarray:
    """正变换，等价于 np.fft.fft。"""
    x = np.asarray(x, dtype=complex)
    if x.size == 0:
        return x.copy()
    return _fft_radix2(x, sign=-1.0)


def ifft(X) -> np.ndarray:
    """逆变换，等价于 np.fft.ifft（自己负责 /n）。"""
    X = np.asarray(X, dtype=complex)
    if X.size == 0:
        return X.copy()
    return _fft_radix2(X, sign=1.0) / X.size


def _zero_pad(x: np.ndarray, n: int) -> np.ndarray:
    out = np.zeros(n, dtype=complex)
    out[:min(x.size, n)] = x[:min(x.size, n)]
    return out


def fft_convolve(a, b) -> np.ndarray:
    """用 FFT 做线性卷积：零填充到不小于 len(a) + len(b) - 1 的 2 的幂。"""
    a = np.asarray(a, dtype=complex)
    b = np.asarray(b, dtype=complex)
    size = int(a.size + b.size - 1)
    n = 1 << int(np.ceil(np.log2(size)))
    out = ifft(fft(_zero_pad(a, n)) * fft(_zero_pad(b, n)))
    return out[:size]


# ------------------------------------------------------------------- NTT

def ntt_transform(a, modulus: int, root: int, inverse: bool = False):
    """在有限域上跑同一套蝴蝶，root 必须是一个阶为 n 的原根。"""
    values = np.asarray(a, dtype=object) % modulus
    n = values.size
    if not is_power_of_two(n):
        raise ValueError(f"NTT 要求 n 是 2 的幂，收到 n = {n}")

    powers = pow(int(root), (modulus - 1) // n, modulus)
    if inverse:
        powers = pow(powers, modulus - 2, modulus)

    values = [int(v) for v in values[bit_reverse_indices(n)]]

    length = 2
    while length <= n:
        half = length // 2
        w_step = pow(int(powers), n // length, modulus)
        w_len = [1]
        for _ in range(1, half):
            w_len.append(w_len[-1] * w_step % modulus)
        for start in range(0, n, length):
            even = values[start:start + half]
            odd = values[start + half:start + length]
            for j in range(half):
                u = even[j]
                v = odd[j] * w_len[j] % modulus
                values[start + j] = (u + v) % modulus
                values[start + j + half] = (u - v) % modulus
        length *= 2

    inv_n = pow(n, modulus - 2, modulus)
    if inverse:
        values = [v * inv_n % modulus for v in values]
    return np.array(values, dtype=object)


# ------------------------------------------------------------------- 自检

def self_test(verbose: bool = True) -> dict:
    """与 numpy 对照的自检，返回各项最大误差。"""
    rng = np.random.default_rng(0)
    report = {}

    for n in (1, 2, 4, 8, 16, 64, 1024):
        x = rng.normal(size=n) + 1j * rng.normal(size=n)

        ref_forward = np.fft.fft(x)
        err_forward = np.max(np.abs(fft(x) - ref_forward))

        ref_inverse = np.fft.ifft(x)
        err_inverse = np.max(np.abs(ifft(x) - ref_inverse))

        err_roundtrip = np.max(np.abs(ifft(fft(x)) - x))
        err_naive = np.max(np.abs(naive_dft(x) - ref_forward))

        report[f"forward_{n}"] = err_forward
        report[f"inverse_{n}"] = err_inverse
        report[f"roundtrip_{n}"] = err_roundtrip
        report[f"naive_vs_npfft_{n}"] = err_naive

    # 单位根性质：ω^{k+n/2} = −ω^k、(ω_n^k)² = ω_{n/2}^k
    n = 8
    w = roots_of_unity(n, sign=1.0)
    report["symmetry"] = np.max(np.abs(w[: n // 2] + w[n // 2:]))
    report["halving"] = np.max(np.abs((w**2)[: n // 2] - roots_of_unity(n // 2, sign=1.0)))

    # 卷积
    a = rng.integers(-9, 9, size=40).astype(float)
    b = rng.integers(-9, 9, size=55).astype(float)
    report["conv"] = np.max(np.abs(fft_convolve(a, b) - np.convolve(a, b)))

    # NTT：p = 998244353 的原根是 3，勉强撞出 n = 2^20 的根
    modulus = 998244353
    for n in (2, 4, 8, 16, 64):
        if (modulus - 1) % n != 0:
            continue
        x = rng.integers(0, modulus, size=n, dtype=np.int64)
        # 直接用 n 次单位复用：root = 3^((p-1)/n)
        root = pow(3, (modulus - 1) // n, modulus)
        back = ntt_transform(ntt_transform(x, modulus, root), modulus, root, inverse=True)
        report[f"ntt_{n}"] = int(np.max(np.abs(np.array([int(v) for v in back], dtype=object) - x)))

    tol = 1e-9
    worst = {k: float(v) for k, v in report.items() if float(v) > tol}
    if verbose:
        for key, value in report.items():
            print(f"{key:>20} : {float(value):.3e}")
        print("自检通过" if not worst else f"超出容差 {tol}: {worst}")
    if worst:
        raise AssertionError(f"fft.py 自检失败: {worst}")
    return report


if __name__ == "__main__":
    self_test()
