from arango import ArangoClient
import json

class ArangoDBGraphMerger:
    def __init__(self, host, port, database, username, password):
        self.client = ArangoClient(hosts=f'http://{host}:{port}')
        self.db = self.client.db(database, username=username, password=password)
        
        # Ensure the graph and its collections exist
        if not self.db.has_graph('knowledge_graph'):
            graph = self.db.create_graph('knowledge_graph')
            graph.create_vertex_collection('nodes')
            graph.create_edge_definition(
                edge_collection='edges',
                from_vertex_collections=['nodes'],
                to_vertex_collections=['nodes']
            )
        else:
            self.graph = self.db.graph('knowledge_graph')

    def merge_data(self, new_data):
        data = json.loads(new_data)
        
        # Merge nodes
        for node in data.get('nodes', []):
            self._merge_node(node)

        # Merge edges
        for edge in data.get('edges', []):
            self._merge_edge(edge)

    def _merge_node(self, node):
        nodes = self.db.collection('nodes')
        node_key = node.get('id')
        
        if not node_key:
            print(f"Skipping node due to missing id: {node}")
            return
        
        if nodes.has(node_key):
            # Update existing node
            nodes.update({'_key': node_key, **node})
        else:
            # Insert new node
            nodes.insert({'_key': node_key, **node})

    def _merge_edge(self, edge):
        edges = self.db.collection('edges')
        
        source = edge.get('source')
        target = edge.get('target')
        
        if not source or not target:
            print(f"Skipping edge due to missing source or target: {edge}")
            return
        
        edge_key = f"{source}-{target}"
        
        # In ArangoDB, edges need _from and _to fields
        edge['_from'] = f"nodes/{source}"
        edge['_to'] = f"nodes/{target}"
        
        if edges.has(edge_key):
            # Update existing edge
            edges.update({'_key': edge_key, **edge})
        else:
            # Insert new edge
            edges.insert({'_key': edge_key, **edge})

    def search(self, query):
        aql = """
        FOR doc IN nodes
            FILTER LIKE(TO_STRING(doc), @query, true)
            RETURN doc
        """
        cursor = self.db.aql.execute(aql, bind_vars={'query': f'%{query}%'})
        return [doc for doc in cursor]

    def visualize(self):
        # This is a placeholder for visualization logic
        # You might use libraries like ArangoDB's built-in Graph Viewer or external tools
        print("Visualizing graph...")
        node_count = self.db.collection('nodes').count()
        edge_count = self.db.collection('edges').count()
        print(f"Nodes: {node_count}")
        print(f"Edges: {edge_count}")
