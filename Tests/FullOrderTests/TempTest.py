import Lattice
from Tests.Run_Test import run_test_from_file

lattice = Lattice.Lattice.numbers_lattice(list(range(20)))
alphabet = ['a', 'b']

run_test_from_file("../../Examples/temp_test1.txt", lattice, alphabet)
