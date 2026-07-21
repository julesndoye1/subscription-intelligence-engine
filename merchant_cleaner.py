def normalize_merchant(description):

    text = str(description).upper()

    merchant_rules = {
        "NETFLIX": "NETFLIX",
        "APPLE": "APPLE",
        "ITUNES": "APPLE",
        "SPOTIFY": "SPOTIFY",
        "PRIME VIDEO": "AMAZON PRIME",
        "AMAZON PRIME": "AMAZON PRIME",
        "GOOGLE": "GOOGLE",
        "MICROSOFT": "MICROSOFT",
        "ADOBE": "ADOBE",
        "CANVA": "CANVA",
        "CHATGPT": "OPENAI",
        "OPENAI": "OPENAI"
    }

    for keyword, merchant in merchant_rules.items():
        if keyword in text:
            return merchant

    return "OTHER"