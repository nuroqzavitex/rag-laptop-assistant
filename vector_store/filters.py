from __future__ import annotations
from typing import Any
from qdrant_client.models import FieldCondition, Filter, MatchValue, Range

def _build_qdrant_filter(where: dict[str, Any]) -> Filter | None:
  pass

def _parse_single_condition(cond: dict[str, Any]) -> FieldCondition | None:
  for field, value in cond.items():
    if isinstance(value, dict):
      if '$eq' in value:
        return FieldCondition(
          key=field,
          match=MatchValue(value=value['$eq'])
        )
      if '$contains' in value:
        return FieldCondition(
          key = field,
          match = MatchValue(value = value['$contains'])
        )
      
      range_params = {}

      if '$gte' in value:
        range_params['gte'] = value['$gte']
      if '$lte' in value:
        range_params['lte'] = value['$lte']
      if '$gt' in value:
        range_params['gt'] = value['$gt']
      if '$lt' in value:
        range_params['lt'] = value['$lt']
      if range_params:
        return FieldCondition(
          key=field,
          range=Range(**range_params)
        )

    else:
      return FieldCondition(
        key=field,
        match=MatchValue(value=value)
      )
  return None