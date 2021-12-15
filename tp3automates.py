#!/usr/bin/env python3
"""
Applies Kleene's star, concatenation and union of automata.
"""

from automaton import Automaton, EPSILON, State, error, warn
import sys
import pdb # for debugging

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

if __name__ == "__main__" :
  if len(sys.argv) != 3:
    usagestring = "Usage: {} <automaton-file1.af> <automaton-file2.af>"
    error(usagestring.format(sys.argv[0]))

  # First automaton, argv[1]
  a1 = Automaton("dummy")
  a1.from_txtfile(sys.argv[1])
  a1.to_graphviz(a1.name+".gv")
  print(a1)

  # Second automaton, argv[2]
  a2 = Automaton("dummy")
  a2.from_txtfile(sys.argv[2])
  a2.to_graphviz(a2.name+".gv")
  print(a2)
    
  a1star = kleene(a1)
  print()
  print(a1star)
  a1star.to_graphviz("a1star.gv")

  a1a2 = concat(a1, a2)
  print()
  print(a1a2)
  a1a2.to_graphviz("a1a2.gv")

  a1ora2 = union(a1, a2)
  print()
  print(a1ora2)
  a1ora2.to_graphviz("a1ora2.gv")

