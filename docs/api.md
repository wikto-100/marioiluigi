## Ruch
Ruchy są opisywane za pomocą stringu w formacie:  
`\d[a-z]\d[a-z][pnbrqkc]{0,1}`  
gdzie pierwsze 2 znaki opisuja pozycje tego co ruszamy a nastepna 2 znaki gdzie to ruszamy   
5 znak opcjonalnie opisuje rodzaj promocji (literka reprezentaujaca figure w FEN) lub ze ruch powinien byc potraktowany jako roszade (c)
  
np  

2a4a  
^^ porusz o dwa do góry pionkiem białym na maks lewo

7a8ab  
^^ wybierz promocje bishop

e1g1c  
^^ roszada ze strony króla

e1c1c  
^^ roszada ze strony królowej


## Plansza

Plansza jest opisywana za pomocą stringa w Forsyth–Edwards Notation (FEN)  
zobacz: https://en.wikipedia.org/wiki/Forsyth%E2%80%93Edwards_Notation  

## Api funkcji
zwraca dostepne ruchy
```
string[] getAvailableMoves(string board);
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

---
```
bool isCheck(string board)
```
