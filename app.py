import bcrypt
import pandas as pd

from flask_sqlalchemy import SQLAlchemy
from flask import Flask, request,render_template, redirect,session, flash, get_flashed_messages
from werkzeug.exceptions import BadRequestKeyError

from sklearn.metrics.pairwise import linear_kernel
from sklearn.feature_extraction.text import TfidfVectorizer


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)
app.secret_key = 'secret_key'

hotels = pd.read_csv("Dataset/Hotels.csv")

def recommend_hotels(df,min_price,max_price,top_n=10):
    recommended_hotels= df[ (df["PRICE_RUPEES"]>=min_price) & (df["PRICE_RUPEES"]<=max_price) ]
    recommended_hotels= recommended_hotels.sort_values(by="NUMBER_OF_REVIEWS",ascending=False).head(top_n)
    recommended_hotels= recommended_hotels.drop(columns=["NUMBER_OF_REVIEWS"])
    if not recommended_hotels.empty:
        return recommended_hotels
    else:
        return "sorry, hotels are not available in this price range..."

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

    def __init__(self,email,password,name):
        self.name = name
        self.email = email
        self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self,password):
        return bcrypt.checkpw(password.encode('utf-8'),self.password.encode('utf-8'))

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('loginform.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            flash('User with this email already exists. Please use a different email.', 'danger')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='danger')
        elif len(name) < 2:
            flash('First name must be greater than 1 character.', category='danger')
        elif len(password) < 7:
            flash('Password must be at least 7 characters.', category='danger')    
        else:
            new_user = User(name=name, email=email, password=password)
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful. You can now log in.', 'success')
            return redirect('/login')

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            session['email'] = user.email
            flash('Login Successfull!', 'success')
            return redirect('dashboard')
        
        else:
            flash('Invalid email or password. Please try again.', 'danger')

    return render_template('login.html')


@app.route('/dashboard')
def dashboard():
    if session['email']:
        user = User.query.filter_by(email=session['email']).first()
        return render_template('dashboard.html',user=user)
    
    return redirect('/login')

@app.route('/places', methods=['GET', 'POST'])
def recommend_places():
    try:
        user_preferences = request.form["preferences"].split(", ")
        top_n = int(request.form["top-n"])
    except ValueError:  
        return render_template("places.html", places="Empty", trigger=True)
    
    except BadRequestKeyError:  
        return render_template("places.html", places="Empty", trigger=True)
    
    data = pd.read_csv('Dataset/final_Types.csv', encoding='latin-1')   
    
    tfidf_vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf_vectorizer.fit_transform(data['Combined_Priorities'])

    user_preferences = [pref.lower() for pref in user_preferences]
    user_pref_vector = tfidf_vectorizer.transform(user_preferences)

    cosine_similarities = linear_kernel(user_pref_vector, tfidf_matrix).flatten()

    recommended_indices = cosine_similarities.argsort()[::-1][:top_n]
    recommended_places = data.iloc[recommended_indices]

    if not recommended_places.empty:
        final_list = []
    
        for index, row in recommended_places.iterrows():
            place_name = row['POIs']
            image_path = r""+row['image_path']
            info = row["INFO"]  
            link = f'https://www.google.com/maps/place/{row["LATITUDE"]},{row["LONGITUDE"]}'
            
            final_list.append([place_name, info, link, image_path])
            
        return render_template("places.html", places=final_list, top_n=top_n, trigger=False, user_preferences=user_preferences)

    else:
        return render_template("places.html"    , places="Please enter a range.", trigger=True)
    


@app.route('/hotels/', methods=['GET', 'POST'])
def recommend_hotels():
    try:
        min_price = float(request.form["min-price"])
        max_price = float(request.form["max-price"])
        top_n = int(request.form["top-n"])
    
    except ValueError:
        return render_template("hotels.html", hotels="Please enter a range.", trigger=True)
    
    except BadRequestKeyError:
        return render_template("hotels.html")
    

    df = pd.read_csv(r"./Dataset/Hotels.csv")

    recommended_hotels= df[ (df["PRICE_RUPEES"]>=min_price) & (df["PRICE_RUPEES"]<=max_price) ]
    recommended_hotels= recommended_hotels.sort_values(by="NUMBER_OF_REVIEWS",ascending=False).head(top_n)
    recommended_hotels= recommended_hotels.drop(columns=["NUMBER_OF_REVIEWS"])

    final_list = []        

    if not recommended_hotels.empty:
        for index, row in recommended_hotels.iterrows():
            place_name = row['HOTEL']
            price=row["PRICE_RUPEES"]
            link = f'https://www.google.com/maps/place/{row["Lat"]},{row["Lng"]}'

            final_list.append([place_name, price, link])

        return render_template("hotels.html", hotels=final_list, trigger=False, top_n=top_n, min_price=min_price, max_price=max_price)
            
    else:
        return render_template("hotels.html", hotels="No hotels found in this price range.", trigger=True)


@app.route('/restaurants', methods=['GET', 'POST'])
def recommend_restaurants():
    try:
        user_category = request.form["category"]
        is_vegetarian = request.form["is-veg"]
        max_cost = float(request.form["max-cost"])
        user_cuisine = request.form["cuisine"]
        top_n = int(request.form["top-n"])

    except ValueError:
        return render_template("restaurants.html", restaurants="Empty field detected", trigger=True)

    except BadRequestKeyError:
        return render_template("restaurants.html")
        
    data_food = pd.read_csv(r"./Dataset/zom_jaipur.csv", encoding='latin1')
    
    if not pd.api.types.is_numeric_dtype(data_food['cost_for_two']):
        data_food =pd.read_csv(r"./Dataset/zom_jaipur.csv", encoding='latin1')
        data_food['cost_for_two'] = data_food['cost_for_two'].str.replace(',', '').astype(float)

    filtered_restaurants = data_food[
        (data_food['category'].str.contains(user_category, case=False, na=False)) &
        ((data_food['is_vegeterian'].str.lower() == 'yes') if is_vegetarian else (data_food['is_vegeterian'].str.lower() == 'no')) &
        (data_food['cost_for_two'] <= max_cost) &
        (data_food['Cuisine_offered'].str.contains(user_cuisine, case=False, na=False)) &
        (data_food["Location"])

    ]

    sorted_restaurants = filtered_restaurants.sort_values(by='avg_din_rate', ascending=False).head(top_n)
    
    final_list = []
    
    if len(sorted_restaurants)==0:
        return render_template("restaurants.html", restaurants="No restaurants found.", trigger=True)

    elif not sorted_restaurants.empty:
        for index, row in sorted_restaurants.iterrows():
            final_list.append([row['Name'], row['Location'], row['category'], row['is_bar_available'], row['cost_for_two'], row['avg_din_rate']])

        return render_template("restaurants.html", restaurants=final_list, trigger=False, user_category=user_category, is_vegetarian=is_vegetarian, max_cost=max_cost, user_cuisine=user_cuisine, top_n=top_n)
            
    else:
        return render_template("restaurants.html", restaurants=final_list, trigger=True, user_category=user_category, is_vegetarian=is_vegetarian, max_cost=max_cost, user_cuisine=user_cuisine, top_n=top_n)


@app.route('/feedback')
def feedback():
    return render_template('feedback.html')

@app.route('/maps')
def maps():
    return render_template('maps.html')

@app.route('/logout')
def logout():
    session.pop('email',None)
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True) 