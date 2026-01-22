from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

def retryable_tool(max_attempts: int = 3):
    """
    Decorator to make a tool function retryable on failure.
    Uses exponential backoff.
    """
    return retry(
        stop=stop_after_attempt(max_attempts),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type(Exception), # Retry on any generic exception for now
        reraise=True
    )
