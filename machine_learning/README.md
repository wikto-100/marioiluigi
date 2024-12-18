# Odpalenie treningu (krok 1 jest do usprawnienia)

## 0. Wymagania
- python (requirements.txt) (najlepiej venv)
- c++11/c++17
- swig (do generowania headerów c++ - python)
- just (do kompilacji biblioteki statycznej rusta)

## 1. Kompilacja MCTS (tymczasowo)
```bash
just marioiluigi/engine/chess_lib
cd marioiluigi/machine_learning/mcts
cp ../../engine/chess_lib/target/release/libchess_lib.a ./lib
make
```
## 2. Uruchomienie treningu
```bash
cd marioiluigi/machine_learning
python -m src.main
```
