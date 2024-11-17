use crate::chess_raw::*;

fn raw_move(state: &mut ChessState, b: Move) {
    state.pieces_data.set(b.1, state.pieces_data.get(b.0));
    state.pieces_data.set(b.0, None);
}

fn handle_pawn(state: &mut ChessState, b: Move) -> Result<bool, String> {
    let us = state.pieces_data.get(b.0).unwrap();
    let maybe_piece_on_target = state.pieces_data.get(b.1);

    let start_pos = b.0;
    let end_pos = b.1;

    //--- enemy ---

    if maybe_piece_on_target.is_some() {
        if end_pos == start_pos + Coord::UP_LEFT || end_pos == start_pos + Coord::UP_RIGHT {
            raw_move(state, b);
            return Ok(true);
        }
        return Ok(false);
    }

    //-- maybe en-passant --

    let real_up = Coord::point_of_view_dir(&Coord::UP, us.clr);
    let real_down = Coord::point_of_view_dir(&Coord::DOWN, us.clr);

    if Some(end_pos) == state.enPassant {
        let enemy_pos = end_pos + real_down;

        let should_be_pawn = state.pieces_data.get(enemy_pos);
        if should_be_pawn.map(|e| e.pieceKind) != Some(PieceKind::Pawn) {
            return Err("En passant data is incorrect".to_string());
        }
        if end_pos == start_pos + Coord::UP_RIGHT || end_pos == start_pos + Coord::UP_RIGHT {
            raw_move(state, b);
            state.pieces_data.set(enemy_pos, None);
            return Ok(true);
        }
        return Ok(false);
    }

    //--- no enemy on target ---

    //we can't move 2 up even if its the first pawn move IF there's something block one block above
    let is_something_one_up = start_pos.y() != 8 && state.pieces_data.get(b.0 + real_up).is_some();

    let in_second_row = start_pos.y() == Coord::row_point_of_view(Coord::WHITE_SECOND_ROW, us.clr);
    println!("{}", in_second_row);
    let is_one_up = end_pos == start_pos + real_up;
    let is_two_up = end_pos == start_pos + real_up * 2;

    if (in_second_row && is_two_up && !is_something_one_up) || is_one_up {
        raw_move(state, b);
        return Ok(true);
    } else {
        return Ok(false);
    }
}

pub fn handle_rook(state: &mut ChessState, b: Move) -> Result<bool, String> {
    let (from, to) = (b.0, b.1);

    if from.x() != to.x() && from.y() != to.y() {
        return Ok(false);
    }

    let sign = (to - from).piecewise_sign();
    if is_anything_in_the_way_excluding(state, from, sign, to) {
        return Ok(false);
    }
    raw_move(state, b);
    return Ok(true);
}
pub fn handle_knight(state: &mut ChessState, b: Move) -> Result<bool, String> {
    let (from, to) = (b.0, b.1);
    let dif = to - from;

    if dif.x().abs() != dif.y().abs() {
        return Ok(false);
    }
    let sign = dif.piecewise_sign();
    if is_anything_in_the_way_excluding(state, from, sign, to) {
        return Ok(false);
    }

    raw_move(state, b);
    return Ok(true);
}
pub fn handle_queen(state: &mut ChessState, b: Move) -> Result<bool, String> {
    let (from, to) = (b.0, b.1);
    let dif = to - from;
    if (from.x() != to.x() && from.y() != to.y()) && dif.x().abs() != dif.y().abs() {
        return Ok(false);
    }
    let sign = dif.piecewise_sign();
    if is_anything_in_the_way_excluding(state, from, sign, to) {
        return Ok(false);
    }
    raw_move(state, b);
    return Ok(true);
}

pub fn handle_bishop(state: &mut ChessState, b: Move) -> Result<bool, String> {
    let (from, to) = (b.1, b.0);
    let dif = to - from;
    let abs_dif = dif.piecewise_abs();
    if (abs_dif.x() == 2 && abs_dif.y() == 1) || (abs_dif.x() == 1 && abs_dif.y() == 2) {
        raw_move(state, b);
        return Ok(true);
    }
    return Ok(false);
}

//if failed board won't be affected
pub fn apply_move(state: &mut ChessState, b: Move) -> Result<(), String> {
    if !b.0.is_describing_position() || !b.1.is_describing_position() {
        return Err("One of the position in move are not on the board".to_string());
    }

    let piece = state.pieces_data.get(b.0);
    let maybe_piece_on_target = state.pieces_data.get(b.1);

    if piece.is_none() {
        return Err("Can't move non existing piece".to_string());
    }
    let piece = piece.unwrap();

    if piece.clr != state.current {
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

    let res = match piece.pieceKind {
        PieceKind::Pawn => handle_pawn(state, b).unwrap(),
        PieceKind::Knight => handle_knight(state, b).unwrap(),
        PieceKind::Bishiop => handle_bishop(state, b).unwrap(),
        PieceKind::Rook => handle_rook(state, b).unwrap(),
        PieceKind::Queen => handle_queen(state, b).unwrap(),
        PieceKind::King => todo!(),
    };
    if !res {
        return Err("Impossible move".to_string());
    }
    state.current = state.current.reverse();

    return Ok(());
}
pub fn is_anything_in_the_way_excluding(
    state: &mut ChessState,
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
