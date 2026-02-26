from typing import List

class ExampleService:
    """
    Business logic for example operations.
    """
    
    def __init__(self) -> None:
        # Initialize any resources needed (e.g., db sessions, clients)
        pass

    async def get_items(self) -> List[str]:
        """
        Mock method to retrieve items.
        
        Returns:
            List[str]: A list of example items.
        """
        return ["item1", "item2", "item3"]

def get_example_service() -> ExampleService:
    """
    Dependency injection provider for ExampleService.
    """
    return ExampleService()
