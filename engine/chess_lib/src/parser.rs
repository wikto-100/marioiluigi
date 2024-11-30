use std::ops::Add;

use derive_new::new;

use crate::chess_raw::*;

pub fn parse_piece_repr(t: char) -> Option<ColoredPiece> {
    return match t {
        'P' => Some(ColoredPiece::new(PieceKind::Pawn, Color::White)),
        'N' => Some(ColoredPiece::new(PieceKind::Knight, Color::White)),
        'B' => Some(ColoredPiece::new(PieceKind::Bishiop, Color::White)),
        'R' => Some(ColoredPiece::new(PieceKind::Rook, Color::White)),
        'Q' => Some(ColoredPiece::new(PieceKind::Queen, Color::White)),
        'K' => Some(ColoredPiece::new(PieceKind::King, Color::White)),

        'p' => Some(ColoredPiece::new(PieceKind::Pawn, Color::Black)),
        'n' => Some(ColoredPiece::new(PieceKind::Knight, Color::Black)),
        'b' => Some(ColoredPiece::new(PieceKind::Bishiop, Color::Black)),
        'r' => Some(ColoredPiece::new(PieceKind::Rook, Color::Black)),
        'q' => Some(ColoredPiece::new(PieceKind::Queen, Color::Black)),
        'k' => Some(ColoredPiece::new(PieceKind::King, Color::Black)),
        _ => None,
    };
}

fn try_parse_fen_board(s: &str) -> Result<BoardPiecesState, String> {
    let mut builder: Vec<Vec<Option<ColoredPiece>>> =
        (0..=7).map(|_| (0..=7).map(|_| None).collect()).collect();
    let mut it = 0;
    let mut last_seen_slash = 0;
    let chars: Vec<_> = s.chars().collect();
    for (&c, i) in chars.iter().zip((0..chars.len())) {
        if it % 8 == 0 && last_seen_slash < it / 8 {
            last_seen_slash = it / 8;
            if c == '/' {
                continue;
            } else {
                return Err(format!("Expected \"/\" at {i} index instead found {}", c));
            }
        }
        let as_number_maybe = c.to_string().parse().ok();
        if let Some(number) = as_number_maybe {
            if (8 - (it % 8)) < number {
                return Err(format!("number overlflows at index {i}"));
            }
            it += number;
            continue;
        }
        let as_piece_maybe = parse_piece_repr(c);
        if let Some(as_piece) = as_piece_maybe {
            builder[it / 8][it % 8] = Some(as_piece);
            it += 1;
            continue;
        }
        return Err(format!("Unknown/unexpected symbol as a piece at {i} index",));
    }
    return Ok(BoardPiecesState::new(builder).unwrap());
}
fn try_parse_color(s: &str) -> Result<Color, String> {
    match s {
        "w" => Ok(Color::White),
        "b" => Ok(Color::Black),
        _ => Err("Unknown letter color".to_string()),
    }
}

//return is white/black
fn try_parse_castling(s: &str) -> Result<[CastlingAvailability; 2], String> {
    let mut white = CastlingAvailability::default();
    let mut black = CastlingAvailability::default();

    if s.len() > 4 {
        return Err("Castling data is too long".to_string());
    }

    if s == "-" {
        return Ok([CastlingAvailability::NOPE, CastlingAvailability::NOPE]);
    }

    let mut amount = 0;
    if s.contains("K") {
        white.kingSide = true;
        amount += 1;
    }
    if s.contains("Q") {
        white.queenSide = true;
        amount += 1;
    }
    if s.contains("k") {
        black.kingSide = true;
        amount += 1;
    }
    if s.contains("q") {
        black.queenSide = true;
        amount += 1;
    }
    if amount < s.len() {
        return Err("Castling data contains illegal symbol".to_string());
    }

    return Ok([white, black]);
}

pub fn parse_fen(s: &str) -> Result<ChessState, String> {
    let afterSplit: Vec<&str> = s.split(" ").collect();
    if let &[s_pieces, s_color, s_castling, s_en_passant, s_halfmove_clock, s_fullmove_number] =
        afterSplit.as_slice()
    {
        let pieces = try_parse_fen_board(s_pieces)?;
        let color = try_parse_color(s_color)?;
        let castling = try_parse_castling(s_castling)?;
        let en_passant = try_parse_optional_coord(s_en_passant)
            .map_err(|e| format!("during parsing en_passant:{e}"))?;
        return Ok(ChessState::new(pieces, color, castling, en_passant));
    }
    return Err("Incorrect format, fen should be 6 strings splited by space".to_string());
}

fn try_parse_optional_coord(coord: &str) -> Result<Option<Coord>, String> {
    if coord == "-" {
        return Ok(None);
    }
    let [a, b]: [char; 2] = coord
        .chars()
        .collect::<Vec<_>>()
        .try_into()
        .map_err(|e| "Coord contains more or less than two chars".to_string())?;

    let x = ((a as i32) - ('a' as i32)) + 1;
    let y = (b as i32) - ('0' as i32);
    return Ok(Some(Coord(x, y)));
}
fn try_parse_coord(coord: &str) -> Result<Coord, String> {
    return try_parse_optional_coord(coord)
        .and_then(|e| e.ok_or("\"-\" value not allowed".to_string()));
}
pub fn parse_move(a: &str) -> Result<Move, String> {
    if a.len() != 4 && a.len() != 5 {
        return Err("move should have 4 len or len 5".to_string());
    }
    let left = try_parse_coord(&a[..2])?; //todo wrap
    let right = try_parse_coord(&a[2..4])?;
    if a.len() == 5 {
        let chr = a.chars().nth(4).unwrap();

        if chr == 'c' {
            return Ok(Move::new_with(
                left,
                right,
                Some(AdditionalMoveData::Castling),
            ));
        }

        let promotio_kind = parse_piece_repr(chr)
            .ok_or_else(|| "promotion data includes wrong piece symbol".to_string())?;
        return Ok(Move::new_with(
            left,
            right,
            Some(AdditionalMoveData::Promotion(promotio_kind.pieceKind)),
        ));
    }

    return Ok(Move::new(left, right));
}