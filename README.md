# Product Recommendation System

## Overview

This repository hosts the **Product Recommendation System**, designed to deliver personalized product suggestions using **Collaborative Filtering** and **Content-Based Filtering**. By leveraging user behavior and product features, the system offers a robust solution for personalized recommendations.

## Features

- **Data Preprocessing**: 
  - Handling duplicates, null values, and simplifying product names.
  - Generating tags based on product attributes (brand, category, description).
  
- **Content-Based Filtering**:
  - **TF-IDF Vectorization** to convert text-based product tags into numerical vectors.
  - **Cosine Similarity** to recommend similar products based on tags.
  
- **Collaborative Filtering**:
  - Constructing a user-item matrix to analyze user-product interactions.
  - Using **K-Nearest Neighbors (KNN)** to recommend products based on user similarities.

- **Seasonality-Based Recommendations**: 
  - Filtering products based on the current season using timestamp data.

- **User Preferences**: 
  - Storing user preferences in a database and recommending products based on these preferences.

- **Hybrid Recommendation System**: 
  - Combining content-based and collaborative filtering for more accurate and diverse recommendations.

How It Works
Collaborative Filtering: Recommendations based on user interactions (ratings and behavior).
Content-Based Filtering: Recommendations based on product tags (brand, category, description).
Seasonality-Based Filtering: Dynamic recommendations based on current time/season.
Hybrid Recommendations: Combining both methods to offer the most accurate suggestions.

API Endpoints
/suggestions: Fetch personalized recommendations based on user preferences and seasonality.
