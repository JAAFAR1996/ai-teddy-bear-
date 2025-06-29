#!/usr/bin/env python3
"""
🚀 AI Teddy Bear API Launcher
Simple, clean entry point without over-engineering
"""

import argparse
import logging
import uvicorn

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    """Simple API server launcher"""
    parser = argparse.ArgumentParser(
        description="AI Teddy Bear API Server",
        epilog="Example: python -m core.main --reload --port 8080"
    )
    
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload for development")
    parser.add_argument("--workers", type=int, default=1, help="Number of worker processes")
    
    args = parser.parse_args()
    
    # Log startup
    logging.info(f"🚀 Starting AI Teddy Bear API on {args.host}:{args.port}")
    
    # Run the server
    if args.reload or args.workers == 1:
        # Development mode or single worker
        uvicorn.run(
            "core.api.production_api:app",  # Point to the actual API app
            host=args.host,
            port=args.port,
            reload=args.reload,
            log_level="info"
        )
    else:
        # Production mode with multiple workers
        uvicorn.run(
            "core.api.production_api:app",
            host=args.host,
            port=args.port,
            workers=args.workers,
            log_level="info",
            access_log=True
        )

if __name__ == "__main__":
    main()
