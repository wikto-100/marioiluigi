## Ruch
Ruchy są opisywane za pomocą stringu w formacie:  
`\d[a-z]\d[a-z]`  
gdzie pierwsze 2 znaki opisuja pozycje tego co ruszamy a nastepna 2 znaki gdzie to ruszamy   
np  
3a5a  

## Plansza

Plansza jest opisywana za pomocą stringa w Forsyth–Edwards Notation (FEN)  
zobacz: https://en.wikipedia.org/wiki/Forsyth%E2%80%93Edwards_Notation  

## Api funkcji
zwraca dostepne ruchy odzielone "\n"   
jeśli nie ma dostepnych ruchów (pat lub szach mat) zwróci pusty string  
```
string getAvailableMoves(string board);
```
---

```
bool canDoMove(string board, string move);  
```
---

zwraca plansze po zaplikowanie ruchu jeśli możliwe w FEN notation   
(w przypadku gdy ruch nie jest mozliwy  zwroci pusty string)  
```
string getAppliedMove(string board,string move)
```

---

```
bool isWhiteTurn(string board);
```
---

zwraca true w przypadku szach mata  
w przypadku pata zwróci false   
```
bool isLostCondition(string board)
```