#!/usr/bin/env python3
"""
Read a regular expression and returns:
 * YES if word is recognized
 * NO if word is rejected"""

from typing import Set, List
from automaton import Automaton, EPSILON, State, error, warn, RegExpReader
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


"""
    Takes an Automaton object.
    Returns the first epsilon transition encountered as a tuple (source, symbol, dest)
"""
def getEpsilonState(a):
    for (source, symbol, dest) in a.transitions:
        if symbol == EPSILON:
            return (source, symbol, dest)
    return None
    

"""
    Takes an Automaton object, a list of states and a symbol.
    Returns a set of destination states.
"""
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

        
"""
    Takes an Automaton object and a list of states.
    Returns True if at least one of the states is accepting. Returns False otherwise.
"""                
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

def new_state(a1:Automaton) -> str:
    maxstate = -1
    for a in a1.states:
        try:
            maxstate = max(int(a), maxstate)
        except ValueError:
            pass
    return str(maxstate + 1)


def kleene(a1:Automaton)->Automaton:
    new_aut = a1.deepcopy()
    new_aut.name = "kleene(" + a1.name + ")"
    for accepting_state in a1.acceptstates:
        new_aut.add_transition(accepting_state, EPSILON, a1.initial.name)
    new_state_name = new_state(new_aut)
    new_aut.add_transition(new_state_name, EPSILON, a1.initial.name)
    new_aut.initial = new_aut.statesdict[new_state_name]
    new_aut.make_accept(new_state_name)
    return new_aut 

##################

def concat(a1:Automaton, a2:Automaton)->Automaton:
    new_aut = a2.deepcopy()
    new_aut.name = "concat(" + a1.name + "," + a2.name + ")"
    new_state_name = str(max(int(new_state(a1)), int(new_state(a2))))
    for state in a2.states:
        if state in a1.states or state:
            new_aut.rename_state(state, new_state_name)
            new_state_name = str(int(new_state_name) + 1)
    
    for (s,a,d) in a1.transitions:
        new_aut.add_transition(s, a, d)
    
    for state in a1.acceptstates:
        new_aut.add_transition(state, EPSILON, new_aut.initial.name)
    
    new_aut.initial = new_aut.statesdict[a1.initial.name]
    
    return new_aut
    

##################

def union(a1:Automaton, a2:Automaton)->Automaton:
    new_aut = a2.deepcopy()
    new_aut.name = "union(" + a1.name + "," + a2.name + ")"
    new_state_name = str(max(int(new_state(a1)), int(new_state(a2))))
    for state in a2.states:
        if state in a1.states:
            new_aut.rename_state(state, new_state_name)
            new_state_name = str(int(new_state_name) + 1)
            
    for (s,a,d) in a1.transitions:
        new_aut.add_transition(s, a, d)
        
    new_aut.make_accept(a1.acceptstates)
    
    new_aut.add_transition(new_state_name, EPSILON, new_aut.initial.name)
    new_aut.add_transition(new_state_name, EPSILON, a1.initial.name)
    new_aut.initial = new_aut.statesdict[new_state_name]
    
    return new_aut 

##################
   
def regexp_to_automaton(re:str)->Automaton:
  """
  Moore's algorithm: regular expression `re` -> non-deterministic automaton
  """
  postfix = RegExpReader(re).to_postfix()
  stack:List[Automaton] = []
  #TODO implement!
  for item in postfix:
      if item.isalnum():
          a = Automaton(item)
          a.add_transition("0", item, "1")
          a.make_accept("1")
          stack.append(a)
      elif item == "+":
          right = stack.pop()
          left = stack.pop()
          a = union(left,right)
          a.name = "union({},{})".format(left.name, right.name)
          stack.append(a)
      elif item == ".":
          right = stack.pop()
          left = stack.pop()
          a = concat(left,right)
          a.name = "concat({},{})".format(left.name, right.name)
          stack.append(a)
      elif item == "*":
          elem = stack.pop()
          a = kleene(elem)
          a.name = "kleene({})".format(elem.name)
          stack.append(a)
  return stack[0]

  
##################

if __name__ == "__main__" :

  if len(sys.argv) != 3:
    usagestring = "Usage: {} <regular-expression> <word-to-recognize>"
    error(usagestring.format(sys.argv[0]))

  regexp = sys.argv[1]  
  word = sys.argv[2]

  a = regexp_to_automaton(regexp)
  determinise(a)
  if recognizes(a, word):
    print("YES")
  else:
    print("NO")

