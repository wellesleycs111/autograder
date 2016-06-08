"""Check for various properties of words like whether
a given word is a palindrome, can be written using only the
top row of the keyboard, and the number of Scrabble points the
word is worth.Also checks whether two words are anagrams
"""
__author__ = 'Wendy Wellesley'

def reverse(s):
    return s[::-1]

def isPalindrome(word):
    """determines whether a word is a palindrome
    (spelt the same backward as forward)"""
    word = word.lower()
    return reverse(word) == word

def isTopRow(word):
    """determines if word can be spelt using only
    the top row of the keyboard: q, w, e, r, t, y, u, i, o, p"""
    word = word.lower()
    top_letters = 'qwertyuiop'
    for letter in word:
        if letter not in top_letters:
            return False
    return True

def scrabblePoints(letter):
    if letter in 'aeilnorstu':
        return 1
    elif letter in 'dg':
        return 2
    elif letter in 'bcmp':
        return 3
    elif letter in 'fhvwy':
        return 4
    elif letter in 'k':
        return 5
    elif letter in 'jx':
        return 8
    elif letter in 'qz':
        return 10
    return 0 # in case letter is not one of 26

def scrabbleScore(word):
    """returns total number of Scrabble points that word
    is worth"""
    word = word.lower()
    total_points = 0
    for letter in word:
        total_points += scrabblePoints(letter)
    return total_points

def removeChar(s,char):
    """remove the first appearance of char from s. If char is not found returns s unchanged"""
    result=""
    s=s.lower()
    char=char.lower()
    removed=False
    for c in s:
        if c!=char or removed==True:
            result+=c
        elif not removed:
                removed=True
    return result
    
