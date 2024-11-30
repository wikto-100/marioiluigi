#ifndef CHESS_LIB_HPP
#define CHESS_LIB_HPP
#include <string>
#include <stdexcept>
#include <vector>
#include <iostream>
namespace
{
    extern "C"
    {
        char *chess_lib_get_available_moves(const char *);
        char *chess_lib_get_applied_move(const char *fen, const char *mv);

        bool chess_lib_can_do_move(const char *, const char *mv);
        bool chess_lib_is_white_turn(const char *);
        bool chess_lib_is_lost_condition(const char *);
        bool chess_lib_is_check(const char *);
        bool chess_lib_is_pat(const char *);

        char *chess_lib_get_error();
        void chess_lib_free_str(const char *);
    }
    std::string handleAfterCall(const char *ptr)
    {
        char *ptr_erorr = chess_lib_get_error();
        if (ptr_erorr == nullptr)
        {
            std::string s = std::string(ptr);
            chess_lib_free_str(ptr);
            return s;
        }
        std::string s_er = std::string(ptr_erorr);
        chess_lib_free_str(ptr_erorr);
        throw std::invalid_argument(s_er);
    }

}
namespace chess_lib
{
    std::vector<std::string> getAvailableMoves(const std::string &fen)
    {
        char *ptr_result = chess_lib_get_available_moves(fen.c_str());
        std::string s_result = handleAfterCall(ptr_result);
        std::string builder = "";

        std::vector<std::string> results;

        // note: \n will be at the very end as well
        for (char c : s_result)
        {

            if (c == '\n')
            {
                results.push_back(builder);
                builder = "";
            }
            else
            {
                builder += c;
            }
        }

        return results;
    }
    std::string getAppliedMove(const std::string &fen, const std::string &mv)
    {
        char *res_ptr = chess_lib_get_applied_move(fen.c_str(), mv.c_str());
        return handleAfterCall(res_ptr);
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
}

#endif