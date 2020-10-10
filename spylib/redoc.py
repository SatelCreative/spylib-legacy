from dataclasses import dataclass
from typing import List, Union, Optional, Type
from enum import Enum
from pydantic import BaseModel
from pydantic.schema import model_process_schema
from apispec import APISpec
from starlette.responses import JSONResponse
from fastapi.openapi.docs import get_redoc_html
from fastapi import APIRouter


SCHEMA_PATH = '#/components/schemas/'


@dataclass
class TagAndModels:
    models: Union[Type[BaseModel], List[Union[BaseModel, Enum]]]
    tag: Optional[str] = None
    description: Optional[str] = None


def _model_to_doc_str(model: Type[BaseModel], title: bool = False):
    clsname = model.__name__
    schema_title = f'## {clsname}\n'
    schema_description = model.__doc__ + '\n' if model.__doc__ is not None else ''
    # The double return carriage is important. DO NOT REMOVE THEM.
    schema_ref = f'<SchemaDefinition schemaRef="{SCHEMA_PATH}{clsname}"/>\n\n'
    if title:
        return f'{schema_title}{schema_description}{schema_ref}'

    return f'{schema_description}{schema_ref}'


def make_docs_router(
    title: str,
    description: str,
    logo_url: str,
    logo_alt_text: str,
    tags_and_models: List[TagAndModels],
) -> APIRouter:
    tags = []
    models = []
    for t_n_m in tags_and_models:
        tag_description = t_n_m.description + '\n' if t_n_m.description else ''
        if isinstance(t_n_m.models, list):
            for model in t_n_m.models:
                models.append(model)
                tag_description += _model_to_doc_str(model=model, title=True)
        else:
            model = t_n_m.models
            models.append(model)
            tag_description += _model_to_doc_str(model=model)
        if t_n_m.tag is None:
            continue
        tags.append(
            {
                'name': t_n_m.tag,
                'description': tag_description,
                # 'x-displayName': 'The Pet Model',
            }
        )

    custom = {
        'tags': tags,
        'x-tagGroups': [{'name': 'Models', 'tags': [tag['name'] for tag in tags]}],
    }

    model_docs = APISpec(
        title=title,
        version='1.0',
        openapi_version='3.0.0',
        info={'description': description, 'x-logo': {'url': logo_url, 'altText': logo_alt_text}},
        **custom,
    )

    # Reuse Fastapi code:
    # https://github.com/tiangolo/fastapi/blob/a6897963d5ff2c836313c3b69fc6062051c07a63/fastapi/utils.py#L16u

    model_name_map = {model: model.__name__ for model in models}

    for model in models:
        schema, _, _ = model_process_schema(
            model, model_name_map=model_name_map, ref_prefix=SCHEMA_PATH
        )
        model_docs.components.schema(model.__name__, schema)

    router = APIRouter()

    @router.get('/openapi.json', include_in_schema=False)
    async def spec():
        return JSONResponse(model_docs.to_dict())

    @router.get('/redoc', include_in_schema=False)
    async def redoc():
        return get_redoc_html(openapi_url='openapi.json', title=title)

    return router
