from math import factorial
import sys

if __name__ == '__main__':

	for line in sys.stdin.readlines():
		number = int(line.strip())
		print sum([int(d) for d in str(factorial(number))])