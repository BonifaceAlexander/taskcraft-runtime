import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from taskcraft.planner.gemini import GeminiPlanner, V2ResponseAdapter
from taskcraft.state.models import Task, AgentState

# Mock the google.genai module since it might not be installed in test env
import sys
mock_genai = MagicMock()
mock_genai.types.Content = MagicMock()
mock_genai.types.Part = MagicMock()
sys.modules["google.genai"] = mock_genai
sys.modules["google.genai.types"] = mock_genai.types

@pytest.fixture
def mock_client():
    with patch("taskcraft.planner.gemini.genai.Client") as MockClient:
        client_instance = MockClient.return_value
        # Mock models.generate_content
        client_instance.models.generate_content = MagicMock()
        yield client_instance

@pytest.mark.asyncio
async def test_gemini_planner_initialization():
    with patch.dict("os.environ", {"GOOGLE_API_KEY": "test_key"}):
        planner = GeminiPlanner()
        assert planner.client is not None

@pytest.mark.asyncio
async def test_plan_generates_content(mock_client):
    with patch.dict("os.environ", {"GOOGLE_API_KEY": "test_key"}):
        planner = GeminiPlanner()
        
        # Setup mock response
        mock_response = MagicMock()
        mock_response.text = "Test thought"
        mock_response.candidates = [MagicMock()]
        mock_response.candidates[0].content.parts = [MagicMock(text="Test thought", function_call=None)]
        
        planner.client.models.generate_content.return_value = mock_response

        task = Task(task_id="123", description="Test task", status=AgentState.EXECUTING)
        history = [{"role": "user", "content": "Context"}]
        
        result = await planner.plan(task, history)
        
        assert isinstance(result, V2ResponseAdapter)
        assert result.text == "Test thought"
        planner.client.models.generate_content.assert_called_once()

@pytest.mark.asyncio
async def test_multimodal_parsing(mock_client):
    with patch.dict("os.environ", {"GOOGLE_API_KEY": "test_key"}):
        with patch("builtins.open", new_callable=MagicMock) as mock_open:
            mock_open.return_value.__enter__.return_value.read.return_value = b"fake_image_bytes"
            with patch("os.path.exists", return_value=True):
                planner = GeminiPlanner()
                
                # Mock response irrelevant here, checking logic flow
                planner.client.models.generate_content.return_value = MagicMock()

                task = Task(task_id="123", description="Vision task", status=AgentState.EXECUTING)
                # User history with image tag
                history = [{"role": "user", "content": "Look at this: [IMAGE: /tmp/test.png]"}]
                
                await planner.plan(task, history)
                
                # Verify parts construction
                call_args = planner.client.models.generate_content.call_args
                contents = call_args.kwargs['contents']
                # We expect the last content to be user role
                last_msg = contents[-1]
                
                # In our mocked genai, distinct parts should be created
                # 1 image part + 1 text part
                assert len(last_msg.parts) == 2 
