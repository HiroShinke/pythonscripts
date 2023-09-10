


from dataclasses import dataclass, field
from typing import Self

class Paragraph:
    pass

@dataclass
class Section:
    name : str
    children : list[Paragraph] = field(default_factory=list)

    def addParagraph(self : Self, p : Paragraph):
        self.children.append(p)

@dataclass
class Paragraph:
    name : str
    children : list[str] = field(default_factory=list)

s = Section("kkk")
print(f"{s}")

a = Paragraph("A")
b = Paragraph("A")

s.addParagraph(a)
s.addParagraph(b)

print(f"{s}")


