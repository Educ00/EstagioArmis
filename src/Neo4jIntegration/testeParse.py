import json

# Exemplo de dados (código JSON fornecido)
data = {
    "lc": 1,
    "type": "constructor",
    "id": ["langchain", "schema", "messages", "AIMessage"],
    "kwargs": {
        "content": "```json\n{\n  \"topic\": \"Sofia's Journey on the Chosen Path\",\n  \"entities\": [\n    {\n      \"name\": \"Sofia\",\n      \"type\": \"Person\",\n      \"metadata\": {\n        \"location\": \"Path 2\",\n        \"feeling\": \"happy\"\n      }\n    },\n    {\n      \"name\": \"Path 2\",\n      \"type\": \"Path\",\n      \"metadata\": {\n        \"description\": \"Wide with trees and flowers\"\n      }\n    },\n    {\n      \"name\": \"Trees\",\n      \"type\": \"Plant\",\n      \"metadata\": {\n        \"relationship_to_path\": \"found along Path 2\"\n      }\n    },\n    {\n      \"name\": \"Wind\",\n      \"type\": \"Natural Element\",\n      \"metadata\": {\n        \"action\": \"felt by Sofia\"\n      }\n    },\n    {\n      \"name\": \"Birds\",\n      \"type\": \"Animal\",\n      \"metadata\": {\n        \"action\": \"heard by Sofia\"\n      }\n    }\n  ],\n  \"relationships\": [\n    {\n      \"source_entity\": \"Sofia\",\n      \"target_entity\": \"Path 2\",\n      \"relationship\": \"chooses\"\n    },\n    {\n      \"source_entity\": \"Sofia\",\n      \"target_entity\": \"Trees\",\n      \"relationship\": \"sees while walking\"\n    },\n    {\n      \"source_entity\": \"Sofia\",\n      \"target_entity\": \"Wind\",\n      \"relationship\": \"feels while walking\"\n    },\n    {\n      \"source_entity\": \"Sofia\",\n      \"target_entity\": \"Birds\",\n      \"relationship\": \"hears while walking\"\n    },\n    {\n      \"source_entity\": \"Path 2\",\n      \"target_entity\": \"Sofia\",\n      \"relationship\": \"provides experience leading to happiness\"\n    }\n  ]\n}\n```",
        "additional_kwargs": {"refusal": None},
        "response_metadata": {
            "token_usage": {
                "completion_tokens": 385,
                "prompt_tokens": 1043,
                "total_tokens": 1428
            },
            "model_name": "gpt-4o-mini-2024-07-18",
            "system_fingerprint": "fp_ded0d14823",
            "id": "chatcmpl-BEZXrWQg1ul7WkpkZ7teFL9SvcFJD"
        },
        "usage_metadata": {
            "input_tokens": 1043,
            "output_tokens": 385,
            "total_tokens": 1428
        }
    }
}

json_data = json.dumps(data, indent=4)
data = str(json_data).replace(r"\n", "\n").replace(r"\"", "\"").replace("  ", "\t").replace("\"```json", "").replace("```\"", "")

with open('arquivo.txt', 'w', encoding='utf-8') as f:
    json.dump(json.loads(data,strict=False), f, indent=4)

#with open('arquivo.txt', 'w', encoding='utf-8') as f:
#    f.write(str(json_data).replace(r"\n", "\n").replace(r"\"", "\"").replace("  ", "\t").replace("\"```json", "").replace("```\"", ""))
