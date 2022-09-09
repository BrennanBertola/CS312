import random


def prime_test(N, k):
	# This is main function, that is connected to the Test button. You don't need to touch it.
	return fermat(N,k), miller_rabin(N,k)

# all significant time complexities are noted next to
# function and are further explained in the report
def mod_exp(x, y, N): # O(log(y))
    if y == 0: return 1
    z = mod_exp(x, y//2, N)
    if y % 2: return x*z**2%N #if y is odd
    else: return z**2%N #if y is even
	

def fprobability(k):
    return 1 - (1/2)**k #we test k times with each time having a 1/2 chance of failing


def mprobability(k):
    return 1 - (1/4)**k #we test k times with each time having a 1/4 chance of failing

def fermat(N,k): #O(k*log(N))
    #checks for base cases
    if N == 1: return 'composite'
    if N == 2 or N == 3: return 'prime'

    for i in range(k): # will check with k different values for a
        a = random.randint(2, N - 1)
        if mod_exp(a, N-1, N) != 1: return 'composite'

    return 'prime'

def miller_rabin(N,k):# O(k*log(N)^2)
    #checks for base cases
    if N == 1: return 'composite'
    if N == 2 or N == 3: return 'prime'

    for i in range(k): # will check with k different values for a
        y = N-1
        a = random.randint(2, N - 1)
        while(1): # contiues to halve y until y is odd, a -1 is returned, or a non 1/-1 is returned
            result = mod_exp(a, y, N)
            if result == N - 1: return 'prime'
            if result != 1: return 'composite'
            if y % 2 == 1: break
            y = y//2

    return 'prime'


# used for testing/debugging
if __name__ == '__main__':
    result = miller_rabin(97, 1)
    print (result)
