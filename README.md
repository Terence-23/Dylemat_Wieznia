# Dylemat więźnia
Dwóch znanych policji przestępców złapano w kradzionym aucie. Podejrzewa się ich o popełnienie dużo poważniejszego przestępstwa (zbrodni), na co jednak nie ma żadnych dowodów. Przestępcy są przesłuchiwani w osobnych celach bez możliwości komunikowania się ze sobą. Przesłuchujący ich komisarz wpada na pewien pomysł - proponuje im nagrodę za wsypanie wspólnika i dostarczenie
dowodów na jego udział w zbrodni. Możliwe są trzy sytuacje:
1.  oboje milczą - wówczas oboje otrzymują niewielki wyrok za kradzież auta (2 lata)
2.  jeden się przyznaje i wsypuje wspólnika - zdrajca wychodzi na wolność, jego kompan (tzw. frajer) otrzymuje wyrok za kradzież i za popełnienie zbrodni (5 lat)
3. oboje się przyznają i wsypują wspólnika - oboje otrzymują karę za kradzież i popełnienie zbrodni, nieco złagodzoną ze względu na współpracę z wymiarem sprawiedliwości (4 lata)

Można to przedstawić w postaci następującej macierzy: 
| Gracz 1 Gracz 2 | W | Z |
|-----------------|---|---|
| W | -2,-2 | -5,0 |
| Z |0,-5 | -4,-4 |
Strategia W oznacza współpracę (między graczami), czyli milczenie. Strategia Z oznacza zdradę, czyli
wsypanie wspólnika.
Gracz dostaje te informacje i wypłaty. Zostaje połączony przez serwer z drugim graczem (nie wie z
kim).
Ma podać swoją decyzję
Po otrzymaniu decyzji obu graczy każdy z nich dostaje informację jaki dostał wyrok.
Serwer podaje jaki procent równowag jest typu (W,W), typu(Z, Z) albo typu niesymetrycznego.