from flask import Flask, jsonify, request, render_template
from recommender import RecommendationEngine
import pandas as pd
import numpy as np

app = Flask(__name__)

# Initialize the recommendation engine with sample data
# In a real application, this would be connected to your database
sample_data = {
    'user_id': [1, 1, 2, 2, 3, 3, 4],
    'product_id': [101, 102, 101, 103, 102, 103, 101],
    'rating': [5, 3, 4, 4, 1, 5, 4]
}
interactions_df = pd.DataFrame(sample_data)
recommender = RecommendationEngine(interactions_df)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/recommendations/<int:user_id>', methods=['GET'])
def get_recommendations(user_id):
    try:
        n_recommendations = int(request.args.get('n', 5))
        recommendations = recommender.get_recommendations(user_id, n_recommendations)
        return jsonify({
            'user_id': user_id,
            'recommendations': recommendations
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/record_interaction', methods=['POST'])
def record_interaction():
    try:
        data = request.json
        user_id = data['user_id']
        product_id = data['product_id']
        rating = data['rating']
        
        recommender.add_interaction(user_id, product_id, rating)
        return jsonify({'status': 'success', 'message': 'Interaction recorded successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)
