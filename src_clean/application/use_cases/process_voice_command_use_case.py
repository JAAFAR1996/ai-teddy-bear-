"""
Use Case - Application Layer
Orchestrates domain services and infrastructure
"""

class RegisterChildUseCase:
    """Use case for registering a new child"""
    
    def __init__(self, child_repository, domain_service):
        self.child_repository = child_repository
        self.domain_service = domain_service
        
    async def execute(self, child_data: dict) -> str:
        """Execute the use case"""
        # 1. Validate with domain service
        # 2. Create child entity
        # 3. Save via repository
        # 4. Publish domain event
        return "child_id"
