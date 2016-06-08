def isValidGesture(gesture):
    """Returns True if gesture is one of the
    strings 'rock', 'paper', or 'scissors',
    and False otherwise."""
    return gesture in ['rock', 'paper', 'scissors']

def beats(gesture1, gesture2):
    """Returns True if the first gesture beats the second
    gesture, i.e., if the first and second gesture are
    rock/scissors or scissors/paper or paper/rock,
    respectively. Returns False otherwise."""
    return (gesture1=='rock' and gesture2!='paper') or (gesture1=='paper' and gesture2!='scissors') or (gesture1=='scissors' and gesture2!='rock')
