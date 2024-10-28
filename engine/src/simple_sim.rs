use std::{io::stdin, process::exit};

use crate::{logic, parser};

pub fn sim() {
    let mut buffer = String::new();
    std::io::stdin().read_line(&mut buffer);

    let p = parser::parse_fen(&buffer);
    if let Err(er) = p {
        eprintln!("{er}");
        exit(1);
    }
    if let Ok(mut s) = p {
        loop {
            let raw = s.pieces_data.get_ref();
            for i in 0..8 {
                print!("{} ", 8 - i);
                for j in 0..8 {
                    print!("{}", parser::stringify_piece(raw[i][j]));
                }
                println!("");
            }
            println!("");
            print!("  ");
            for i in 0..8 {
                print!("{}", (i + ('a' as u8)) as char);
            }
            println!("");

            let mut buf: String = String::new();
            stdin().read_line(&mut buf);
            if buf.trim() == "F" {
                s.current = s.current.reverse();
                continue;
            }
            let mv = parser::parse_move(buf.trim()).unwrap();
            let res = logic::apply_move(&mut s, mv);
            if let Err(r) = res {
                println!("{}", r);
            }
        }
    }
}
