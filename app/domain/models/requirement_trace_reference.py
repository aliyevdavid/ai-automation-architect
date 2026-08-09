from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RequirementTraceReference:
    """Reference to one structured project-requirement field."""

    field_path: str

    def __post_init__(self) -> None:
        if not isinstance(self.field_path, str):
            raise TypeError("field_path must be a string.")
        if not self.field_path.strip():
            raise ValueError("field_path must not be blank.")
