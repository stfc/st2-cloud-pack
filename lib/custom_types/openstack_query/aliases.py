from typing import Optional, Callable, Any, Dict

PresetKwargs = Dict[str, Any]

MappingFunc = Callable[..., bool]
FilterFunc = Callable[[Any], bool]

MappingReturn = Optional[MappingFunc]
