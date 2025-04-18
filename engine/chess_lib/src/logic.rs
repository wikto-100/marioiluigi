use core::panic;

use itertools::Itertools;

use crate::chess_raw::*;

const MAX_MAP: [[[Option<Coord>; 65]; 2]; 6] = generate_max_move_map();

fn raw_move(state: &ChessState, b: Move, effects_ref: &mut Vec<Effect>) {
    effects_ref.push(EffectHelper::get_change(
        b.to,
        state.pieces_data.get(b.from),
    ));
    effects_ref.push(EffectHelper::get_change(b.from, None));
}

fn handle_pawn(state: &ChessState, b: Move) -> Option<Vec<Effect>> {
    //dont use state.current at that point
    let clr = state.pieces_data.get(b.from).unwrap().clr;

    let mut effects = handle_pawn_no_promotion(state, b)?;
    if Coord::row_point_of_view(b.to.y(), clr) != 8 {
        return Some(effects);
    }

    let promote_to = match b.additional {
        Some(AdditionalMoveData::Promotion(p)) if p != PieceKind::King => p,
        _ => PieceKind::Queen,
    };

    effects.push(EffectHelper::get_change(
        b.to,
        Some(ColoredPiece::new(promote_to, clr)),
    ));
    return Some(effects);
}
fn handle_pawn_no_promotion(state: &ChessState, b: Move) -> Option<Vec<Effect>> {
    let mut effects = Vec::new();
    let us = state.pieces_data.get(b.from).unwrap();
    let maybe_piece_on_target = state.pieces_data.get(b.to);

    let start_pos = b.from;
    let end_pos = b.to;

    let real_up = Coord::point_of_view_dir(&Coord::UP, us.clr);
    let real_down = Coord::point_of_view_dir(&Coord::DOWN, us.clr);

    let real_up_left = real_up + Coord::LEFT;
    let real_up_right = real_up + Coord::RIGHT;
    //--- enemy ---

    if maybe_piece_on_target.is_some() {
        if end_pos == start_pos + real_up_left || end_pos == start_pos + real_up_right {
            raw_move(state, b, &mut effects);
            return Some(effects);
        }
        return None;
    }

    //-- maybe en-passant --

    if Some(end_pos) == state.en_passant {
        let enemy_pos = end_pos + real_down;

        if end_pos == start_pos + real_up_left || end_pos == start_pos + real_up_right {
            raw_move(state, b, &mut effects);
            effects.push(EffectHelper::get_change(enemy_pos, None));
            return Some(effects);
        }
        return None;
    }

    //--- no enemy on target ---

    //we can't move 2 up even if its the first pawn move IF there's something block one block above
    let is_something_one_up =
        start_pos.y() != 8 && state.pieces_data.get(b.from + real_up).is_some();

    let in_second_row = start_pos.y() == Coord::row_point_of_view(Coord::WHITE_SECOND_ROW, us.clr);
    let is_one_up = end_pos == start_pos + real_up;
    let is_two_up = end_pos == start_pos + real_up * 2;

    if (in_second_row && is_two_up && !is_something_one_up) || is_one_up {
        raw_move(state, b, &mut effects);
        if is_two_up {
            effects.push(Box::new(move |s| s.en_passant = Some(start_pos + real_up)));
        }
        return Some(effects);
    } else {
        return None;
    }
}

fn handle_rook(state: &ChessState, b: Move) -> Option<Vec<Effect>> {
    let mut effects = Vec::new();
    let us = state.pieces_data.get(b.from).unwrap();
    let (from, to) = (b.from, b.to);

    if from.x() != to.x() && from.y() != to.y() {
        return None;
    }

    let sign = (to - from).piecewise_sign();
    if is_anything_in_the_way_excluding(state, from, sign, to) {
        return None;
    }
    raw_move(state, b, &mut effects);

    if from == Coord(1, Coord::row_point_of_view(1, us.clr)) {
        effects.push(Box::new(move |s| {
            s.castling[us.clr.repr()].queen_side = false;
        }))
    } else if from == Coord(8, Coord::row_point_of_view(1, us.clr)) {
        effects.push(Box::new(move |s| {
            s.castling[us.clr.repr()].king_side = false;
        }))
    }

    return Some(effects);
}
fn handle_bishop(state: &ChessState, b: Move) -> Option<Vec<Effect>> {
    let mut effects = Vec::new();
    let (from, to) = (b.from, b.to);
    let dif = to - from;

    if dif.x().abs() != dif.y().abs() {
        return None;
    }
    let sign = dif.piecewise_sign();
    if is_anything_in_the_way_excluding(state, from, sign, to) {
        return None;
    }

    raw_move(state, b, &mut effects);
    return Some(effects);
}
fn handle_queen(state: &ChessState, b: Move) -> Option<Vec<Effect>> {
    let mut effects = Vec::new();
    let (from, to) = (b.from, b.to);
    let dif = to - from;
    if (from.x() != to.x() && from.y() != to.y()) && dif.x().abs() != dif.y().abs() {
        return None;
    }
    let sign = dif.piecewise_sign();
    if is_anything_in_the_way_excluding(state, from, sign, to) {
        return None;
    }
    raw_move(state, b, &mut effects);
    return Some(effects);
}

