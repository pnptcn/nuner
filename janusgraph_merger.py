from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection
from gremlin_python.structure.graph import Graph
from gremlin_python.process.graph_traversal import __
from gremlin_python.process.strategies import *
from gremlin_python.process.traversal import T, Cardinality
import json
import logging

logger = logging.getLogger(__name__)

class JanusGraphMerger:
    def __init__(self, host="janusgraph", port=8182):
        self.graph = Graph()
        self.g = self.graph.traversal().withRemote(DriverRemoteConnection(f'ws://{host}:{port}/gremlin', 'g'))

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
        
        vertex = self.g.V().has('id', node_id).toList()
        if vertex:
            # Update existing vertex
            vertex = vertex[0]
            for key, value in node.items():
                if key != 'id':
                    if isinstance(value, dict):
                        for sub_key, sub_value in value.items():
                            self.g.V(vertex).property(Cardinality.single, f"{key}_{sub_key}", sub_value).next()
                    elif isinstance(value, list):
                        for item in value:
                            if isinstance(item, dict):
                                for sub_key, sub_value in item.items():
                                    self.g.V(vertex).property(Cardinality.list_, f"{key}_{sub_key}", sub_value).next()
                            else:
                                self.g.V(vertex).property(Cardinality.set_, key, item).next()
                    else:
                        self.g.V(vertex).property(Cardinality.single, key, value).next()
        else:
            # Create new vertex
            vertex = self.g.addV('node').property('id', node_id).next()
            for key, value in node.items():
                if key != 'id':
                    if isinstance(value, dict):
                        for sub_key, sub_value in value.items():
                            self.g.V(vertex).property(Cardinality.single, f"{key}_{sub_key}", sub_value).next()
                    elif isinstance(value, list):
                        for item in value:
                            if isinstance(item, dict):
                                for sub_key, sub_value in item.items():
                                    self.g.V(vertex).property(Cardinality.list_, f"{key}_{sub_key}", sub_value).next()
                            else:
                                self.g.V(vertex).property(Cardinality.set_, key, item).next()
                    else:
                        self.g.V(vertex).property(Cardinality.single, key, value).next()

    def _merge_edge(self, edge):
        source = edge.get('source')
        target = edge.get('target')
        label = edge.get('label', 'edge')
        
        if not source or not target:
            logger.warning(f"Skipping edge due to missing source or target: {edge}")
            return
        
        edge_id = f"{source}-{target}"
        
        source_vertex = self.g.V().has('id', source).next()
        target_vertex = self.g.V().has('id', target).next()
        
        existing_edge = self.g.V(source_vertex).outE(label).where(__.inV().is_(target_vertex)).toList()
        
        if existing_edge:
            # Update existing edge
            existing_edge = existing_edge[0]
            for key, value in edge.items():
                if key not in ['source', 'target', 'label']:
                    if isinstance(value, dict):
                        for sub_key, sub_value in value.items():
                            self.g.E(existing_edge).property(f"{key}_{sub_key}", sub_value).next()
                    elif isinstance(value, list):
                        for item in value:
                            if isinstance(item, dict):
                                for sub_key, sub_value in item.items():
                                    self.g.E(existing_edge).property(f"{key}_{sub_key}", sub_value).next()
                            else:
                                self.g.E(existing_edge).property(key, item).next()
                    else:
                        self.g.E(existing_edge).property(key, value).next()
        else:
            # Create new edge
            new_edge = self.g.V(source_vertex).addE(label).to(target_vertex).next()
            for key, value in edge.items():
                if key not in ['source', 'target', 'label']:
                    if isinstance(value, dict):
                        for sub_key, sub_value in value.items():
                            self.g.E(new_edge).property(f"{key}_{sub_key}", sub_value).next()
                    elif isinstance(value, list):
                        for item in value:
                            if isinstance(item, dict):
                                for sub_key, sub_value in item.items():
                                    self.g.E(new_edge).property(f"{key}_{sub_key}", sub_value).next()
                            else:
                                self.g.E(new_edge).property(key, item).next()
                    else:
                        self.g.E(new_edge).property(key, value).next()

    def search(self, query):
        results = self.g.V().has('id', __.text().containing(query)).elementMap().toList()
        return results

    def visualize(self):
        print("Visualizing graph...")
        node_count = self.g.V().count().next()
        edge_count = self.g.E().count().next()
        print(f"Nodes: {node_count}")
        print(f"Edges: {edge_count}")
