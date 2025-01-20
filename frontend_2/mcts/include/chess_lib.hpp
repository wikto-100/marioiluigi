#ifndef CHESS_LIB_HPP
#define CHESS_LIB_HPP

#include <string>
#include <stdexcept>
#include <vector>

// Declare C functions with C linkage
extern "C" {
    char* chess_lib_get_available_moves(const char*);
    char* chess_lib_get_applied_move(const char* fen, const char* mv);

    bool chess_lib_can_do_move(const char*, const char* mv);
    bool chess_lib_is_white_turn(const char*);
    bool chess_lib_is_lost_condition(const char*);
    bool chess_lib_is_check(const char*);
    bool chess_lib_is_pat(const char*);

    char* chess_lib_get_error();
    void chess_lib_free_str(const char*);
}

// C++ wrapper functions within the chess_lib namespace
namespace chess_lib {
    // Declarations only
    std::vector<std::string> getAvailableMoves(const std::string &fen);
    std::string getAppliedMove(const std::string &fen, const std::string &mv);
    bool canDoMove(const std::string &fen, const std::string &mv);
    bool isWhiteTurn(const std::string &fen);
    bool isLostCondition(const std::string &fen);
    bool isCheck(const std::string &fen);
    bool isPat(const std::string &fen);
}

#endif // CHESS_LIB_HPP