fn handle_knight(state: &ChessState, b: Move) -> Option<Vec<Effect>> {
    let mut effects = Vec::new();
    let (from, to) = (b.from, b.to);
    let dif = to - from;
    let abs_dif = dif.piecewise_abs();
    if (abs_dif.x() == 2 && abs_dif.y() == 1) || (abs_dif.x() == 1 && abs_dif.y() == 2) {
        raw_move(state, b, &mut effects);
        return Some(effects);
    }
    return None;
}
fn handle_king(state: &ChessState, b: Move) -> Option<Vec<Effect>> {
    let mut effects = Vec::new();
    let (from, to) = (b.from, b.to);
    let dif = to - from;
    let x_dif_abs = dif.x().abs();
    let y_dif_abs = dif.y().abs();
    if (x_dif_abs + y_dif_abs) == 1 || (x_dif_abs == y_dif_abs && x_dif_abs == 1) {
        raw_move(state, b, &mut effects);
        effects.push(EffectHelper::get_unmark_castling(state.current));

        return Some(effects);
    }
    return None;
}
fn handle_castling(state: &ChessState, b: Move) -> Option<Vec<Effect>> {
    let mut effects = Vec::new();

    let t = if b.to.x() < b.from.x() {
        CastlingType::QueenSide
    } else {
        CastlingType::KingSide
    };

    match t {
        CastlingType::KingSide if !state.castling[state.current.repr()].king_side => return None,
        CastlingType::QueenSide if !state.castling[state.current.repr()].queen_side => return None,
        _ => {}
    };

    //todo: do additional asserts
    //for know we assume the castling data is correct (at least the rook and king are in the correct positions)

    let piece = state.pieces_data.get(b.from).unwrap();
    if piece.piece_kind != PieceKind::King {
        return None;
    }
    if !((t == CastlingType::KingSide && b.to == b.from + Coord::make_x(2))
        || (t == CastlingType::QueenSide && b.to == b.from - Coord::make_x(2)))
    {
        return None;
    }

    if t == CastlingType::KingSide {
        for add in 1..=2 {
            let coord = b.from + Coord::make_x(add);
            if state.pieces_data.get(coord).is_some() {
                return None;
            }
        }
        raw_move(state, b, &mut effects);
        raw_move(
            state,
            Move::new(Coord(8, b.from.y()), b.to - Coord::make_x(1)),
            &mut effects,
        );
    } else if t == CastlingType::QueenSide {
        for add in 1..=3 {
            let coord = b.from - Coord::make_x(add);
            if state.pieces_data.get(coord).is_some() {
                return None;
            }
        }
        raw_move(state, b, &mut effects);
        raw_move(
            state,
            Move::new(Coord(1, b.from.y()), b.to + Coord::make_x(1)),
            &mut effects,
        );
    }
    effects.push(EffectHelper::get_unmark_castling(state.current));
    return Some(effects);
}

