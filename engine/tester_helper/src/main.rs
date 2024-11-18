use chess_lib;
use chess_lib::*;
use std::{env::args, fs, process::exit};
mod simple_sim;

fn main() {
    let mut args: Vec<_> = args().collect();
    if args.len() == 1 {
        let mut buffer = String::new();
        std::io::stdin().read_line(&mut buffer).unwrap();
        args.push(buffer);
    }
    let strg = fs::read_to_string(args[1].trim()).unwrap();
    let p = parser::parse_fen(&strg);
    if let Err(er) = p {
        eprintln!("{er}");
        exit(1);
    }
    simple_sim::sim(&mut p.unwrap());
}
