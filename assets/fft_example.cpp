// 2026-10-11  fft.cpp
// 2026-11-21  fft_example.cpp

#include <algorithm>
#include <bit>
#include <cassert>
#include <complex>
#include <concepts>
#include <cstddef>
#include <functional>
#include <iostream>
#include <numbers>
#include <ranges>
#include <span>
#include <vector>

constexpr bool use_iterate = false;

using namespace std;

template <typename Elem>
struct fft_float {
};

template <floating_point Flt>
struct fft_float<complex<Flt>> {
    using type = Flt;
};

template <floating_point Flt>
struct fft_float<Flt> {
    using type = Flt;
};

template <typename T>
using fft_float_t = fft_float<T>::type;

template <typename T>
using fft_complex_t = complex<fft_float_t<T>>;

template <typename Elem>
vector<fft_complex_t<Elem>> fft_r(span<const Elem> a, bool inverse_root = false)
{
    using Float = fft_float_t<Elem>;
    using Complex = fft_complex_t<Elem>;
    const size_t n = a.size();
    if (n == 1) {
        return vector<Complex>{a.front()};
    }
    assert(has_single_bit(n));
    const Complex omega = exp(
        (inverse_root ? -1 : +1)
        * 2 * numbers::pi_v<Float> * 1i / Complex(n)
    );
    const vector<Elem> a_even = a
        | views::stride(2)
        | ranges::to<vector>();
    const vector<Elem> a_odd = a
        | views::drop(1)
        | views::stride(2)
        | ranges::to<vector>();
    const vector<Complex> y_even = fft_r<Elem>(a_even, inverse_root);
    const vector<Complex> y_odd = fft_r<Elem>(a_odd, inverse_root);
    return vector{
        views::zip(y_even, y_odd)
        | views::enumerate
        | views::transform(
            [omega](auto p) -> Complex {
                const auto [i, v] = p;
                const auto [even, odd] = v;
                return even + pow(omega, i) * odd;
            }
        )
        | ranges::to<vector>(),
        views::zip(y_even, y_odd)
        | views::enumerate
        | views::transform(
            [omega](auto p) -> Complex {
                const auto [i, v] = p;
                const auto [even, odd] = v;
                return even - pow(omega, i) * odd;
            }
        )
        | ranges::to<vector>()
    }
    | views::join
    | ranges::to<vector>();
}

template <typename Elem>
vector<fft_complex_t<Elem>> fft_i(span<const Elem> a, bool inverse_root = false)
{
    using Float = fft_float_t<Elem>;
    using Complex = fft_complex_t<Elem>;
    const size_t n = a.size();
    assert(has_single_bit(n));
    const size_t lb = countr_zero(n);

    const auto rev = [lb](size_t i) -> size_t {
        size_t r = 0;
        for (size_t b = 0; b < lb; ++b) {
            r = (r << 1) | ((i >> b) & 1);
        }
        return r;
    };

    vector<Complex> res(n);
    for (size_t i = 0; i < n; ++i) {
        res[rev(i)] = a[i];
    }

    for (size_t s = 1; s <= lb; ++s) {
        const size_t m = size_t{1} << s;
        const Complex omega = exp(
            (inverse_root ? -1 : +1)
            * 2 * numbers::pi_v<Float> * 1i / Complex(m)
        );
        for (size_t k = 0; k < n; k += m) {
            for (size_t j = 0; j < m / 2; ++j) {
                const Complex t = pow(omega, static_cast<Float>(j)) * res[k + j + m / 2];
                const Complex u = res[k + j];
                res[k + j] = u + t;
                res[k + j + m / 2] = u - t;
            }
        }
    }

    return res;
}

template <typename Elem>
vector<fft_complex_t<Elem>> fft(span<const Elem> a, bool inverse_root = false)
{
    if constexpr (use_iterate) {
        return fft_i(a, inverse_root);
    } else {
        return fft_r(a, inverse_root);
    }
}

template <typename Elem>
vector<fft_complex_t<Elem>> fft_inverse(span<const Elem> dft)
{
    const size_t n = dft.size();
    assert(has_single_bit(n));
    return fft(dft, true)
        | views::transform(
            [n](Elem u) {
                return u / fft_complex_t<Elem>(n);
            }
        )
        | ranges::to<vector>();
}

template <typename Elem>
vector<fft_complex_t<Elem>> polynomial_multiply(span<const Elem> poly1, span<const Elem> poly2)
{
    using Float = fft_float_t<Elem>;
    using Complex = fft_complex_t<Elem>;
    const size_t n = poly1.size();
    assert(n == poly2.size());
    assert(has_single_bit(n));

    vector<Elem> x = poly1 | ranges::to<vector>();
    x.resize(2 * n);
    vector<Elem> y = poly2 | ranges::to<vector>();
    y.resize(2 * n);
    const vector<Complex> x_dft = fft<Elem>(x);
    const vector<Complex> y_dft = fft<Elem>(y);
    const vector<Complex> result_dft = views::zip_transform(
            [](Complex a, Complex b) {
                return a * b;
            },
            x_dft,
            y_dft
        )
        | ranges::to<vector>();
    const vector<Complex> result = fft_inverse<Complex>(result_dft);
    return result;
}

template <typename Elem>
vector<fft_complex_t<Elem>> polynomial_multiply_simple(span<const Elem> poly1, span<const Elem> poly2)
{
    using Complex = fft_complex_t<Elem>;
    const auto get = [](span<const Elem> ls, size_t index) -> Complex {
        if (index < ls.size()) {
            return ls[index];
        }
        return Complex{};
    };
    return views::iota(size_t{0}, poly1.size() + poly2.size())
        | views::transform(
            [=](size_t p) -> Complex {
                return ranges::fold_left(
                    views::iota(size_t{0}, p + 1)
                        | views::transform(
                            [=](size_t i) -> Complex {
                                return get(poly1, i) * get(poly2, p - i);
                            }
                        ),
                    Complex{},
                    plus{}
                );
            }
        )
        | ranges::to<vector>();
}

int main()
{
    vector<double> a {4, 7, -1, 3};
    vector<double> b {6, 33, 5, 2};
    vector<complex<double>> ab = polynomial_multiply<double>(a, b);
    for (complex<double> v : ab) {
        cout << v << '\n';
    }
    cout << '\n';
    vector<complex<double>> ab_s = polynomial_multiply_simple<double>(a, b);
    for (complex<double> v : ab_s) {
        cout << v << '\n';
    }
}