//for every piece
//for every color
//list of coords
pub const fn generate_max_move_map() -> [[[Option<Coord>; 65]; 2]; 6] {
    const N: usize = 65;
    const fn insert<const N1: usize, const N2: usize>(inp: &[Coord; N1]) -> [Option<Coord>; N2] {
        let mut a: [Option<Coord>; N2] = [None; N2];
        let mut i = 0;
        while i < N1 {
            a[i] = Some(inp[i]);
            i += 1;
        }
        a[i] = None;
        return a;
    }
    const fn get_pawn_white() -> [Option<Coord>; N] {
        return insert(&[Coord::UP, Coord::UP_TWICE, Coord::UP_LEFT, Coord::UP_RIGHT]);
    }
    const fn get_pawn_black() -> [Option<Coord>; N] {
        return insert(&[
            Coord::DOWN,
            Coord::DOWN_TWICE,
            Coord::DOWN_LEFT,
            Coord::DOWN_RIGHT,
        ]);
    }
    const fn get_knight() -> [Option<Coord>; N] {
        return insert(&[
            Coord(1, 2),
            Coord(-1, 2),
            Coord(1, -2),
            Coord(-1, -2),
            Coord(2, 1),
            Coord(2, -1),
            Coord(-2, 1),
            Coord(-2, -1),
        ]);
    }
    const fn get_bishop() -> [Coord; 32] {
        let mut a: [Coord; 32] = [Coord(0, 0); 32];
        let mut i: i32 = 0;
        while i < 8 {
            a[i as usize] = Coord(i + 1, i + 1);
            a[(i + 8) as usize] = Coord(-(i + 1), -(i + 1));
            a[(i + 16) as usize] = Coord(i + 1, -(i + 1));
            a[(i + 24) as usize] = Coord(-(i + 1), i + 1);
            i += 1;
        }
        return a;
    }
    const fn get_rook() -> [Coord; 32] {
        let mut a: [Coord; 32] = [Coord(0, 0); 32];
        let mut i: i32 = 0;
        while i < 8 {
            a[i as usize] = Coord(0, i + 1);
            a[(i + 8) as usize] = Coord(0, -(i + 1));
            a[(i + 16) as usize] = Coord(i + 1, 0);
            a[(i + 24) as usize] = Coord(-(i + 1), 0);
            i += 1;
        }
        return a;
    }
    const fn get_queen() -> [Coord; 64] {
        let b = get_bishop();
        let r = get_rook();
        //note: even tho 64 may seem like bruteforcing all options, most of them will be instantly discarded
        //as they are out of border
        let mut a: [Coord; 64] = [Coord(0, 0); 64];
        let mut i = 0;
        while i < 32 {
            a[i] = b[i];
            a[i + 32] = r[i];
            i += 1;
        }
        return a;
    }

    const fn get_king() -> [Coord; 8] {
        return [
            Coord::LEFT,
            Coord::RIGHT,
            Coord::UP,
            Coord::DOWN,
            Coord::UP_LEFT,
            Coord::UP_RIGHT,
            Coord::DOWN_LEFT,
            Coord::DOWN_RIGHT,
        ];
    }
    let mut ar: [[[Option<Coord>; N]; 2]; 6] = [[[None; N]; 2]; 6];
    ar[PieceKind::Pawn as usize] = [get_pawn_white(), get_pawn_black()];
    ar[PieceKind::Knight as usize] = [get_knight(), get_knight()];
    ar[PieceKind::Bishiop as usize] = [insert(&get_bishop()), insert(&get_bishop())];
    ar[PieceKind::Rook as usize] = [insert(&get_rook()), insert(&get_rook())];
    ar[PieceKind::Queen as usize] = [insert(&get_queen()), insert(&get_queen())];
    ar[PieceKind::King as usize] = [insert(&get_king()), insert(&get_king())];
    return ar;
}

//note max_map doesn't include castling
pub fn read_max_map(piece: ColoredPiece) -> impl Iterator<Item = Coord> {
    return MAX_MAP[piece.piece_kind as usize][1 - piece.clr as usize]
        .iter()
        .filter_map(|e| *e);
}
pub fn get_available_moves(state: &ChessState) -> Vec<Move> {
    let mut moves: Vec<Move> = Vec::new();
    for (i, j) in (1..=8).cartesian_product(1..=8) {
        let left = Coord(i, j);
        let maybe_cur_piece = state.pieces_data.get(left);

        //early skip for easy using max_map
        if maybe_cur_piece.is_none() || maybe_cur_piece.unwrap().clr != state.current {
            continue;
        }
        let piece = maybe_cur_piece.unwrap();

        for coord_dif in read_max_map(piece) {
            let right = left + coord_dif;
            let mv = Move::new(left, right);
            if can_do_move(&state, mv, true, false) {
                moves.push(mv);
            }
        }
        if piece.piece_kind == PieceKind::King {
            let mv = Move::new_with(left, left + Coord(2, 0), None);
            if can_do_move(&state, mv, true, false) {
                moves.push(mv);
            }
            let mv = Move::new_with(left, left + Coord(-2, 0), None);
            if can_do_move(&state, mv, true, false) {
                moves.push(mv);
            }
        }
    }
    return moves;
}

