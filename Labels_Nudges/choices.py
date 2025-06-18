#  (to_be stored, human-readable)


# ________________gender__________________
Gender_choices = [
    ('Male', 'Male'),
    ('Female', 'Female'),
    ('refuse_to_disc', 'Other / Prefer not to say')
]

# Gloria: Changing from party choices to topic choices, these might change. Here are the  rating choices/

environment_choices = [
    (1, '1 - Strongly disagree'),
    (2, '2'),
    (3, '3'),
    (4, '4'),
    (5, '5 - Strongly agree'),
]
weather_choices = [
    (1, '1 - Strongly disagree'),
    (2, '2'),
    (3, '3'),
    (4, '4'),
    (5, '5 - Strongly agree'),
]

green_living_choices = [
    (1, '1 - Strongly disagree'),
    (2, '2'),
    (3, '3'),
    (4, '4'),
    (5, '5 - Strongly agree'),
]


Age_choices = [
    (None, ''),
    ('under_18', 'Under 18'),
    ('b18_24', '18-24'),
    ('b25_35', '25-35'),
    ('b35_45', '35-45'),
    ('b45_55', '45-55'),
    ('over_55', 'Over 55')
]
DietRestrictions = [
    ('No_dietary_restrictions', 'No Dietary Restrictions'),
    ('Diabetes', 'Diabetes'),
    ('Gluten_free', 'Gluten-free'),
    ('Halal', 'Halal'),
    ('Kosher', 'Kosher'),
    ('Lactose_intolerance', 'Lactose intolerance'),
    ('Pescatarian', 'Pescatarian'),
    ('Vegetarian', 'Vegetarian'),
    ('Other', 'Other'),

]

DietGoal = [
    ('No_goals', 'No goals'),
    ('Eat_less_salt', 'Eat less salt'),
    ('Eat_less_sugar', 'Eat less sugar'),
    ('Eat_more_fruit', 'Eat more fruit'),
    ('Eat_more_protein', 'Eat more protein'),
    ('Eat_more_vegetables', 'Eat more vegetables'),
    ('Gain_weight', 'Gain weight'),
    ('Lose_weight', 'Lose weight'),
]

CookingExprience = [
    ('Very_Low', 'Very Low'),
    ('Low', 'Low'),
    ('Medium', 'Medium'),
    ('High', 'High'),
    ('Very High', 'Very high'),
]
EatingHabit = [
    ('Very_unhealthy', 'Very Unhealthy'),
    ('Unhealthy', 'Unhealthy'),
    ('Neither_healthy_no_unhealthy', 'Neither healthy, nor unhealthy'),
    ('Healthy', 'Healthy'),
    ('Very_Healthy', 'Very Healthy'),
]

EducationLevel = [
    (None, ''),
    ('Less_high_school', 'Less than high school'),
    ('High_school', 'High school or equivalent'),
    ('BA', 'Bachelor degree (e.g. BA, BSc)'),
    ('MSc', 'Master degree (e.g. MA, MSc)'),
    ('Doctorate', 'Doctorate (e.g. PhD)'),
    ('Not', 'Prefer not to say'),
]

foodCategories = [
    (None, ''),
    # ('Salad','Salad'),
    ('Fruits and Vegetables', 'Fruits and Vegetables'),
    # ('Seafood','Seafood'),
    ('Meat and Poultry', 'Meat and Poultry'),
    # ('Pasta and Noodles','Pasta and Noodles'),
    # ('Soups and Chili','Soups and Chili'),
    ('Barbecue', 'Barbecue'),
    ('Seafood Pasta and Noodles', 'Seafood Pasta and Noodles')
]

(Str_D, Str_N) = ('Strongly_Disagree', '1 - Strongly Disagree')
(Dis_D, Dis_N) = ('Disagree', '2')
(Nt_D, Nt_N) = ('Neutral', '3')
(Ag_D, Ag_N) = ('Agree', '4')
(StrAG_D, StrAG_N) = ('Strongly_Agree', '5 - Strongly Agree')

(Str_D2, Str_N2) = ('Red', 'Red')
(Dis_D2, Dis_N2) = ('Blue', 'Blue')
(Nt_D2, Nt_N2) = ('Green', 'Green')
(Ag_D2, Ag_N2) = ('Orange', 'Orange')
(StrAG_D2, StrAG_N2) = ('Brown', 'Brown')

FK__choices = [
    (Str_D, Str_N),
    (Dis_D, Dis_N),
    (Nt_D, Nt_N),
    (Ag_D, Ag_N),
    (StrAG_D, StrAG_N)
]

FK__choices2 = [
    (Str_D2, Str_N2),
    (Dis_D2, Dis_N2),
    (Nt_D2, Nt_N2),
    (Ag_D2, Ag_N2),
    (StrAG_D2, StrAG_N2)
]
