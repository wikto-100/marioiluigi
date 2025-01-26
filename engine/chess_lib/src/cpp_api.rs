use crate::api_template;
use std::convert::identity;
use std::ffi::{CStr, CString};
use std::os::raw::c_char;
use std::sync::Mutex;

lazy_static::lazy_static! {
    static ref Api_Error: Mutex<Option<String>> = Mutex::new(None);
}

fn set_error(s: Option<String>) {
    *Api_Error.lock().unwrap() = s;
}

#[no_mangle]
pub extern "C" fn chess_lib_get_error() -> *const c_char {
    let mut guard = Api_Error.lock().unwrap();
    if let Some(v) = &*guard {
        let r = CString::new(v.as_str()).unwrap().into_raw();
        *guard = None;
        return r;
    }
    return std::ptr::null();
}

fn panic_if_null(ptr: *const c_char) {
    if ptr.is_null() {
        panic!("null pointer given as an argument");
    }
}

fn register_error_or<T, TRes: Default>(a: Result<T, String>, f: impl FnOnce(T) -> TRes) -> TRes {
    if let Err(er) = a {
        set_error(Some(er));
        return TRes::default();
    }
    return f(a.unwrap());
}

fn register_erorr_or_on_ptr<T>(
    a: Result<T, String>,
    f: impl FnOnce(T) -> *const c_char,
) -> *const c_char {
    if let Err(er) = a {
        set_error(Some(er));
        return std::ptr::null();
    }
    return f(a.unwrap());
}

fn wrap_simple_bool_return(
    fen_ptr: *const c_char,
    f: impl Fn(&str) -> Result<bool, String>,
) -> bool {
    panic_if_null(fen_ptr);
    let board_fen = unsafe { CStr::from_ptr(fen_ptr) }.to_str().unwrap();
    let maybe_ans = f(board_fen);
    return register_error_or(maybe_ans, identity);
}

#[no_mangle]
pub unsafe extern "C" fn chess_lib_free_str(ptr: *mut c_char) {
    drop(CString::from_raw(ptr));
}

#[no_mangle]
pub extern "C" fn chess_lib_get_available_moves(fen_ptr: *const c_char) -> *const c_char {
    panic_if_null(fen_ptr);
    let fen = unsafe { CStr::from_ptr(fen_ptr) }.to_str().unwrap();
    let moves = api_template::internal_get_available_moves(fen);

    return register_erorr_or_on_ptr(moves, |moves| {
        let r = moves.iter().fold("".to_string(), |a, b| a + b + "\n");
        return CString::new(r).unwrap().into_raw();
    });
}
#[no_mangle]
pub extern "C" fn chess_lib_can_do_move(fen_ptr: *const c_char, mv_ptr: *const c_char) -> bool {
    panic_if_null(fen_ptr);
    panic_if_null(mv_ptr);

    let board_fen = unsafe { CStr::from_ptr(fen_ptr) }.to_str().unwrap();
    let mv = unsafe { CStr::from_ptr(mv_ptr) }.to_str().unwrap();
    let maybe_ans = api_template::internal_can_do_move(board_fen, mv);

    return register_error_or(maybe_ans, identity);
}

#[no_mangle]
pub extern "C" fn chess_lib_get_applied_move(
    fen_ptr: *const c_char,
    mv_ptr: *const c_char,
) -> *const c_char {
    panic_if_null(fen_ptr);
    panic_if_null(mv_ptr);

    let board_fen = unsafe { CStr::from_ptr(fen_ptr) }.to_str().unwrap();
    let mv = unsafe { CStr::from_ptr(mv_ptr) }.to_str().unwrap();
    let maybe_ans = api_template::internal_get_applied_move(board_fen, mv);

    return register_erorr_or_on_ptr(maybe_ans, |ans| {
        return CString::new(ans).unwrap().into_raw();
    });
}

#[no_mangle]
pub extern "C" fn chess_lib_is_white_turn(fen_ptr: *const c_char) -> bool {
    return wrap_simple_bool_return(fen_ptr, api_template::internal_is_white_turn);
}
#[no_mangle]
pub extern "C" fn chess_lib_is_lost_condition(fen_ptr: *const c_char) -> bool {
    return wrap_simple_bool_return(fen_ptr, api_template::internal_is_lost_condition);
}

#[no_mangle]
pub extern "C" fn chess_lib_is_check(fen_ptr: *const c_char) -> bool {
    return wrap_simple_bool_return(fen_ptr, api_template::internal_is_check);
}
#[no_mangle]
pub extern "C" fn chess_lib_is_pat(fen_ptr: *const c_char) -> bool {
    return wrap_simple_bool_return(fen_ptr, api_template::internal_is_pat);
}
