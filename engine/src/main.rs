use std::{
    io::{stdin, Read},
    process::exit,
    thread::current,
};
mod chess_raw;
mod parser;
use derive_new::new;
mod logic;
mod simple_sim;

fn main() {
    simple_sim::sim();
}
