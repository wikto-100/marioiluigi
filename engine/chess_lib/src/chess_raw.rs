use std::{
    fmt::{write, Display},
    ops::{Add, Mul, Sub},
};

use derive_new::new;

use crate::serializer;

#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
#[repr(usize)]
pub enum PieceKind {
    Pawn,
    Knight,
    Bishiop,
    Rook,
    Queen,
    King,
}
#[derive(Debug, Clone, Copy, PartialEq, Eq, strum_macros::Display)]
#[repr(usize)]
pub enum Color {
    Black,
    White,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, derive_new::new)]
pub struct ColoredPiece {
    pub piece_kind: PieceKind,
    pub clr: Color,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub struct Coord(pub i32, pub i32);
#[derive(Debug, Clone)]
pub struct BoardPiecesState {
    v: Vec<Vec<Option<ColoredPiece>>>,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum CastlingType {
    KingSide,
    QueenSide,
}
#[derive(Debug, Clone, Copy, PartialEq, Eq, Default)]
pub struct CastlingAvailability {
    pub kingSide: bool,
    pub queenSide: bool,
}

//todo: add halfmove clock
//todo: add fullmove number
#[derive(Debug, Clone, new)]
pub struct ChessState {
    pub pieces_data: BoardPiecesState,
    pub current: Color,

    //white then black
    pub castling: [CastlingAvailability; 2],
    pub en_passant: Option<Coord>,
}
pub type Effect = Box<dyn Fn(&mut ChessState)>;
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub struct Move {
    pub from: Coord,
    pub to: Coord,
    pub additional: Option<AdditionalMoveData>,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub enum AdditionalMoveData {
    Promotion(PieceKind),
    Castling,
}

impl Display for Move {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self.additional {
            None => write!(f, "{}{}", self.from, self.to),
            Some(AdditionalMoveData::Castling) => write!(f, "{}{}c", self.from, self.to),
            Some(AdditionalMoveData::Promotion(kind)) => write!(
                f,
                "{}{}{}",
                self.from,
                self.to,
                serializer::charify_piece(Some(ColoredPiece::new(kind, Color::White)))
            ),
        }
    }
}

impl Color {
    pub fn reverse(&self) -> Color {
        match self {
            Color::Black => Color::White,
            Color::White => Color::Black,
        }
    }
    pub fn repr(&self) -> usize {
        match self {
            Color::Black => 1,
            Color::White => 0,
        }
    }
}

impl Coord {
    pub const LEFT: Coord = Coord::make_x(-1);
    pub const RIGHT: Coord = Coord::make_x(1);

    pub const UP: Coord = Coord::make_y(1);
    pub const UP_TWICE: Coord = Coord::make_y(2);
    pub const DOWN: Coord = Coord::make_y(-1);
    pub const DOWN_TWICE: Coord = Coord::make_y(-2);

    pub const UP_LEFT: Coord = Coord(-1, 1);
    pub const UP_RIGHT: Coord = Coord(1, 1);

    pub const DOWN_LEFT: Coord = Coord(-1, -1);
    pub const DOWN_RIGHT: Coord = Coord(1, -1);

    pub const BlACK_FIRST_ROW: i32 = 8;
    pub const BLACK_SECOND_ROW: i32 = 7;
    pub const WHITE_FIRST_ROW: i32 = 1;
    pub const WHITE_SECOND_ROW: i32 = 2;

    pub const fn point_of_view_dir(&self, c: Color) -> Coord {
        match c {
            Color::Black => Coord(self.0, -self.1),
            Color::White => *self,
        }
    }
    pub fn is_describing_position(self) -> bool {
        return self.0 >= 1 && self.0 <= 8 && self.1 >= 1 && self.1 <= 8;
    }
    pub fn row_point_of_view(u: i32, c: Color) -> i32 {
        match c {
            Color::Black => 9 - u,
            Color::White => u,
        }
    }
    pub const fn make_x(u: i32) -> Coord {
        return Coord(u, 0);
    }
    pub const fn make_y(u: i32) -> Coord {
        return Coord(0, u);
    }
    pub fn x(&self) -> i32 {
        return self.0;
    }
    pub fn y(&self) -> i32 {
        return self.1;
    }
    pub fn map(&self, f: impl Fn(i32) -> i32) -> Coord {
        return Coord(f(self.x()), f(self.y()));
    }
    pub fn piecewise_sign(&self) -> Coord {
        return self.map(i32::signum);
    }
    pub fn piecewise_abs(&self) -> Coord {
        return self.map(i32::abs);
    }
}
impl Add for Coord {
    type Output = Coord;

    fn add(self, rhs: Self) -> Self::Output {
        return Coord(self.0 + rhs.0, self.1 + rhs.1);
    }
}
impl Sub for Coord {
    type Output = Coord;

    fn sub(self, rhs: Self) -> Self::Output {
        return Coord(self.0 - rhs.0, self.1 - rhs.1);
    }
}
impl Mul<i32> for Coord {
    type Output = Coord;

    fn mul(self, rhs: i32) -> Self::Output {
        return Coord(self.0 * rhs, self.1 * rhs);
    }
}
impl Display for Coord {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        if Coord::is_describing_position(*self) {
            let x = ((self.x() - 1) as u8 + 'a' as u8) as char;
            let y = self.y().to_string();
            return write!(f, "{x}{y}");
        }
        write!(f, "Corrupted({},{})", self.x(), self.y())
    }
}

impl BoardPiecesState {
    pub fn new(v: Vec<Vec<Option<ColoredPiece>>>) -> Option<BoardPiecesState> {
        if (v.len() == 8 && v.iter().all(|a| a.len() == 8)) {
            return Some(Self { v });
        }
        return None;
    }
    pub fn get_ref(&self) -> &Vec<Vec<Option<ColoredPiece>>> {
        return &self.v;
    }
    pub fn translate_to_raw(c: Coord) -> Option<(usize, usize)> {
        if !Coord::is_describing_position(c) {
            return None;
        }
        return Some(((8 - c.1) as usize, (c.0 - 1) as usize));
    }
    pub fn get(&self, c: Coord) -> Option<ColoredPiece> {
        let (a, b) = Self::translate_to_raw(c).unwrap();
        return self.v[a][b];
    }
    pub fn set(&mut self, c: Coord, p: Option<ColoredPiece>) {
        let (a, b) = Self::translate_to_raw(c).unwrap();
        self.v[a][b] = p;
    }
}
pub struct EffectHelper {}
impl EffectHelper {
    pub fn get_change(c: Coord, p: Option<ColoredPiece>) -> Effect {
        return Box::new(move |s| s.pieces_data.set(c, p));
    }
    pub fn apply_effects(effects: &Vec<Effect>, state: &mut ChessState) {
        for ef in effects {
            ef(state);
        }
    }
    pub fn get_unmark_castling(c: Color) -> Effect {
        return Box::new(move |s| s.castling[c.repr()] = CastlingAvailability::NOPE);
    }
}
impl Move {
    pub fn new(from: Coord, to: Coord) -> Move {
        return Move {
            from,
            to,
            additional: None,
        };
    }
    pub fn new_with(from: Coord, to: Coord, additional: Option<AdditionalMoveData>) -> Move {
        return Move {
            from,
            to,
            additional,
        };
    }
}

impl CastlingAvailability {
    pub const NOPE: CastlingAvailability = CastlingAvailability {
        kingSide: false,
        queenSide: false,
    };
}
