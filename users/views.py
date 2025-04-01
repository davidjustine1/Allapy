from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
import pandas as pd
import os
from sklearn.metrics.pairwise import cosine_similarity


from django.conf import settings
from django.conf.urls.static import static


# Define file paths
DATASET_FILE = r"D:\Allapy\final_datasetHB.csv"

# Load dataset
df = pd.read_csv(DATASET_FILE)
df1 = df[['user_id', 'houseboat_name', 'rating']]

# Ensure user_id is treated as string for consistency
df1['user_id'] = df1['user_id'].astype(str)

# Create a user-item matrix (pivot table)
user_item_matrix = df1.pivot_table(index='user_id', columns='houseboat_name', values='rating')

# Function to calculate similarity between users
def calculate_user_similarity(user_item_matrix):
    user_item_matrix_filled = user_item_matrix.fillna(0)
    return cosine_similarity(user_item_matrix_filled)

# Compute similarity matrix
user_similarity = calculate_user_similarity(user_item_matrix)

# Create a DataFrame for user similarity
user_similarity_df = pd.DataFrame(user_similarity, index=user_item_matrix.index, columns=user_item_matrix.index)

def get_recommendation(user_id, user_similarity_df, user_item_matrix, n=5):
    user_id = str(user_id)
    similar_users = user_similarity_df[user_id].sort_values(ascending=False).index[1:]
    similar_users_ratings = user_item_matrix.loc[similar_users]
    weighted_ratings = similar_users_ratings.mean(axis=0)
    rated_HB = user_item_matrix.loc[user_id].dropna().index.tolist()
    unrated_HB = [hb for hb in weighted_ratings.index if hb not in rated_HB]
    recommended_HB = weighted_ratings[unrated_HB].sort_values(ascending=False).head(n)
    return recommended_HB.index.tolist(), recommended_HB.values.tolist()

def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'users/signup.html', {'form': form})

@login_required
def home_view(request):
    return render(request, 'users/home.html')

def logout_view(request):
    logout(request)
    return redirect('login')

def houseboat_detail(request, houseboat_id):
    return render(request, 'houseboat_detail.html', {'houseboat': houseboat})

@login_required
def recommendations_view(request):
    if request.method == 'POST':
        user_id = request.user.id
        capacity_filter = request.POST.get('capacity')
        bedrooms_filter = request.POST.get('bedrooms')
        rating_filter = request.POST.get('rating') 
        type_filter = request.POST.get('type')

        # Get base recommendations
        top_recommendations, ratings = get_recommendation(user_id, user_similarity_df, user_item_matrix, n=10)
        
        # Create a list of houseboat details
        houseboats = []
        for hb_name, rating in zip(top_recommendations, ratings):
            # Get houseboat details from the dataset
            hb_details = df[df['houseboat_name'] == hb_name].iloc[0]
            
            # Apply filters
            if capacity_filter != 'all':
                if int(hb_details['capacity']) > int(capacity_filter):
                    continue
                    
            if bedrooms_filter != 'all':
                if str(hb_details['bedrooms']) != bedrooms_filter:
                    continue
                    
            if rating_filter != 'all':
                if float(hb_details['rating']) < float(rating_filter):
                    continue
                    
            if type_filter != 'all':
                if hb_details['houseboat_type'].lower() != type_filter.lower():
                    continue
            
            # Add filtered houseboat to results
            houseboats.append({
                'name': hb_name,
                'rating': hb_details['rating'],
                'capacity': hb_details['capacity'],
                'bedrooms': hb_details['bedrooms'],
                'type': hb_details['houseboat_type'],
                'price': hb_details['final_price'],
                'id': hb_details['Sl No']
            })

        context = {
            'houseboats': houseboats,
            'filters': {
                'capacity': capacity_filter,
                'bedrooms': bedrooms_filter,
                'rating': rating_filter,
                'type': type_filter
            }
        }
        return render(request, 'users/recommendations.html', context)

    return redirect('home')
