from datetime import datetime
import csv


from collections import defaultdict
import os
import pandas as pd


### prepare the data

weights = {'Average Rating': 4.456135881104034,
 'calories_kCal': 424.59341825902334,
 'Servings': 6.245222929936306,
 'recipe_prep_time': 17.072186836518046,
 '#ingredient': 8.801486199575372}

maxims = {'Average Rating': 4.91,
 'calories_kCal': 1595,
 'Servings': 35,
 'recipe_prep_time': 60.0,
 '#ingredient': 26}

minims = {'Average Rating': 3.63,
 'calories_kCal': 43,
 'Servings': 1,

 'recipe_prep_time': 5.0,
 '#ingredient': 1}

attributes = ['Average Rating','calories_kCal','Servings','recipe_prep_time','#ingredient']



def get_top_recommendations(user_input,healhiness, user_category,weights=weights):

    # read data
    data = pd.read_csv('./static/Data_csv/'+healhiness+'Recipes.csv')
    data = data.loc[data.category == user_category]

    data = data.loc[data['Average Rating'] >= user_input['Average Rating']]

    #data = data[attributes]

    sum_weights = sum(weights.values())
    id_distances = pd.DataFrame(columns = ['id','distance'])
    for i in data.index:
        distance = 0
        for j in attributes:
            distance += ( 1 - (abs(user_input[j] - float(data.at[i, j]))/ (maxims[j] - minims[j])))
    
        id_distances = id_distances.append({'id':data.at[i,'id'],'distance':distance}, ignore_index=True)

    recommendations = id_distances.sort_values('distance', ascending=True)[:5]['id'].values

    return list(recommendations)
  