use std::{collections::HashSet, hash::Hash};

use itertools::Itertools;
use lazy_static::lazy_static;
use rand::Rng;

use crate::{
    chess_raw::{ChessState, Coord, Move},
    logic::{self, can_do_move},
    parser, serializer,
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
    let mov = mv(a);
    return logic::can_do_move(state, mov, true, false)
        && logic::get_available_moves(state).contains(&mov);
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

#[test]
pub fn get_available_moves_fast_test() {
    let mut r = rand_mt::Mt19937GenRand32::new(3333);
    for i in 1..100 {
        let mut s = STARTING_POS.clone();
        for j in 1..100 {
            let fast: HashSet<Move> =
                HashSet::from_iter(logic::get_available_moves(&s).into_iter());
            let mut dif: HashSet<Move> =
                HashSet::from_iter(logic::get_available_moves_slow(&s).into_iter());
            for el in &fast {
                dif.remove(&el);
            }
            assert_eq!(dif, HashSet::new());

            let len = fast.len();
            if len == 0 {
                break;
            }
            let any = fast.into_iter().nth(r.gen_range(0..len)).unwrap();
            logic::apply_move(&mut s, any);
        }
    }
}
