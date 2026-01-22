import streamlit as st
import asyncio
import pandas as pd
import json
from datetime import datetime
from taskcraft.state.persistence import SQLiteStateManager
from taskcraft.state.models import Task
from taskcraft.core.lifecycle import AgentState

st.set_page_config(page_title="TaskCraft Control Center", page_icon="🕵️‍♂️", layout="wide")

st.title("🕵️‍♂️ TaskCraft Governance Console")

# --- DATA LOADING ---
async def load_data():
    db = SQLiteStateManager("taskcraft_state.db") # Default DB
    await db.initialize()
    tasks = await db.list_tasks()
    return tasks

# Wrapper to run async in streamlit
tasks = asyncio.run(load_data())

# --- SIDEBAR ---
st.sidebar.header("Filter Tasks")
status_filter = st.sidebar.multiselect(
    "Status", 
    [s.name for s in AgentState],
    default=[AgentState.EXECUTING.name, AgentState.AWAITING_APPROVAL.name, AgentState.COMPLETED.name]
)

# --- MAIN TABLE ---
if not tasks:
    st.info("No tasks found.")
else:
    # Convert to DataFrame for easier display
    data = []
    for t in tasks:
        data.append({
            "Task ID": t.task_id,
            "Description": t.description,
            "Status": t.status.name,
            "Steps": len(t.steps),
            "Updated": t.updated_at
        })
    df = pd.DataFrame(data)
    
    # Filter
    if status_filter:
        df = df[df['Status'].isin(status_filter)]
    
    st.dataframe(df, use_container_width=True)

    # --- TASK DETAILS ---
    st.markdown("---")
    st.header("Task Inspector")
    
    selected_task_id = st.selectbox("Select Task to Inspect", df['Task ID'].tolist())
    
    if selected_task_id:
        # Find the full task object
        task = next((t for t in tasks if t.task_id == selected_task_id), None)
        
        if task:
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("📋 Context")
                st.json({
                    "id": task.task_id,
                    "status": task.status.name,
                    "created": str(task.created_at)
                })
                
                # Action Buttons
                if task.status == AgentState.AWAITING_APPROVAL:
                    st.error("⚠️ This task is waiting for approval!")
                    st.code(f"python -m taskcraft.main_cli approve {task.task_id}", language="bash")
                    st.caption("Run this command in your terminal to approve.")

            with col2:
                st.subheader("👣 Execution Steps")
                step_data = []
                for s in task.steps:
                    step_data.append({
                        "Idx": s.index,
                        "Tool": s.name,
                        "Status": s.status,
                        "Error": s.error
                    })
                st.table(pd.DataFrame(step_data))
                
                # Show details of last step
                if task.steps:
                    with st.expander("Latest Step Details"):
                        st.write(task.steps[-1].model_dump())
