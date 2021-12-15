#!/usr/bin/env python3
"""
Read an automaton and a word, returns:
 * YES if word is recognized
 * NO if word is rejected
Determinises the automaton if it's non deterministic
"""

from typing import Set, List
from automaton import Automaton, EPSILON, State, error, warn
import sys
import pdb # for debugging

##################

def is_deterministic(a:'Automaton')->bool:
  for state, state_automaton in a.statesdict.items():
      if state == "%":
          return False
      for k,v in state_automaton.transitions.items():
          if (len(list(v)) > 1):
              return False
  return True
  
##################
  
def recognizes(a:'Automaton', word:str)->bool:
  current_state = a.initial
  for char in word:
      if char != "%":
          if char not in a.statesdict[str(current_state)].transitions:
              return False
          current_state = list(a.statesdict[str(current_state)].transitions[char])[0]
      
  if str(current_state) not in a.acceptstates:
      return False
  
  return True
  
##################

def getEpsilonState(a):
    for (source, symbol, dest) in a.transitions:
        if symbol == EPSILON:
            return (source, symbol, dest)
    return None
    

def getDestination(a, state_list, symbol):
    dest = set()
    for state in state_list:
        if a.statesdict[state].transitions.get(symbol):
            dest.update([dest.name for dest in a.statesdict[state].transitions.get(symbol)])
    return dest 

        
def short_circuit(a, transition):
    source, symbol, middle = transition
    if isAccepting(a, [middle]):
        a.make_accept(source)
    if source != middle:
        middle_transitons = a.statesdict[middle].transitions
        for s in a.alphabet:
            dests = middle_transitons.get(s)
            if dests:
                dests = list(dests)
                for dest in dests:
                    if not(str(dest) == middle and s == EPSILON):
                        a.add_transition(source, s, str(dest))
    a.remove_transition(source, symbol, middle)
        
                
def isAccepting(a, states):
    for state in states:
        if state in a.acceptstates:
            return True
    return False


def reduce_states(a):
    det = Automaton("dfa")
    new_states = [set([a.initial.name])]
    
    i = 0
    while i < len(new_states):
        for symbol in a.alphabet:
            new_dest = getDestination(a, new_states[i], symbol)
            if len(new_dest) > 0:
                if str(new_dest) not in det.statesdict:
                    new_states.append(new_dest)
                det.add_transition(str(new_states[i]), symbol, str(new_dest))
        if isAccepting(a, new_states[i]):
            det.make_accept(str(new_states[i]))
        i = i + 1
    det.remove_unreachable()
    return det
                
def rename_states(a:Automaton):
    namecount = 0
    for state in a.states:
        a.rename_state(state, str(namecount))
        namecount = namecount + 1 
    
def determinise(a:Automaton):
    epsilon_transition = getEpsilonState(a)
    while epsilon_transition:
        short_circuit(a, epsilon_transition)
        a.remove_unreachable()
        epsilon_transition = getEpsilonState(a)
    
    det = reduce_states(a)
    rename_states(det)
    
    a.reset()
    a.from_txt(det.to_txtfile())
  
##################

if __name__ == "__main__" :
  if len(sys.argv) != 3:
    usagestring = "Usage: {} <automaton-file.af> <word-to-recognize>"
    error(usagestring.format(sys.argv[0]))

  automatonfile = sys.argv[1]  
  word = sys.argv[2]

  a = Automaton("dummy")
  a.from_txtfile(automatonfile)
  if not is_deterministic(a) :
    determinise(a)
  if recognizes(a, word):
    print("YES")
  else:
    print("NO")
