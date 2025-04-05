from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
import pandas as pd
import os
from sklearn.metrics.pairwise import cosine_similarity
from .models import Houseboat

from django.conf import settings
from django.conf.urls.static import static
from datetime import datetime, date


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
    # Get top 10 houseboats sorted by rating
    top_houseboats = df.nlargest(10, 'rating').apply(lambda x: {
        'id': x['Sl No'],
        'name': x['houseboat_name'],
        'rating': float(x['rating']),
        'capacity': x['capacity'],
        'bedrooms': x['bedrooms'],
        'type': x['houseboat_type'],
        'price': float(x['final_price']),
        'kiv_no': x['kiv_no'],
        'image_url': '/static/houseboat1.jpg'  # Add static image URL
    }, axis=1).tolist()
    
    return render(request, 'users/home.html', {
        'houseboats': top_houseboats,
        'user': request.user
    })

def logout_view(request):
    logout(request)
    return redirect('login')

def houseboat_detail(request, houseboat_id):
    try:
        hb_details = df[df['Sl No'] == int(houseboat_id)].iloc[0]
        
        # Get base price from dataset
        base_price = float(hb_details['final_price'])
        peak_price = base_price * 1.20  # 20% higher for peak season
        off_peak_price = base_price * 0.85  # 15% lower for off-peak season
        
        rating_float = float(hb_details['rating'])
        full_stars = int(rating_float)
        has_half_star = (rating_float - full_stars) >= 0.5
        
        context = {
            'name': hb_details['houseboat_name'],
            'capacity': hb_details['capacity'],
            'bedrooms': hb_details['bedrooms'],
            'rating': rating_float,
            'type': hb_details['houseboat_type'],
            'price': base_price,
            'peak_price': peak_price,
            'off_peak_price': off_peak_price,
            'kiv_no': hb_details['kiv_no'],
            'full_stars': range(full_stars),
            'has_half_star': has_half_star,
            'empty_stars': range(5 - full_stars - (1 if has_half_star else 0))
        }
        return render(request, 'users/houseboat_detail.html', context)
    except (IndexError, KeyError):
        return redirect('home')

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
                if int(hb_details['capacity']) < int(capacity_filter):
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

        # Sort houseboats by rating in descending order
        houseboats.sort(key=lambda x: float(x['rating']), reverse=True)
        
        # Add no_results flag to context
        no_results = len(houseboats) == 0
        
        context = {
            'houseboats': houseboats,
            'no_results': no_results,
            'filters': {
                'capacity': capacity_filter,
                'bedrooms': bedrooms_filter,
                'rating': rating_filter,
                'type': type_filter
            }
        }
        return render(request, 'users/recommendations.html', context)

    return redirect('home')

def calculate_price_with_rules(base_price_per_night, check_in_date_str, check_out_date_str, platform_fee_percent=10.0):
    # Add the calculate_price_with_rules function here from your code
    pass

def booking(request, houseboat_id):
    try:
        houseboat_details = df[df['Sl No'] == int(houseboat_id)].iloc[0]
        
        # Get base price from dataset
        base_price = float(houseboat_details['final_price'])
        
        context = {
            'houseboat': {
                'name': houseboat_details['houseboat_name'],
                'kiv_no': houseboat_details['kiv_no'],
                'price_per_night': base_price,
                'type': houseboat_details['houseboat_type'],
                'capacity': houseboat_details['capacity'],
                'bedrooms': houseboat_details['bedrooms']
            },
            'platform_fee': 10.0,  # 10% platform fee
            'today': date.today(),
        }
        
        return render(request, 'users/booking.html', context)
    except (IndexError, KeyError):
        return redirect('home')
