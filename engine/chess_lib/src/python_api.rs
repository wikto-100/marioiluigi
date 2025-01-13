use std::sync::Arc;

use pyo3::{exceptions::PyValueError, prelude::*};

use crate::api_template;

fn convert_to_py_result<T>(a: Result<T, String>) -> PyResult<T> {
    return a.map_err(|e| PyErr::new::<PyValueError, _>(e));
}

#[pyfunction]
pub fn get_available_moves(board_fen: &str) -> PyResult<Vec<String>> {
    return convert_to_py_result(api_template::internal_get_available_moves(board_fen));
}

#[pyfunction]
pub fn can_do_move(board_fen: &str, mv: &str) -> PyResult<bool> {
    return convert_to_py_result(api_template::internal_can_do_move(board_fen, mv));
}
#[pyfunction]
pub fn get_applied_move(board_fen: &str, mv: &str) -> PyResult<String> {
    return convert_to_py_result(api_template::internal_get_applied_move(board_fen, mv));
}
#[pyfunction]
pub fn is_white_turn(board_fen: &str) -> PyResult<bool> {
    return convert_to_py_result(api_template::internal_is_white_turn(board_fen));
}
#[pyfunction]
pub fn is_lost_condition(board_fen: &str) -> PyResult<bool> {
    return convert_to_py_result(api_template::internal_is_lost_condition(board_fen));
}
#[pyfunction]
pub fn is_check(board_fen: &str) -> PyResult<bool> {
    return convert_to_py_result(api_template::internal_is_check(board_fen));
}
#[pyfunction]
pub fn is_pat(board_fen: &str) -> PyResult<bool> {
    return convert_to_py_result(api_template::internal_is_pat(board_fen));
}

#[pymodule]
fn chess_lib(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(get_available_moves, m)?)?;
    m.add_function(wrap_pyfunction!(can_do_move, m)?)?;
    m.add_function(wrap_pyfunction!(get_applied_move, m)?)?;
    m.add_function(wrap_pyfunction!(is_white_turn, m)?)?;
    m.add_function(wrap_pyfunction!(is_lost_condition, m)?)?;
    m.add_function(wrap_pyfunction!(is_check, m)?)?;
    m.add_function(wrap_pyfunction!(is_pat, m)?)?;
    Ok(())
}
