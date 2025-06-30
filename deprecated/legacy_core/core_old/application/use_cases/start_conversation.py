# Use case: Start Conversation
class StartConversationUseCase:
    """Use case for starting a new conversation."""
    def __init__(self, conversation_service):
        self.conversation_service = conversation_service

    async def execute(self, child_id: str, initial_message: str):
        return await self.conversation_service.start_conversation(child_id, initial_message) 