import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

class RecommendationEngine:
    def __init__(self, interactions_df):
        """
        Initialize the recommendation engine with user-item interactions
        
        Parameters:
        interactions_df (pd.DataFrame): DataFrame with columns [user_id, product_id, rating]
        """
        self.interactions_df = interactions_df
        self.user_item_matrix = None
        self.similarity_matrix = None
        self._update_matrices()
    
    def _update_matrices(self):
        """Update user-item matrix and similarity matrix"""
        # Create user-item matrix
        self.user_item_matrix = pd.pivot_table(
            self.interactions_df,
            values='rating',
            index='user_id',
            columns='product_id',
            fill_value=0
        )
        
        # Calculate user similarity matrix using cosine similarity
        self.similarity_matrix = cosine_similarity(self.user_item_matrix)
        
    def add_interaction(self, user_id, product_id, rating):
        """
        Add a new user-item interaction
        """
        new_interaction = pd.DataFrame({
            'user_id': [int(user_id)],
            'product_id': [int(product_id)],
            'rating': [float(rating)]
        })
        self.interactions_df = pd.concat([self.interactions_df, new_interaction], ignore_index=True)
        self._update_matrices()
    
    def get_recommendations(self, user_id, n_recommendations=5):
        """
        Get top N recommendations for a user using collaborative filtering
        """
        if user_id not in self.user_item_matrix.index:
            return []
            
        # Get user's index in the similarity matrix
        user_idx = list(self.user_item_matrix.index).index(user_id)
        
        # Get similar users
        similar_users = self.similarity_matrix[user_idx]
        
        # Get products that similar users liked but the target user hasn't rated
        user_products = set(self.interactions_df[
            self.interactions_df['user_id'] == user_id
        ]['product_id'])
        
        # Calculate product scores based on similar users' ratings
        product_scores = {}
        for other_user_id in self.user_item_matrix.index:
            if other_user_id == user_id:
                continue
                
            similarity = similar_users[list(self.user_item_matrix.index).index(other_user_id)]
            
            # Get products rated by the other user
            other_user_ratings = self.interactions_df[
                self.interactions_df['user_id'] == other_user_id
            ]
            
            for _, row in other_user_ratings.iterrows():
                if row['product_id'] not in user_products:
                    if row['product_id'] not in product_scores:
                        product_scores[row['product_id']] = 0
                    product_scores[row['product_id']] += float(similarity * row['rating'])
        
        # Sort products by score and return top N
        recommended_products = sorted(
            product_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )[:n_recommendations]
        
        return [{'product_id': int(p[0]), 'score': float(p[1])} for p in recommended_products]
