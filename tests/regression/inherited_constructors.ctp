
    
class (Base:
    pass  # this has a default constructor
)

class (Derived(Base):
    pass  # this does too - (c++ implicitly calls Base default constructor)
)

def (main:
    d = Derived()
)
    