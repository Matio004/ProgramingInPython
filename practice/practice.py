"""Dose this.

This file generates prime numbers, does prime factorization and calculates lcm.
"""


def sieve(limit):
    """
    Return list of prime numbers using sieve of Eratosthenes algorithm.

    :param limit: the last number to be checked
    :return: list of prime numbers
    """
    primes = [True]*(limit + 1)
    i = 2
    while i * i < limit:
        if primes[i]:
            for j in range(i * i, limit + 1, i):
                primes[j] = False
        i += 1
    numbers = []

    for number in range(2, limit + 1):
        if primes[number]:
            numbers.append(number)
    return numbers


def prime_factorization(n):
    """
    Return prime factors for given number.

    :param n: integer number
    :return: dict with prime_factor: count of such factors
    """
    factors = {}
    i = 2
    while n != 1:
        while n % i == 0:
            factors[i] = factors.get(i, 0) + 1
            n //= i
        i += 1
    return factors


def lcm(a, b):
    """
    Return lowerest common multiplier using prime factorization.

    :param a: number
    :param b: other number
    :return: lcm integer
    """
    a_factors = prime_factorization(a)
    b_factors = prime_factorization(b)

    lcm_ = 1
    primes = set(a_factors.keys()) | set(b_factors.keys())
    for i in primes:
        lcm_ *= i ** max(a_factors.get(i, 0), b_factors.get(i, 0))
    return lcm_


print('Liczby pierwsze od 2 do 100:', sieve(100))
print('LCM(192, 348) =', lcm(192, 348))
