"""
Child Family Domain Service

Domain service for child family and grouping business logic.
"""

import logging
from typing import Any, Dict, List, Optional

from src.core.domain.entities.child import Child


class ChildFamilyDomainService:
    """Domain service for child family business logic"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def group_children_by_family(self, children: List[Child]) -> Dict[str, List[Child]]:
        """Group children by family code"""
        family_groups = {}

        for child in children:
            family_code = getattr(child, "family_code", None) or "unknown"

            if family_code not in family_groups:
                family_groups[family_code] = []

            family_groups[family_code].append(child)

        return family_groups

    def find_siblings(self, child: Child, all_children: List[Child]) -> List[Child]:
        """Find siblings of a child"""
        if not hasattr(child, "family_code") or not child.family_code:
            return []

        siblings = []
        for other_child in all_children:
            if (
                other_child.id != child.id
                and hasattr(other_child, "family_code")
                and other_child.family_code == child.family_code
            ):
                siblings.append(other_child)

        return siblings
