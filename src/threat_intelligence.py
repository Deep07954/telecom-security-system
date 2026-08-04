import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import networkx as nx
import plotly.graph_objects as go
import os
os.environ["OMP_NUM_THREADS"] = "1"

class AdvancedThreatAnalyzer:
    def __init__(self, data_path="data/telecom_security_data.csv"):
        # If running from src/ or root, handle path gracefully
        if not os.path.exists(data_path):
            data_path = "telecom_security_data.csv"
            
        self.df = pd.read_csv(data_path)
        self.threats = self.df[self.df['label'] == 1].copy()

    def cluster_attack_patterns(self):
        """Uses K-Means to profile attacks and assigns names to them."""
        features = ['session_duration', 'packet_rate', 'login_attempts', 
                    'location_switch_freq', 'bandwidth_usage', 'call_failures']
        
        X_threats = self.threats[features]
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X_threats)
        
        kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
        self.threats['cluster'] = kmeans.fit_predict(X_scaled)
        
        # Map clusters to actual Attack Names
        attack_names = []
        for _, row in self.threats.iterrows():
            if row['packet_rate'] > 200:
                attack_names.append("DDoS / Botnet Swarm")
            elif row['location_switch_freq'] > 5:
                attack_names.append("SIM Cloning (Impossible Travel)")
            else:
                attack_names.append("Brute Force / ATO")
        
        self.threats['attack_name'] = attack_names
        return self.threats

    def generate_3d_network_graph(self):
        """Builds a 3D Interactive Plotly Graph for Streamlit."""
        self.cluster_attack_patterns()
        
        # Take a sample to keep the 3D rendering smooth in the browser
        sample_threats = self.threats.sample(n=min(100, len(self.threats)), random_state=42)
        
        G = nx.Graph()
        
        # Simulate Network Topology
        for idx, row in sample_threats.iterrows():
            sim_id = f"SIM_{idx}<br>Type: {row['attack_name']}"
            if row['location_switch_freq'] > 5:
                towers = [f"Cell Tower {np.random.randint(1, 10)}" for _ in range(3)]
                for t in towers:
                    G.add_edge(sim_id, t)
            else:
                tower = f"Cell Tower {np.random.randint(1, 10)}"
                G.add_edge(sim_id, tower)

        # Calculate 3D layout coordinates (dim=3 is the magic parameter)
        pos = nx.spring_layout(G, dim=3, seed=42)
        
        edge_x, edge_y, edge_z = [], [], []
        for edge in G.edges():
            x0, y0, z0 = pos[edge[0]]
            x1, y1, z1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
            edge_z.extend([z0, z1, None])

        edge_trace = go.Scatter3d(
            x=edge_x, y=edge_y, z=edge_z,
            line=dict(width=1, color='#555555'),
            hoverinfo='none', mode='lines'
        )

        node_x, node_y, node_z, node_text, node_color = [], [], [], [], []
        
        for node in G.nodes():
            x, y, z = pos[node]
            node_x.append(x)
            node_y.append(y)
            node_z.append(z)
            node_text.append(node)
            
            # Color coding: Green for Towers, Red/Orange/Purple for Attacks
            if "Tower" in node:
                node_color.append('#00FF00') # Healthy Tower
            elif "DDoS" in node:
                node_color.append('#FF0000') # Red for DDoS
            elif "SIM" in node:
                node_color.append('#FFA500') # Orange for SIM Clone
            else:
                node_color.append('#B19CD9') # Purple for Brute Force

        node_trace = go.Scatter3d(
            x=node_x, y=node_y, z=node_z,
            mode='markers', hoverinfo='text',
            marker=dict(size=6, color=node_color, line=dict(width=2, color='white')),
            text=node_text
        )

        fig = go.Figure(data=[edge_trace, node_trace])
        fig.update_layout(
            title="3D Telecom Threat Topology",
            paper_bgcolor="#0E1117",
            plot_bgcolor="#0E1117",
            font=dict(color="white"),
            showlegend=False,
            scene=dict(
                xaxis=dict(showbackground=False, showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showbackground=False, showgrid=False, zeroline=False, showticklabels=False),
                zaxis=dict(showbackground=False, showgrid=False, zeroline=False, showticklabels=False),
            ),
            margin=dict(l=0, r=0, b=0, t=40)
        )
        return fig

if __name__ == "__main__":
    analyzer = AdvancedThreatAnalyzer()
    fig = analyzer.generate_3d_network_graph()
    fig.write_html("3d_fraud_network.html")
    print("[+] 3D Graph generated successfully.")