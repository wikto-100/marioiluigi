from .chess_lib import *

__doc__ = chess_lib.__doc__ # type: ignore
if hasattr(chess_lib, "__all__"): # type: ignore
    __all__ = chess_lib.__all__ # type: ignore