import asyncio
import os
from taskcraft.core.runtime import AgentRuntime
from taskcraft.state.persistence import SQLiteStateManager
from taskcraft.governance.policy import PolicyEngine
from taskcraft.llm.client import GeminiClient

# --- STEP 1: Define your custom tools ---
async def check_stock_price(ticker: str) -> str:
    """A simple tool to get stock prices."""
    print(f"💰 Checking stock price for {ticker}...")
    return f"{ticker} is currently trading at $150.00 📈"

async def main():
    # --- STEP 2: Initialize Infrastructure ---
    # Data is saved to 'my_agent.db' automatically
    state_manager = SQLiteStateManager("my_agent.db")
    await state_manager.initialize()

    # --- STEP 3: Setup the Agent ---
    runtime = AgentRuntime(
        state_manager=state_manager,
        policy_engine=PolicyEngine(policies=[]), # No restrictions for this demo
        tools={
            "check_stock_price": check_stock_price
        }
    )
    
    # Please ensure you have GOOGLE_API_KEY exported in your terminal!
    client = GeminiClient() 

    # --- STEP 4: Give it a job! ---
    print("🤖 Agency Started...")
    task = await runtime.create_task("Please check the stock price of Google")
    
    # Run the loop
    await runtime.run_loop(task, client)
    print("✅ Done!")

if __name__ == "__main__":
    asyncio.run(main())
