use crate::chess_raw::*;

pub fn charify_piece(piece: Option<ColoredPiece>) -> char {
    if piece.is_none() {
        return ' ';
    }
    let piece = piece.unwrap();
    let chr = match piece.piece_kind {
        PieceKind::Pawn => 'p',
        PieceKind::Knight => 'n',
        PieceKind::Bishiop => 'b',
        PieceKind::Rook => 'r',
        PieceKind::Queen => 'q',
        PieceKind::King => 'k',
    };
    if piece.clr == Color::White {
        return chr.to_uppercase().next().unwrap();
    }
    return chr;
}
pub fn charify_color(clr: Color) -> char {
    return match clr {
        Color::Black => 'b',
        Color::White => 'w',
    };
}
fn serialize_fen_castling_av(a: [CastlingAvailability; 2]) -> String {
    let [white, black] = a;
    if !white.king_side && !white.queen_side && !black.king_side && !white.king_side {
        return "-".to_string();
    }
    let mut builder = String::new();
    if white.king_side {
        builder += "K";
    }
    if white.queen_side {
        builder += "Q";
    }
    if black.king_side {
        builder += "k";
    }
    if black.queen_side {
        builder += "q";
    }
    return builder;
}

fn serialize_fen_placement(s: &ChessState) -> String {
    let mut builder = String::new();

    for y in (1..=8).rev() {
        let mut counter = 0;
        for x in 1..=8 {
            let c = Coord(x, y);
            match s.pieces_data.get(c) {
                Some(p) => {
                    if counter > 0 {
                        builder += &counter.to_string();
                        counter = 0;
                    }
                    builder += &charify_piece(Some(p)).to_string();
                }
                None => counter += 1,
            }
        }
        if counter > 0 {
            builder += &counter.to_string();
        }
        if y != 1 {
            builder += "/";
        }
    }
    return builder;
}
pub fn serialize_to_fen(s: &ChessState) -> String {
    let placement = serialize_fen_placement(s);
    let clr = charify_color(s.current);
    let castling_av = serialize_fen_castling_av(s.castling);
    let en_passant = s
        .en_passant
        .map(|e| format!("{e}"))
        .unwrap_or("-".to_string());
    let halfmove = 0;
    let fullmove = 1;
    return format!("{placement} {clr} {castling_av} {en_passant} {halfmove} {fullmove}");
}
