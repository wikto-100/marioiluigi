use lazy_static::lazy_static;

use crate::{
    chess_raw::{ChessState, Coord, Move},
    logic::{self, can_do_move},
    parser,
};

lazy_static! {
    static ref STARTING_POS: ChessState =
        parser::parse_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1").unwrap();
    static ref WHITE_VS_KING: ChessState =
        parser::parse_fen("k7/8/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1").unwrap();
    static ref CASTLING_TEST: ChessState =
        parser::parse_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/R3K2R w KQkq - 0 1").unwrap();
}

pub fn mv(a: &str) -> Move {
    return parser::parse_move(a).unwrap();
}
pub fn apply_mvp(state: &mut ChessState, a: &str) -> Result<(), String> {
    return logic::apply_move(state, mv(a));
}
pub fn can_mvp(state: &ChessState, a: &str) -> bool {
    return logic::can_do_move(state, mv(a), true, false);
}
pub fn skip(state: &mut ChessState) {
    state.current = state.current.reverse();
}
#[test]
pub fn test_king_moves() {
    let mut s = WHITE_VS_KING.clone();

    skip(&mut s);
    assert!(can_mvp(&s, "a8a7"));

    assert!(!can_mvp(&s, "a8a9"));

    assert!(can_mvp(&s, "a8b7"));

    assert!(!can_mvp(&s, "a8b6"));

    apply_mvp(&mut s, "a8b7").unwrap();
    skip(&mut s);

    assert!(can_mvp(&s, "b7b6"));
    assert!(can_mvp(&s, "b7b8"));

    assert!(can_mvp(&s, "b7a7"));
    assert!(can_mvp(&s, "b7c7"));

    assert!(can_mvp(&s, "b7a8"));
    assert!(can_mvp(&s, "b7c6"));
    assert!(can_mvp(&s, "b7a6"));
    assert!(can_mvp(&s, "b7c8"));
}
