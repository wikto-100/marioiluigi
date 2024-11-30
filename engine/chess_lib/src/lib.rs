pub mod api_template;
pub mod chess_raw;
pub mod logic;
pub mod parser;

#[cfg(feature = "cpp_api")]
mod cpp_api;
#[cfg(feature = "python_api")]
pub mod python_api;

pub mod serializer;
mod test;
use derive_new::new;

#[no_mangle]
pub extern "C" fn test2() -> i32 {
    69
}
