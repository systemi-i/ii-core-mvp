# src/models/typed_edge.py

from typing import Optional, Literal, List
from pydantic import BaseModel


class TypedEdge(BaseModel):
    from_node: str
    to_node: str
    type: Literal[
        "dependency",
        "temporal",
        "conditional",
        "override",
        "semantic_link",
        "actor_constraint",
        "feedback_loop"
    ]

    # Optional shared metadata
    label: Optional[str] = None
    tags: Optional[List[str]] = []

    # Conditional edge fields
    condition: Optional[str] = None

    # Temporal edge fields
    relation: Optional[Literal["must_finish_before", "within_days", "no_earlier_than"]] = None
    rationale: Optional[str] = None

    # Override edge fields
    override_id: Optional[str] = None
    trigger_condition: Optional[str] = None
    override_action: Optional[str] = None

    # Semantic edge field
    tag: Optional[str] = None  # For semantic links, e.g. "#Permit"

    # Actor constraint field
    required_actor: Optional[str] = None

    # Provenance fields (for AI-generated edges, future use)
    generated_by: Optional[str] = None
    confidence: Optional[float] = None
