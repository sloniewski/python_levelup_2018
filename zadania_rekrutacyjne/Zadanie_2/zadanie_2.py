def isprime(n):
    """Returns True if n is prime."""
    if n == 2:
        return True
    if n == 3:
        return True
    if n % 2 == 0:
        return False
    if n % 3 == 0:
        return False

    i = 5
    w = 2

    while i * i <= n:
        if n % i == 0:
            return False

        i += w
        w = 6 - w

    return True


current_no = 3
primes_count = 1
primes_no = 1234567
primes_sum = 2

while primes_count < primes_no:
    if isprime(current_no):
        primes_sum += current_no
        primes_count += 1
    current_no += 2

print(primes_sum)
