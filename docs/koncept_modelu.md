Wstępny koncept implementacji modelu szachowego opartego o sieć splotową:
    1. Reprezentacja stanów
    Należy przetworzyć planszę na format, który jest zrozumiały dla CNN.
    Planszę reprezentujemy jako tensor bitboardów, gdzie każdy bitboard odpowiada różnym figurom na planszy, kontrolowanym polom i (innym zasadom - todo).
    
    2. Przestrzeń działań
    Możliwe działania podejmowane przez agenta są legalnymi ruchami w danej pozycji. Tworzymy maskę legalnych ruchów, która jest reprezentowana jako tensor boolowski 8x8x8x8, w którym:
        - pierwsze 2 wymiary odpowiadają pozycji X, Y z której wykonywany jest ruch
        - pozostałe 2 wymiary odpowiadają pozycji X' , Y' na którą wykonywany jest ruch.
    Maska ta będzie przekrajana z outputem z CNN, aby model nie halucynował.

TODO: zintegruj dane z silnika z wejściem do modelu (Adrian + kod Michała)


3. Architektura sieci neuronowej (todo) - Wiktor
Proponowana architektura:

[Tensor Wejściowy]
   |
[Conv1] -> ReLU
   |
[Conv2] -> ReLU
   |
[Conv3] -> ReLU
   |
[Spłaszczenie]
   |
[FC1] -> ReLU
   |
[FC2] -> Sigmoid
   |
[Przekształcenie do Przestrzeni Akcji]
   |
[Warstwa Maskująca]
   |
[Normalizacja]
   |
[Wyjściowe Prawdopodobieństwa]


4. Sygnał nagrody (todo)
5. Strategia eksploracji (todo)