from __future__ import annotations

from collections import OrderedDict

from _example_utils import run_raw_path_examples

# Request payloads copied from ../../llm_gateway/docs/price-rules-admin.yaml.
# Mock-only admin example: replace auth handling before using against an admin environment.
EXAMPLES = [{'name': 'update_price_rule',
  'method': 'POST',
  'path': '/admin/price-rules/price_rule_123',
  'json_body': {'input_price_micros_per_million': 200000,
                'output_price_micros_per_million': 800000,
                'status': 1}},
 {'name': 'create_price_rule',
  'method': 'POST',
  'path': '/admin/price-rules/create',
  'json_body': {'model_key': 'llm_model_gpt4o',
                'billing_family': 'text_token',
                'billing_strategy': 'text_io',
                'input_token_min': 0,
                'input_price_micros_per_million': 150000,
                'output_price_micros_per_million': 600000,
                'effective_at': '2026-06-02 00:00:00',
                'status': 1}},
 {'name': 'business_override_price_rule',
  'method': 'POST',
  'path': '/admin/price-rules/business-override',
  'json_body': {'model_key': 'llm_model_gpt4o',
                'billing_family': 'text_token',
                'billing_strategy': 'text_io',
                'input_price_micros_per_million': 150000,
                'output_price_micros_per_million': 600000}}]


if __name__ == "__main__":
    run_raw_path_examples("Admin price rules", EXAMPLES)
