from flask import Flask, render_template, request
import pandas as pd

app = Flask(__name__)

data = pd.read_csv('cleaned_cabs.csv')

def recommend_ride(data, origin, destination, day_of_week, hour):
    filtered_data = data[
        (data['origin'] == origin) &
        (data['destination'] == destination) &
        (data['day_of_week'] == day_of_week)
    ]

    if hour in filtered_data['hour'].unique():
        grouped_data = filtered_data.groupby(['car_category', 'car_type'])['price'].mean()

        recommendations = []
        for car_category in data['car_category'].unique():
            try:
                category_data = grouped_data.loc[car_category]
                if not category_data.empty:
                    category_recommendations = []
                    for car_type, avg_price in category_data.items():
                        category_recommendations.append(f"{car_type}: ${avg_price:.2f}")

                    cheapest_option = category_data.idxmin()
                    suggestion = 'No data available' if pd.isnull(cheapest_option) else cheapest_option
                    recommendations.append({
                        'car_category': f"{car_category}",
                        'recommendations': category_recommendations,
                        'suggestion': f"We suggest using {suggestion}"
                    })
                else:
                    recommendations.append({
                        'car_category': f"{car_category}",
                        'recommendations': ["No data available for this car category in this hour"],
                        'suggestion': ""
                    })
            except KeyError:
                recommendations.append({
                    'car_category': f"{car_category}",
                    'recommendations': ["No data available for this car category"],
                    'suggestion': ""
                })

        return recommendations
    else:
        daily_filtered_data = filtered_data[filtered_data['hour'] != hour]
        daily_grouped_data = daily_filtered_data.groupby(['car_category', 'car_type'])['price'].mean()

        recommendations = []
        for car_category in data['car_category'].unique():
            try:
                category_data = daily_grouped_data.loc[car_category]
                category_recommendations = []
                for car_type, avg_price in category_data.items():
                    category_recommendations.append(f"{car_type}: ${avg_price:.2f}")

                cheapest_option = category_data.idxmin()
                suggestion = 'No data available' if pd.isnull(cheapest_option) else cheapest_option
                recommendations.append({
                    'car_category': f"{car_category}",
                    'recommendations': category_recommendations,
                    'suggestion': f"We suggest using {suggestion}"
                })
            except KeyError:
                recommendations.append({
                    'car_category': f"{car_category}",
                    'recommendations': ["No data available for this car category"],
                    'suggestion': ""
                })

        return recommendations

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/recommend', methods=['POST'])
def recommend():
    if request.method == 'POST':
        user_origin = request.form['origin']
        user_destination = request.form['destination']
        user_day_of_week = request.form['day_of_week']
        user_hour = int(request.form['hour'])

        result = recommend_ride(data, user_origin, user_destination, user_day_of_week, user_hour)
        return render_template('recommendation.html', result=result)

if __name__ == '__main__':
    app.run(debug=True)
