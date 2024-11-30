use std::str;

use crate::{chess_raw::Color, logic, parser, serializer};

pub fn internal_get_available_moves(board_fen: &str) -> Result<Vec<String>, String> {
    let f = parser::parse_fen(board_fen)?;
    let moves = logic::get_available_moves(&f);
    return Ok(moves.iter().map(|e| e.to_string()).collect());
}
pub fn internal_can_do_move(board_fen: &str, mv: &str) -> Result<bool, String> {
    let f = parser::parse_fen(board_fen)?;
    let mv = parser::parse_move(mv)?;
    return Ok(logic::can_do_move(&f, mv, true, false));
}
pub fn internal_get_applied_move(board_fen: &str, mv: &str) -> Result<String, String> {
    let mut f = parser::parse_fen(board_fen)?;
    let mv = parser::parse_move(mv)?;
    logic::apply_move(&mut f, mv)?;
    return Ok(serializer::serialize_to_fen(&f));
}
pub fn internal_is_white_turn(board_fen: &str) -> Result<bool, String> {
    let f = parser::parse_fen(board_fen)?;
    return Ok(f.current == Color::White);
}

pub fn internal_is_lost_condition(board_fen: &str) -> Result<bool, String> {
    let f = parser::parse_fen(board_fen)?;
    return Ok(logic::is_lost_condition(&f));
}
pub fn internal_is_check(board_fen: &str) -> Result<bool, String> {
    let f = parser::parse_fen(board_fen)?;
    return Ok(logic::is_check(&f));
}
pub fn internal_is_pat(board_fen: &str) -> Result<bool, String> {
    let f = parser::parse_fen(board_fen)?;
    return Ok(logic::get_available_moves(&f).len() == 0 && !logic::is_lost_condition(&f));
}
