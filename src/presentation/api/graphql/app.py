from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter

from .schema import schema


def create_graphql_app() -> FastAPI:
    """Create FastAPI app with GraphQL endpoint"""
    app = FastAPI(title="AI Teddy Bear GraphQL API")

    # Create GraphQL router
    graphql_app = GraphQLRouter(
        schema, graphiql=True, path="/graphql"
    )  # Enable GraphiQL interface

    # Include GraphQL router
    app.include_router(graphql_app, prefix="/api/v1")

    # Health check endpoint
    @app.get("/health")
    async def health_check():
        return {"status": "healthy", "api": "graphql"}

    # CORS middleware
    from fastapi.middleware.cors import CORSMiddleware

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return app


app = create_graphql_app()
