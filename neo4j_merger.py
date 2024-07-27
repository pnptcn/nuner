from neo4j import GraphDatabase
import json
import logging
import re

logger = logging.getLogger(__name__)

class Neo4jGraphMerger:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def merge_data(self, new_data):
        with self.driver.session() as session:
            data = json.loads(new_data)
            
            # Merge nodes
            for node in data.get('nodes', []):
                session.write_transaction(self._merge_node, node)
            
            # Merge edges
            for edge in data.get('edges', []):
                session.write_transaction(self._merge_edge, edge)

    @staticmethod
    def _sanitize_label(label):
        # Capitalize and remove any non-alphanumeric characters
        return re.sub(r'\W+', '', label.title())

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
        
        # Get the label from the 'type' property, or use 'Entity' as default
        label = Neo4jGraphMerger._sanitize_label(node.get('type', 'Entity'))
        
        # Prepare node properties
        properties = Neo4jGraphMerger._flatten_properties(node)
        
        # Merge node
        query = (
            f"MERGE (n:{label} {{id: $id}}) "
            "SET n += $properties "
            "RETURN n"
        )
        result = tx.run(query, id=node_id, properties=properties)
        return result.single()

    @staticmethod
    def _merge_edge(tx, edge):
        source = edge.get('source')
        target = edge.get('target')
        label = Neo4jGraphMerger._sanitize_label(edge.get('label', 'RELATED_TO'))
        
        if not source or not target:
            logger.warning(f"Skipping edge due to missing source or target: {edge}")
            return
        
        # Prepare edge properties
        properties = Neo4jGraphMerger._flatten_properties({k: v for k, v in edge.items() if k not in ['source', 'target', 'label']})
        
        # Merge edge
        query = (
            "MATCH (source {id: $source}), (target {id: $target}) "
            f"MERGE (source)-[r:{label}]->(target) "
            "SET r += $properties "
            "RETURN r"
        )
        result = tx.run(query, source=source, target=target, properties=properties)
        return result.single()

    def search(self, query):
        with self.driver.session() as session:
            result = session.read_transaction(self._search, query)
            return result

    @staticmethod
    def _search(tx, query):
        cypher_query = (
            "MATCH (n) "
            "WHERE n.id CONTAINS $query "
            "RETURN n"
        )
        result = tx.run(cypher_query, query=query)
        return [record["n"] for record in result]

    def visualize(self):
        with self.driver.session() as session:
            node_count = session.read_transaction(lambda tx: tx.run("MATCH (n) RETURN count(n) AS count").single()["count"])
            edge_count = session.read_transaction(lambda tx: tx.run("MATCH ()-[r]->() RETURN count(r) AS count").single()["count"])
        print(f"Graph contains {node_count} nodes and {edge_count} edges")
        print("For detailed visualization, please use Neo4j Browser at http://localhost:7474")

# Example usage
# merger = Neo4jGraphMerger("bolt://localhost:7687", "neo4j", "password")
