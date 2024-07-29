import json
import logging
import os
import re

from arangodb import ArangoDBGraphMerger
from janusgraph_merger import JanusGraphMerger
from neo4j_merger import Neo4jGraphMerger
from openai import OpenAI

logger = logging.getLogger(__name__)


class Job:
    def __init__(self, profile):
        self.profile = profile

    def prompt(self, content):
        return f"""
        Please analyze the following text carefully, and extract ALL valuable information including, but not limited to:
        entities, events, locations, and their relationships. We are looking to mine intelligence as granular as possible.
        Format the response as a JSON object according to the following template:

        {{
            "nodes": [{{
                "id": "<normalized-and-tokenized-name>",
                "status": "<any status indicator we may know, otherwise unknown>",
                "type": "<the type of the data>",
                "label": "<the simplified name of the entity, event, location, or otherwise identifiable item>",
                "data": {{
                    <arbitrary (nestable) key/value store to use for additional information, intelligence, or context>
                    "original_name": "<the original name as it was found in the content, before simplification>",
                    "alternative_names": "<alternative instances of the name if found>",
                    "timeline": [
                        {{"<year>": "<(suggested structure) any found information that can be structured as a timeline>"}},
                        {{"<date>": "<(suggested structure) any found information that can be structured as a timeline>"}},
                        {{"<timestamp>": "<(suggested structure) any found information that can be structured as a timeline>"}}
                    ],
                    "work_history": [<mentions of previous or currently other positions, if relevant, as arbitrary key/value store>],
                    "education": [<mentions of previous or current educations, if relevant, as arbitrary key/value store>],
                    "achievements": [<mentions of previous or current achievements, if relevant, as arbitrary key/value store>],
                    "facts": [<any other groupable items, that have no distinct group already, as arbitrary key/value store>],
                    "tags": [<any short remarkable item, or common terms that could be used for soft-linking, tags may be key/value stores>],
                    "urls": [<any url found in relation to this node>],
                    ... <additional, unforeseen structures that make sense>
                }}
            }}],
            "edges": [{{
                "id": "<source-id-target-id>",
                "source": "<source-id>",
                "target": "<target-id>",
                "status": "<any status indicator we may know, otherwise unknown>",
                "type": "<edge type: directed, undirected, weighted, etc.>",
                "label": "<type/name of relationship>",
                "data": {{
                    <arbitrary (nestable) key/value store to use for additional information, intelligence, or context>,
                    ... <additional, unforeseen structures that make sense>
                }}
            }}]
        }}

        Be aware that you will be sent unfiltered, completely uncurated input, and there may be cases where there is no interesting information to be found.
        In such cases, respond with:

        {{
            "nodes": [{{}}],
            "edges": [{{}}]
        }}

        and nothing else.

        Please deeply analyze and structure the input text below, uncovering all of the importent information it contains.

        UNSTRUCTURED INPUT:

        {content}

        1. Provide only the JSON response below.
        2. Omit empty key/value pairs.
        3. DO NOT UNDER ANY CIRCUMSTANCE ADD ANY OTHER TEXT OR FORMATTING!
           NO: ```
           NO: ```json
        4. MAKE SURE TO OUTPUT A VALID JSON STRUCTURE ONLY!
        5. DO NOT ADD NEWLINES, INDENTATION, OR ANYTHING ADDITIONAL TO WHAT IS NEEDED TO OUTPUT A COMPLETE VALID JSON REPSONSE.

        JSON RESPONSE:


        """

    def do(self):
        client = OpenAI(
            base_url="http://host.docker.internal:1234/v1", api_key="lm-studio"
        )
        # client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        # arango_merger = ArangoDBGraphMerger("arangodb", 8529, "_system", "root", "yourpassword")
        # janus_merger = JanusGraphMerger("janusgraph", 8182)
        neo4j_merger = Neo4jGraphMerger("bolt://neo4j:7687", "neo4j", "securepassword")

        page = self.profile.get("page")
        if not page:
            logger.error("Invalid profile data: missing page.")
            return

        content = page.get("content")
        if not content:
            logger.error("Invalid profile data: missing content.")
            return

        chunks = content.get("chunks")
        if not chunks:
            logger.error("Invalid profile data: missing chunks.")
            return

        for chunk in chunks:
            stream = client.chat.completions.create(
                model="lmstudio-community/Meta-Llama-3.1-8B-Instruct-GGUF",
                messages=[{"role": "user", "content": self.prompt(chunk)}],
                temperature=0.1,
                stream=True,
            )

            out = []
            for part in stream:
                content = part.choices[0].delta.content
                if content is not None:
                    out.append(content)
                    print(content, end="")

            if len(out) > 0:
                try:
                    json_output = "".join(out)
                    # arango_merger.merge_data(json_output)
                    # janus_merger.merge_data(json_output)
                    neo4j_merger.merge_data(json_output)
                except json.JSONDecodeError:
                    logger.error(f"Invalid JSON output: {json_output}")
                except Exception as e:
                    logger.error(f"Error merging data: {str(e)}")
