#set page("us-letter")
#set table(
  fill: (x, y) =>
  if x == 0 or y == 0 { blue }
)
#show table.cell: it => {
  if it.x == 0 or it.y == 0 {
    set text(white)
    strong(it) 
  }
}
1. 
#table(
columns: 6,
rows: 4,
[],                       [*Domain*],            [*Direction*], [*Init*],           [*Merge*],      [*Transfer*],
[Reaching Definitions],   [Sets of defs],        [Forward],     [$T$],              [Union],        [$"out"_b = "gen"_b union ("in"_b - "kill"_b)$],
[Live Variables],         [Sets of vars],        [Backward],    [$emptyset$],       [Union],        [$f("out"_b) = "use"_b union ("out"_b - "kill"_b)$],
[Constant Propagation],   [Valuation or T],      [],            [$emptyset$],       [Intersection], [$"out"_b = f_b("in"_b)$],
[Available Expressions],  [Sets of expressions], [],            [$emptyset$],       [Intersection], [$"out"_b =  "gen"_b union ("in"_b - "kill"_b)$],
)
2.
The Worklist Algorithm is guaranteed to converge to a solution because the domain is finite and the function is monotonic, which means
the function will eventually work through all sets and converge.
