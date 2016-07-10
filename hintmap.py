"""
Error Hint Map
"""

# TODO: pass these to the grade() function
ERROR_HINT_MAP = {
  'q1': {
    "<type 'exceptions.IndexError'>": """
      We noticed that your program threw an IndexError.
      While many things may cause this, it may have been from
      trying to access an index that's larger than the length of
      the list or string.
      Remember that indexing starts from 0.
    """
  },
  'q3': {
      "<type 'exceptions.AttributeError'>": """
        We noticed that your project threw an AttributeError on q3.
        While many things may cause this, it may have been from assuming
        a certain size or structure to the state space. For example, if you have
        a line of code assuming that the state is (x, y) and we run your code
        on a state space with (x, y, z), this error could be thrown. Try
        making your code more general and submit again!

    """
  }
}
