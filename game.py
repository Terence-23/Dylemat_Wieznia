from enum import Enum

class PDecisions(Enum):
    NULL =-1
    BETRAY = 1
    COOPERATE = 2
    
class PState:
    def __init__(self, UID) -> None:
        self.UID = UID
        self.decision = PDecisions.NULL    

class Game:
    def __init__(self, UID1, UID2, *args):
        self.p1 = PState(UID1)
        self.p2 = PState(UID2)
        
    def resolved(self):
        return self.p1.decision != PDecisions.NULL and\
            self.p2.decision != PDecisions.NULL
    
    def result(self):
        if not self.resolved(): return None
        elif self.p1.decision == PDecisions.BETRAY:
            if self.p2.decision == PDecisions.BETRAY: return (-4, -4)
            else: return (0, -5) 
        else:
            if self.p1.decision == PDecisions.BETRAY: return (-5, 0)
            else: return (-2, -2)
            
    def p_result(self, UID):
        if not self.resolved(): return None
        elif self.p1.UID == UID: return self.result()[0]
        elif self.p2.UID == UID: return self.result()[1]
        else: return None
        
    def has_player(self, UID):
        return self.p1.UID == UID or self.p2.UID == UID
    
    def add_decision(self, UID, decision):
        if self.p1.UID == UID: self.p1.decision = decision
        elif self.p2.UID == UID: self.p2.decision = decision
   