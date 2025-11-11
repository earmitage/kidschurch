"""
Cost Calculator for LLM API calls
Provides token cost calculations based on provider and model
"""

# Provider-specific token costs (per 1M tokens)
# Prices are approximate and may vary - update as needed
COSTS = {
    'openai': {
        'gpt-3.5-turbo': {'input': 0.50, 'output': 1.50},
        'gpt-4': {'input': 30.00, 'output': 60.00},
        'gpt-4-turbo': {'input': 10.00, 'output': 30.00},
    },
    'anthropic': {
        'claude-3-haiku-20240307': {'input': 0.25, 'output': 1.25},
        'claude-3-opus-20240229': {'input': 15.00, 'output': 75.00},
        'claude-3-sonnet-20240229': {'input': 3.00, 'output': 15.00},
    },
    'gemini': {
        'gemini-2.0-flash-exp': {'input': 0.075, 'output': 0.30},
        'gemini-pro': {'input': 0.50, 'output': 1.50},
        'gemini-2.0-flash-preview-image-generation': {'input': 0.0, 'output': 0.0},  # Image generation pricing may differ
    }
}


def calculate_cost(provider: str, model: str, input_tokens: int, output_tokens: int) -> float:
    """
    Calculate estimated cost for LLM API call
    
    Args:
        provider: AI provider name ('openai', 'anthropic', 'gemini')
        model: Model name
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens
        
    Returns:
        Estimated cost in USD
    """
    provider_lower = provider.lower()
    model_lower = model.lower()
    
    # Find matching provider
    if provider_lower not in COSTS:
        return 0.0
    
    provider_costs = COSTS[provider_lower]
    
    # Find matching model (fuzzy match)
    model_pricing = None
    for cost_model, pricing in provider_costs.items():
        if cost_model.lower() in model_lower or model_lower in cost_model.lower():
            model_pricing = pricing
            break
    
    # If no exact match, use first available model as fallback
    if model_pricing is None and provider_costs:
        model_pricing = list(provider_costs.values())[0]
    
    if model_pricing is None:
        return 0.0
    
    # Calculate cost
    input_cost = (input_tokens / 1_000_000) * model_pricing['input']
    output_cost = (output_tokens / 1_000_000) * model_pricing['output']
    
    return round(input_cost + output_cost, 6)