pub fn get_available_moves_slow(state: &ChessState) -> Vec<Move> {
    let mut moves: Vec<Move> = Vec::new();
    for (i, j) in (1..=8).cartesian_product(1..=8) {
        let left = Coord(i, j);

        let maybe_cur_piece = state.pieces_data.get(left);

        if maybe_cur_piece.is_none() || maybe_cur_piece.unwrap().clr != state.current {
            continue;
        }
        for (m, k) in (1..=8).cartesian_product(1..=8) {
            let right = Coord(m, k);
            let mv = Move::new(left, right);
            if can_do_move(&state, mv, true, false) {
                moves.push(mv);
            }
        }
    }
    return moves;
}
fn can_be_attacked_in_one_move(state: &ChessState, c: Coord) -> Result<bool, String> {
    if !c.is_describing_position() {
        return Err("coord is out of bound".to_string());
    }
    if state.pieces_data.get(c).is_none() {
        return Err("No piece at that point".to_string());
    }
    let original_piece = state.pieces_data.get(c).unwrap();

    for (i, j) in (1..=8).cartesian_product(1..=8) {
        let piece_cord = Coord(i, j);
        let piece = state.pieces_data.get(piece_cord);
        if piece.is_none() {
            continue;
        }
        let piece = piece.unwrap();
        if piece.clr == original_piece.clr {
            continue;
        }
        let mv = Move::new(piece_cord, c);
        if can_do_move(state, mv, false, true) {
            return Ok(true);
        }
    }
    return Ok(false);
}

pub fn can_do_move(
    state: &ChessState,
    b: Move,
    consider_king_safety: bool,
    ignore_clr: bool,
) -> bool {
    return check_move(&state, b, consider_king_safety, ignore_clr).is_ok();
}

pub fn apply_move(state: &mut ChessState, b: Move) -> Result<(), String> {
    let effects = check_move(state, b, true, false)?;
    for el in effects {
        el(state);
    }
    return Ok(());
}
//if failed board won't be affected
pub fn check_move(
    state: &ChessState,
    b: Move,
    consider_king_safety: bool,
    ignore_clr: bool,
) -> Result<Vec<Effect>, String> {
    if !b.from.is_describing_position() || !b.to.is_describing_position() {
        return Err("One of the position in move are not on the board".to_string());
    }

    let piece = state.pieces_data.get(b.from);
    let maybe_piece_on_target = state.pieces_data.get(b.to);

    if piece.is_none() {
        return Err("Can't move non existing piece".to_string());
    }
    let piece = piece.unwrap();

    if !ignore_clr && piece.clr != state.current {
        return Err(format!("This is not a {} turn", piece.clr));
    }

    if let Some(piece_on_target) = maybe_piece_on_target {
        if piece_on_target.clr == piece.clr {
            return Err(format!(
                "Can't move {} piece into another {} piece",
                piece.clr, piece.clr
            ));
        }
    }

    let res = handle_castling(state, b);
    if let Some(res) = res {
        let mut effects = res;
        effects.push(Box::new(|a| a.current = a.current.reverse()));
        return Ok(effects);
    }

    let res = match piece.piece_kind {
        PieceKind::Pawn => handle_pawn(state, b),
        PieceKind::Knight => handle_knight(state, b),
        PieceKind::Bishiop => handle_bishop(state, b),
        PieceKind::Rook => handle_rook(state, b),
        PieceKind::Queen => handle_queen(state, b),
        PieceKind::King => handle_king(state, b),
    };
    if res.is_none() {
        return Err("Impossible move".to_string());
    }

    let mut effects = res.unwrap();
    let current_en_passant = state.en_passant;
    effects.push(Box::new(move |a| {
        if current_en_passant == a.en_passant {
            a.en_passant = None;
        }
    }));
    effects.push(Box::new(|a| a.current = a.current.reverse()));

    if consider_king_safety {
        let mut state_cp = state.clone();
        EffectHelper::apply_effects(&effects, &mut state_cp);
        let king_pos = find_king_pos(&state_cp, state.current);
        if can_be_attacked_in_one_move(&state_cp, king_pos).unwrap() {
            return Err("king could be attacked then".to_string());
        }
    }

    return Ok(effects);
}

pub fn is_lost_condition(state: &ChessState) -> bool {
    let king_pos = find_king_pos(state, state.current);
    return can_be_attacked_in_one_move(state, king_pos).unwrap()
        && get_available_moves(state).len() == 0;
}

pub fn find_king_pos(state: &ChessState, clr: Color) -> Coord {
    for (i, j) in (1..=8).cartesian_product(1..=8) {
        let c = Coord(i, j);
        let piece = state.pieces_data.get(c);
        if piece.is_none() {
            continue;
        }
        let piece = piece.unwrap();
        if piece.clr != clr {
            continue;
        }
        if piece.piece_kind != PieceKind::King {
            continue;
        }
        return c;
    }
    panic!("");
}
fn is_anything_in_the_way_excluding(
    state: &ChessState,
    start: Coord,
    sign: Coord,
    end: Coord,
) -> bool {
    let mut s = start + sign;
    while s != end {
        if state.pieces_data.get(s).is_some() {
            return true;
        }
        s = s + sign;
    }
    return false;
}

pub fn is_check(state: &ChessState) -> bool {
    return can_be_attacked_in_one_move(state, find_king_pos(state, state.current)).unwrap();
}
