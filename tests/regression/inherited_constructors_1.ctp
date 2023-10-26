
# deleted default constructor, explicit 1-arg constructor
class (Base:
    a: int
)

class (Derived(Base):  # Inheriting constructors because no user defined init method present. Default constructor is deleted (implicitly by c++) because it's deleted in the base class
    pass
)
    
def (main:
    d = Derived(5)
    std.cout << d.a
)
    