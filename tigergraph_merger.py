import pyTigerGraph as tg
import json
import logging

logger = logging.getLogger(__name__)

class TigerGraphMerger:
    def __init__(self, host, graph_name, username, password):
        self.conn = tg.TigerGraphConnection(host=host, graphname=graph_name, username=username, password=password)
        self.graph_name = graph_name
        
        # Ensure the graph exists
        self._create_graph_if_not_exists()
        
        # Ensure the schema exists
        self._create_schema_if_not_exists()

    def _create_graph_if_not_exists(self):
        try:
            logger.info(f"Attempting to create graph: {self.graph_name}")
            self.conn.createGraph(self.graph_name)
            logger.info(f"Graph {self.graph_name} created successfully")
        except Exception as e:
            if "Graph already exists" in str(e):
                logger.info(f"Graph {self.graph_name} already exists")
            else:
                logger.error(f"Error creating graph: {str(e)}")
                raise

    def _create_schema_if_not_exists(self):
        try:
            # Check if vertex types exist, if not create them
            if 'node' not in self.conn.getVertexTypes():
                logger.info("Creating vertex type: node")
                self.conn.createVertexType("node")
            
            # Check if edge type exists, if not create it
            if 'edge' not in self.conn.getEdgeTypes():
                logger.info("Creating edge type: edge")
                self.conn.createEdgeType("edge", "node", "node")
        except Exception as e:
            logger.error(f"Error creating schema: {str(e)}")
            raise

    def merge_data(self, new_data):
        data = json.loads(new_data)
        
        # Merge nodes
        for node in data.get('nodes', []):
            self._merge_node(node)

        # Merge edges
        for edge in data.get('edges', []):
            self._merge_edge(edge)

    def _merge_node(self, node):
        node_id = node.get('id')
        if not node_id:
            logger.warning(f"Skipping node due to missing id: {node}")
            return
        
        # In TigerGraph, upsert will create or update the vertex
        self.conn.upsertVertex("node", node_id, node)

    def _merge_edge(self, edge):
        source = edge.get('source')
        target = edge.get('target')
        
        if not source or not target:
            logger.warning(f"Skipping edge due to missing source or target: {edge}")
            return
        
        edge_id = f"{source}-{target}"
        
        # In TigerGraph, upsert will create or update the edge
        self.conn.upsertEdge("node", source, "edge", "node", target, edge_id, edge)

    def search(self, query):
        # This is a basic implementation. You might want to adjust based on your specific needs
        gsql_query = f'''
        INTERPRET QUERY () FOR GRAPH {self.graph_name} {{
          StartVertex = {{node.*}};
          PRINT StartVertex WHERE toLowerCase(to_string(StartVertex)) LIKE "%{query.lower()}%";
        }}'''
        
        result = self.conn.runInterpretedQuery(gsql_query)
        return result[0]['StartVertex']

    def visualize(self):
        # This is a placeholder for visualization logic
        # TigerGraph provides GraphStudio for visualization, but it's web-based
        # For programmatic visualization, you might need to use a third-party library
        print("Visualizing graph...")
        stats = self.conn.getStatistics()
        print(f"Nodes: {stats['node']}")
        print(f"Edges: {stats['edge']}")
