
#include <iostream>
#include "../cpp_headers/chess_lib.hpp"
#include <sstream>
#include <algorithm>

#define ASSERT(EXPR) assert(EXPR, #EXPR)

void assert(bool cnd, const char *msg)
{
    if (!cnd)
    {
        std::cerr << "assertion failed, when: " << msg;
        exit(1);
    }
}

void test_api()
{

    auto fen = std::string("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1");
    try
    {
        ASSERT(chess_lib::isWhiteTurn(fen));
        ASSERT(!chess_lib::isCheck(fen));
        ASSERT(!chess_lib::isLostCondition(fen));
        ASSERT(chess_lib::getAppliedMove(fen, "a2a4") == std::string("rnbqkbnr/pppppppp/8/8/P7/8/1PPPPPPP/RNBQKBNR b KQkq a3 0 1"));
        ASSERT(!chess_lib::canDoMove(fen, "a2a5"));
        ASSERT(chess_lib::canDoMove(fen, "a2a4"));

        // 2 move check-mate
        fen = chess_lib::getAppliedMove(fen, "f2f4");
        fen = chess_lib::getAppliedMove(fen, "e7e5");
        fen = chess_lib::getAppliedMove(fen, "g2g4");
        fen = chess_lib::getAppliedMove(fen, "d8h4");

        ASSERT(chess_lib::isLostCondition(fen));
        ASSERT(chess_lib::isCheck(fen));
        ASSERT(chess_lib::getAvailableMoves(fen).size() == 0);

        fen = std::string("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1");

        // 2 move check-only
        fen = chess_lib::getAppliedMove(fen, "f2f4");
        fen = chess_lib::getAppliedMove(fen, "e7e5");
        fen = chess_lib::getAppliedMove(fen, "h2h4");
        fen = chess_lib::getAppliedMove(fen, "d8h4");
        ASSERT(!chess_lib::isLostCondition(fen));
        ASSERT(chess_lib::isCheck(fen));
        ASSERT(chess_lib::getAvailableMoves(fen).size() > 0);

        fen = "k7/8/8/8/8/8/8/K7 w - - 0 1";
        std::vector<std::string> moves = chess_lib::getAvailableMoves(fen);
        std::sort(moves.begin(), moves.end());
        std::vector<std::string> expected = {"a1a2", "a1b1", "a1b2"};
        assert(moves == expected, "get availabe moves test on king only\n");
    }
    catch (const std::invalid_argument &exc)
    {
        std::stringstream s;
        s << "an exception was thrown: " << exc.what();
        assert(false, s.str().c_str());
    }
}

int main()
{
    test_api();
}
