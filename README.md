# Learn FOLA

FOLAs are automata that assign each input word an element from some fully ordered lattice (some set {0,...,k}). We present an algorithm for learning automata for an unknown formal series (language) induced by some lattice automaton. In active learning algorithms, we use membership (values) and equivalence queries for learning and determining the automaton, and we wish to ask as less of them as possible. This package includes the following
  - Creating Lattice automata (LDFAs and FOLAs) from text.
  - Performing all useful operations on FOLAs.
  - Active learning for FOLAs.
  - Comparison between this algorithm and the LStar algorithm.

### Creating a FOLA
  - Create a text file `a.txt`
  - Add an initial state title
  - For each of the states in the automaton, add a row in the file as follows:
    q$v: a1|a1_val->q'1    a2|a2_val->q'2 ...
    Whereas `q` is the title of the state, `v` is the value of the state, `ai` are the alphabet letters, and `ai_val` are the values of each of the transitions made by these letters. `q'i` are the states to which the transitions are.
    - Example: <br />
		0=>  <br />
		0$2:          a|1->1        b|2->1  <br />      
		1$1:          a|2->0        b|0->1  <br />
		
    is the following FOLA:
    ![FOLA](a1.png?raw=true "A FOLA")
    - Create the alphabet and the lattice for the automaton
        - `lattice = Lattice.Lattice.numbers_lattice(list(range(4)))`
        - `alphabet = ['a', 'b']`
    - Create the automaton
        - `a = LDFA.LDFA.create_by_input(alphabet, lattice, "a.txt")`

### Learning FOLA

- Once you have the text file for the automaton, you can learn is using the following method:
    - `run_test_from_file("a.txt", lattice, alphabet)`
- The result will be printed in no time! (polynomial...)