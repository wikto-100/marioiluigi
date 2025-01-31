#include "chess_lib.hpp"
#include <stdexcept>
#include <vector>
#include <string>

namespace {
    // Helper to handle errors from Rust side
    std::string handleAfterCall(const char* ptr)
    {
        // If Rust set an error, get it
        char* ptr_error = chess_lib_get_error();
        if (ptr_error != nullptr) {
            std::string msg(ptr_error);
            chess_lib_free_str(ptr_error);
            throw std::invalid_argument(msg);
        }
        // Otherwise convert the result to std::string
        std::string s(ptr);
        chess_lib_free_str(ptr);
        return s;
    }
}

namespace chess_lib {

std::vector<std::string> getAvailableMoves(const std::string &fen)
{
    char* ptr_result = chess_lib_get_available_moves(fen.c_str());
    std::string s_result = handleAfterCall(ptr_result);

    std::vector<std::string> results;
    std::string builder;
    for (char c : s_result) {
        if (c == '\n') {
            results.push_back(builder);
            builder.clear();
        } else {
            builder.push_back(c);
        }
    }
    return results;
}

std::string getAppliedMove(const std::string &fen, const std::string &mv)
{
    char* ptr = chess_lib_get_applied_move(fen.c_str(), mv.c_str());
    return handleAfterCall(ptr);
}

bool canDoMove(const std::string &fen, const std::string &mv)
{
    return chess_lib_can_do_move(fen.c_str(), mv.c_str());
}

bool isWhiteTurn(const std::string &fen)
{
    return chess_lib_is_white_turn(fen.c_str());
}

bool isLostCondition(const std::string &fen)
{
    return chess_lib_is_lost_condition(fen.c_str());
}

bool isCheck(const std::string &fen)
{
    return chess_lib_is_check(fen.c_str());
}

bool isPat(const std::string &fen)
{
    return chess_lib_is_pat(fen.c_str());
}

} // namespace chess_lib
