use std::{
    collections::HashSet,
    io::{stdin, stdout, Write},
    process::exit,
    time::Instant,
};

use chess_lib::{chess_raw::ChessState, serializer};

use crate::{logic, parser};

pub fn sim(s: &mut ChessState) {
    loop {
        let raw = s.pieces_data.get_ref();
        for i in 0..8 {
            print!("{} ", 8 - i);
            for j in 0..8 {
                print!("{}", serializer::charify_piece(raw[i][j]));
            }
            println!("");
        }
        println!("");
        print!("  ");
        for i in 0..8 {
            print!("{}", (i + ('a' as u8)) as char);
        }
        println!("");
        println!("{}", serializer::serialize_to_fen(&s));
        println!("en passant {:?}", s.en_passant);
        println!("white av passant {:?}", s.castling[0]);
        println!("black av passant {:?}", s.castling[1]);

        if logic::is_lost_condition(&s) {
            println!("you lost, {} won", s.current.reverse());
            exit(0);
        }

        let mut buf: String = String::new();
        loop {
            print!(">");
            stdout().flush().unwrap();
            buf.clear();
            stdin().read_line(&mut buf).unwrap();
            if buf.trim() == "skip" {
                s.current = s.current.reverse();
                continue;
            }
            if buf.trim() == "list" {
                let t = Instant::now();
                let moves = logic::get_available_moves(&s);
                let fast = (Instant::now() - t).as_micros();
                println!("fast took {}", fast);

                let t = Instant::now();
                let slow_moves = logic::get_available_moves_slow(&s);
                let slow = (Instant::now() - t).as_micros();
                println!("slow took {}", slow);

                println!("gain {}", slow as f32 / fast as f32);

                let mut possible: HashSet<_> = HashSet::from_iter(moves.into_iter());
                let mut possible_slow: HashSet<_> =
                    HashSet::from_iter(logic::get_available_moves_slow(&s).into_iter());

                if possible != possible_slow {
                    println!("NOT THE SAMEE");
                    println!("{} {}", possible.len(), possible_slow.len());
                    for el in &possible_slow {
                        println!("{el}");
                    }
                    println!("vs");
                    for el in &possible {
                        println!("{el}");
                    }
                    println!("end");
                    
                }

                for el in possible {
                    println!("{el}");
                }

                continue;
            }
            if buf.trim() == "redraw" {
                break;
            }
            let maybe_mv = parser::parse_move(buf.trim());
            if let Err(r) = maybe_mv {
                println!("Invalid move/or special syntax : {r}");
                continue;
            }
            let mv = maybe_mv.unwrap();
            let res = logic::apply_move(s, mv);
            if let Err(r) = res {
                println!("{}", r);
                continue;
            }
            break;
        }
    }
}
