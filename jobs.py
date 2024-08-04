import logging
from gliner import GLiNER
import json
from neo4j import GraphDatabase
import nltk
from nltk.tokenize import sent_tokenize
import re
from fuzzywuzzy import fuzz

nltk.download('punkt', quiet=True)

logger = logging.getLogger(__name__)


class Job:
    def __init__(self, profile):
        self.profile = profile

    @staticmethod
    def smart_chunk(text, max_chunk_size=1000):
        sentences = sent_tokenize(text)
        chunks = []
        current_chunk = ""

        for sentence in sentences:
            if len(current_chunk) + len(sentence) <= max_chunk_size:
                current_chunk += sentence + " "
            else:
                chunks.append(current_chunk.strip())
                current_chunk = sentence + " "

        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks

    @staticmethod
    def extract_entities_and_relations(model, content):
        # Define entity types
        entity_labels = [
            "person", "organization", "location", "date", "event", "product",
            "position", "financial_info", "scam", "government_body", "law",
            "technology", "project", "award", "education", "publication"
        ]
        
        # Extract entities
        entities = model.predict_entities(content, entity_labels)
        
        # Define relation types
        relation_labels = [
            "person <> organization",
            "person <> position",
            "person <> event",
            "organization <> event",
            "organization <> location",
            "event <> date",
            "person <> education",
            "person <> award",
            "organization <> project",
            "person <> project",
            "organization <> financial_info",
            "person <> publication",
            "organization <> technology",
            "government_body <> law",
            "organization <> scam",
            "person <> scam"
        ]
        
        # Extract relations
        relations = model.predict_entities(content, relation_labels)
        
        return entities, relations

    @staticmethod
    def process_entities(entities):
        nodes = []
        for entity in entities:
            node = {
                "id": Job.generate_node_id(entity["text"]),
                "status": "active",
                "type": entity["label"],
                "label": entity["text"],
                "data": {
                    "original_name": entity["text"],
                    "score": entity["score"]
                }
            }
            nodes.append(node)
        return nodes

    @staticmethod
    def generate_node_id(text):
        # Generate a consistent ID for a node based on its text
        return text.lower().replace(" ", "-")

    @staticmethod
    def process_relations(relations):
        edges = []
        for relation in relations:
            print("relation", relation)
            source_type, target_type = relation["label"].split(" <> ")
            source_text, target_text = relation["text"].split(" <> ")
            
            source_id = Job.generate_node_id(source_text)
            target_id = Job.generate_node_id(target_text)
            
            edge = {
                "id": f"{source_id}-{target_id}",
                "source": source_id,
                "target": target_id,
                "status": "active",
                "type": "directed",
                "label": relation["label"],
                "data": {
                    "score": relation["score"]
                }
            }
            edges.append(edge)
        return edges

    @staticmethod
    def extract_additional_info(model, content):
        # Extract timeline information
        timeline_prompt = "Extract timeline information from the text:\n"
        timeline = model.predict_entities(timeline_prompt + content, ["timeline"])

        # Extract key facts
        facts_prompt = "Extract key facts from the text:\n"
        facts = model.predict_entities(facts_prompt + content, ["fact"])

        # Extract potential leads for investigation
        leads_prompt = "Identify potential leads for further investigation:\n"
        leads = model.predict_entities(leads_prompt + content, ["lead"])

        return timeline, facts, leads

    def do(self):
        try:
            # Load the model inside the method
            model = GLiNER.from_pretrained("knowledgator/gliner-multitask-large-v0.5")
            
            # Create Neo4j connection inside the method
            driver = GraphDatabase.driver("bolt://neo4j:7687", auth=("neo4j", "securepassword"))

            page = self.profile.get('page')
            if not page:
                logger.error("Invalid profile data: missing page.")
                return

            content = page.get('content')
            if not content:
                logger.error("Invalid profile data: missing content.")
                return

            # Extract the actual text content from the 'chunks' field
            chunks = content.get('raw')
            if not chunks:
                logger.error("Invalid content data: missing chunks.")
                return

            all_nodes = []
            all_edges = []

            for chunk in chunks.split("\n"):
                print("chunk", chunk)
                # Process each chunk
                entities, relations = self.extract_entities_and_relations(model, chunk)
                
                nodes = self.process_entities(entities)
                all_nodes.extend(nodes)
                print("nodes:", all_nodes)

            edges = self.process_relations(relations)                
            all_edges.extend(edges)
            print("edges:", all_edges)

            # Extract additional information from the full text
            full_text = " ".join(chunks)
            timeline, facts, leads = self.extract_additional_info(model, full_text)

            # Process additional information
            for item in timeline + facts + leads:
                node = {
                    "id": self.generate_node_id(item["text"]),
                    "status": "active",
                    "type": item["label"],
                    "label": item["text"],
                    "data": {
                        "original_text": item["text"],
                        "score": item["score"]
                    }
                }
                all_nodes.append(node)

            data = {
                "nodes": all_nodes,
                "edges": all_edges
            }
            
            json_output = json.dumps(data)
            
            try:
                with driver.session() as session:
                    session.write_transaction(self.merge_data, json_output)
            except Exception as e:
                logger.error(f"Error merging data: {str(e)}")

            driver.close()
        except Exception as e:
            logger.error(f"Error in do: {str(e)}")

    @staticmethod
    def merge_data(tx, json_data):
        data = json.loads(json_data)
        
        # Merge nodes
        for node in data.get('nodes', []):
            Job._merge_node(tx, node)
        
        # Merge edges
        for edge in data.get('edges', []):
            Job._merge_edge(tx, edge)

    @staticmethod
    def _sanitize_label(label):
        # Capitalize and remove any non-alphanumeric characters
        return re.sub(r'\W+', '', label.title())

    @staticmethod
    def _normalize_name(name):
        # Remove common titles and suffixes
        name = re.sub(r'\b(Dr\.?|Mr\.?|Mrs\.?|Ms\.?|Prof\.?|Ltd\.?|Inc\.?|Corp\.?)\b', '', name, flags=re.IGNORECASE)
        # Remove punctuation and convert to lowercase
        return re.sub(r'[^\w\s]', '', name).lower().strip()

    @staticmethod
    def _flatten_properties(properties):
        flattened = {}
        for key, value in properties.items():
            if isinstance(value, (str, int, float, bool)):
                flattened[key] = value
            elif isinstance(value, (list, dict)):
                flattened[key] = json.dumps(value)
            else:
                flattened[key] = str(value)
        return flattened

    @staticmethod
    def _merge_node(tx, node):
        node_id = node.get('id')
        if not node_id:
            logger.warning(f"Skipping node due to missing id: {node}")
            return
        
        label = Job._sanitize_label(node.get('type', 'Entity'))
        properties = Job._flatten_properties(node)
        
        normalized_name = Job._normalize_name(properties.get('label', ''))
        
        # Find existing nodes with similar names
        query = (
            f"MATCH (n:{label}) "
            "WHERE n.normalized_name IS NOT NULL "
            "WITH n, apoc.text.levenshteinSimilarity(n.normalized_name, $normalized_name) AS similarity "
            "WHERE similarity > 0.8 "
            "RETURN n "
            "ORDER BY similarity DESC "
            "LIMIT 1"
        )
        result = tx.run(query, normalized_name=normalized_name)
        existing_node = result.single()
        
        if existing_node:
            # Update existing node
            update_query = (
                f"MATCH (n:{label}) WHERE id(n) = $node_id "
                "SET n += $properties "
                "RETURN n"
            )
            result = tx.run(update_query, node_id=existing_node['n'].id, properties=properties)
        else:
            # Create new node
            create_query = (
                f"CREATE (n:{label} $properties) "
                "SET n.normalized_name = $normalized_name "
                "RETURN n"
            )
            result = tx.run(create_query, properties=properties, normalized_name=normalized_name)
        
        return result.single()

    @staticmethod
    def _merge_edge(tx, edge):
        source = edge.get('source')
        target = edge.get('target')
        label = Job._sanitize_label(edge.get('label', 'RELATED_TO'))
        
        if not source or not target:
            logger.warning(f"Skipping edge due to missing source or target: {edge}")
            return
        
        properties = Job._flatten_properties({k: v for k, v in edge.items() if k not in ['source', 'target', 'label']})
        
        query = (
            "MATCH (source), (target) "
            "WHERE source.normalized_name = $source_name AND target.normalized_name = $target_name "
            f"MERGE (source)-[r:{label}]->(target) "
            "SET r += $properties "
            "RETURN r"
        )
        result = tx.run(query, source_name=Job._normalize_name(source), target_name=Job._normalize_name(target), properties=properties)
        return result.single()
