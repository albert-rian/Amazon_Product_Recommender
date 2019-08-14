from flask import Flask, send_from_directory, render_template, request, redirect, url_for
import pandas as pd
import numpy as np
import random
import json
import joblib
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from pandas import DataFrame
from ast import literal_eval

app = Flask(__name__, static_url_path='')         

df_Reviews_Simple = pd.read_csv('Reviews_simple.csv')
df_Data = pd.read_csv('metaData_clean.csv')

df_Data = df_Data.fillna({    
    'description' : 'No description available.',
    'brand' : 'Unknown brand'
})
df_Data['price'] = round(df_Data['price'], 2)

df_content_based = pd.read_csv('metaData_for_contentbased.csv', converters={"categories": lambda x: x.replace("'", "").strip("[]").split(", ")})
df_content_based = df_content_based.drop('Unnamed: 0', 1)

# ===========================================================================================
# ML model for PB
df_sum_clean_PB = pd.read_csv('reviews_clean_PB.csv', index_col = 0)
df_sum_clean_PB = df_sum_clean_PB.drop(['index'], axis = 1)

docs = df_sum_clean_PB['Summary_Clean']
vect = CountVectorizer(max_features = 100, stop_words = 'english')
X = vect.fit_transform(docs)

df_feature_names = DataFrame(X.A, columns = vect.get_feature_names())
df_feature_names = df_feature_names.astype(int)

X_PB = np.array(df_feature_names)

# ===========================================================================================
# ML model for UB
df_sum_clean_UB = pd.read_csv('reviews_clean_UB.csv', index_col = 0)
df_sum_clean_UB = df_sum_clean_UB.drop(['index'], axis = 1)

docs = df_sum_clean_UB['Summary_Clean']
vect = CountVectorizer(max_features = 100, stop_words = 'english')
X = vect.fit_transform(docs)

df_feature_names = DataFrame(X.A, columns = vect.get_feature_names())
df_feature_names = df_feature_names.astype(int)

X_UB = np.array(df_feature_names)

# ===========================================================================================
# home route
@app.route('/')
def home():
    prod_of_the_day = []
    for i in range(len(df_sum_clean_PB)):
        if df_sum_clean_PB['AvgScore'][i] >= 4.5:
            prod_of_the_day.append(df_sum_clean_PB['ProductId'][i])
    prod_of_the_day = random.sample(prod_of_the_day, 5)

    prod1 = [
        df_Data[df_Data['asin'] == prod_of_the_day[0]]['title'].values[0], 
        df_Data[df_Data['asin'] == prod_of_the_day[0]]['price'].values[0], 
        df_Data[df_Data['asin'] == prod_of_the_day[0]]['imUrl'].values[0]
    ]
    prod2 = [
        df_Data[df_Data['asin'] == prod_of_the_day[1]]['title'].values[0], 
        df_Data[df_Data['asin'] == prod_of_the_day[1]]['price'].values[0], 
        df_Data[df_Data['asin'] == prod_of_the_day[1]]['imUrl'].values[0]
    ]
    prod3 = [
        df_Data[df_Data['asin'] == prod_of_the_day[2]]['title'].values[0], 
        df_Data[df_Data['asin'] == prod_of_the_day[2]]['price'].values[0], 
        df_Data[df_Data['asin'] == prod_of_the_day[2]]['imUrl'].values[0]
    ]
    prod4 = [
        df_Data[df_Data['asin'] == prod_of_the_day[3]]['title'].values[0], 
        df_Data[df_Data['asin'] == prod_of_the_day[3]]['price'].values[0], 
        df_Data[df_Data['asin'] == prod_of_the_day[3]]['imUrl'].values[0]
    ]
    prod5 = [
        df_Data[df_Data['asin'] == prod_of_the_day[4]]['title'].values[0], 
        df_Data[df_Data['asin'] == prod_of_the_day[4]]['price'].values[0], 
        df_Data[df_Data['asin'] == prod_of_the_day[4]]['imUrl'].values[0]
    ]
    POTD = prod_of_the_day
    return render_template('home.html', 
        prod1 = prod1, prod2 = prod2, prod3 = prod3, prod4 = prod4, prod5 = prod5, 
        POTD = POTD
    )

# login page
@app.route('/login')
def login():
    return render_template('login.html')
    
# POST login
@app.route('/postlogin', methods = ['POST'])
def postlogin():
    df_new_user = pd.read_json('data_cust.json')
    UserName = request.form['nama']      
    if UserName in df_Reviews_Simple['UserName'].values or UserName in df_new_user['UserName'].values:
        return redirect(url_for('suksesLogin', UserName = UserName))
    else:
        return redirect(url_for('gagalLogin', UserName = UserName))

# success login
@app.route('/successlogin/<string:UserName>')
def suksesLogin(UserName):
    user_purchase_history = []
    df_new_user = pd.read_json('data_cust.json')

    if UserName in df_new_user['UserName'].values:
        for i in range(10):
            user_purchase_history.append(['No purchase history', 'No product.'])

        prod_of_the_day = []
        for i in range(len(df_sum_clean_PB)):
            if df_sum_clean_PB['AvgScore'][i] >= 4.5:
                prod_of_the_day.append(df_sum_clean_PB['ProductId'][i])
        prod_of_the_day = random.sample(prod_of_the_day, 5)

        prodRec = []
        for i in range(len(prod_of_the_day)):
            rec_i = [
                prod_of_the_day[i],
                df_Data[df_Data['asin'] == prod_of_the_day[i]]['title'].values[0],
                df_Data[df_Data['asin'] == prod_of_the_day[i]]['imUrl'].values[0]
            ]
            prodRec.append(rec_i)
        line_rec = 'Buy our products of the day: '
    else:
        UserId= df_Reviews_Simple[df_Reviews_Simple['UserName'] == UserName]['UserId'].values[0]
        UserIndex = df_sum_clean_UB[df_sum_clean_UB['UserId'] == UserId].index.values[0]
        for i in range(len(df_Reviews_Simple)):
            if df_Reviews_Simple['UserId'][i] == UserId:
                bought_product_i = []
                bought_product_i.append(df_Reviews_Simple['ProductId'][i])
                bought_product_i.append(df_Data[df_Data['asin'] == df_Reviews_Simple['ProductId'][i]]['title'].values[0])
                user_purchase_history.append(bought_product_i)

        rec_array = model_UB.kneighbors([X_UB[UserIndex]])[1][0]
        y = []
        for i in rec_array:
            y.append(i)
        rec_array = y
        rec_array = random.sample(rec_array, k = 5)
        
        list_prodRec = []
        for m in range(len(df_Reviews_Simple)):
            if (df_Reviews_Simple["UserId"][m] == df_sum_clean_UB["UserId"][rec_array[0]]) & (df_Reviews_Simple["Score"][m] >= 4):
                list_prodRec.append(df_Reviews_Simple['ProductId'][m])

        if len(list_prodRec) >= 5:
            k = 5
        else:
            k = len(list_prodRec)

        list_prodRec = random.sample(list_prodRec, k)

        prodRec = []
        for i in list_prodRec:
            rec_i = [
                i,
                df_Data[df_Data['asin'] == i]['title'].values[0],  
                df_Data[df_Data['asin'] == i]['imUrl'].values[0]
            ]
            prodRec.append(rec_i)
        line_rec = 'Our product recommendations tailored for your interest: '

    return render_template('login_success.html', 
        UserName = UserName, user_purchase_history = user_purchase_history, prodRec = prodRec, line_rec = line_rec
    )

# fail login
@app.route('/faillogin/<string:UserName>')
def gagalLogin(UserName):
    return render_template('login_fail.html', UserName = UserName)

# signup page
@app.route('/signup')
def html2():
    return render_template('signup.html')

# POST signup
@app.route('/postsignup', methods = ['POST'])
def postsignup():
    UserName = request.form['nama']   
    with open('data_cust.json') as data:
        data_cust_json = json.load(data) 
    df_new_user = pd.read_json('data_cust.json')

    if UserName in df_Reviews_Simple['UserName'].values or UserName in df_new_user['UserName'].values:
        return redirect(url_for('gagalSignup', UserName = UserName))
    else:
        x = {'UserName' : ''}
        x['UserName'] = UserName
        data_cust_json.append(x)
        jsonku = open('data_cust.json', 'w')
        jsonku.write(str(json.dumps(data_cust_json)))
        return redirect(url_for('suksesSignup', UserName = UserName))

# success sign up
@app.route('/suksessignup/<string:UserName>')
def suksesSignup(UserName):
    return render_template('signup_success.html', UserName = UserName)

# fail sign up
@app.route('/gagalsignup/<string:UserName>')
def gagalSignup(UserName):
    return render_template('signup_fail.html', UserName = UserName)

# Product Page
@app.route('/postproduct', methods = ['POST'])
def post():
    ProductId = request.form['ProductId']
    if ProductId not in df_Data['asin'].values:
        return render_template('error.html')
    else:
        return redirect(url_for('product', ProductId = ProductId))

# Buy product page
@app.route('/buyproduct')
def buyproduct():
    prod_of_the_day = []
    for i in range(len(df_sum_clean_PB)):
        if df_sum_clean_PB['AvgScore'][i] >= 4.5:
            prod_of_the_day.append(df_sum_clean_PB['ProductId'][i])
    prod_of_the_day = random.sample(prod_of_the_day, 5)

    prodRec = []
    for i in range(len(prod_of_the_day)):
        rec_i = [
            prod_of_the_day[i],
            df_Data[df_Data['asin'] == prod_of_the_day[i]]['title'].values[0],
            df_Data[df_Data['asin'] == prod_of_the_day[i]]['imUrl'].values[0]
        ]
        prodRec.append(rec_i)
    return render_template('buy.html', prodRec = prodRec)

@app.route('/product/<string:ProductId>')
def product(ProductId):   
    prodCat = [df_Data[df_Data['asin'] == ProductId]['categories'].values[0].strip('[]')]

    if len(df_content_based[df_content_based['asin'] == ProductId]['categories'].values[0]) > 1:
        prod_sub_cat = df_content_based[df_content_based['asin'] == ProductId]['categories'].values[0][1]
    else:
        prod_sub_cat = df_content_based[df_content_based['asin'] == ProductId]['categories'].values[0][0]
    
    prod_brand = df_content_based[df_content_based['asin'] == ProductId]['brand'].values[0]
    
    similar_sub_cat = []
    similar_brand = []

    for i in range(len(df_content_based)):
        if prod_sub_cat in df_content_based['categories'].iloc[i]:
            similar_sub_cat.append(df_content_based['asin'].iloc[i])
        if df_content_based['brand'].iloc[i] == prod_brand:
            similar_brand.append(df_content_based['asin'].iloc[i])

    prod_of_the_day = []
    for i in range(len(df_sum_clean_PB)):
        if df_sum_clean_PB['AvgScore'][i] >= 4.5:
            prod_of_the_day.append(df_sum_clean_PB['ProductId'][i])
    prod_of_the_day = random.sample(prod_of_the_day, 5)

    for i in range(3):
        if len(similar_sub_cat) < 3:
            similar_sub_cat.append(prod_of_the_day[i])
        elif len(similar_sub_cat) == 3:
            break
    
    if len(similar_brand) == 0:
        similar_brand.append(prod_of_the_day[3])
        similar_brand.append(prod_of_the_day[4])
    if len(similar_brand) == 1:
        similar_brand.append(prod_of_the_day[3])

    similar_sub_cat = random.sample(similar_sub_cat, k = 3)
    similar_brand = random.sample(similar_brand, k = 2)
    
    if ProductId in df_sum_clean_PB['ProductId'].values:
        prodIndex = df_sum_clean_PB[df_sum_clean_PB['ProductId'] == ProductId].index.values[0]
        rec_array = model_PB.kneighbors([X_PB[prodIndex]])[1][0]
        y = []
        for i in rec_array:
            y.append(i)
        rec_array = y
        rec_array = random.sample(rec_array, k = 5)

        prodRec = []
        for i in range(5):
            product_recommend_Id = df_sum_clean_PB['ProductId'][rec_array[i]]
            rec_i = [
                product_recommend_Id,
                df_Data[df_Data['asin'] == product_recommend_Id]['title'].values[0],  
                df_Data[df_Data['asin'] == product_recommend_Id]['imUrl'].values[0]
            ]
            prodRec.append(rec_i)
        
        for i in range(3):
            rec_i = [
                similar_sub_cat[i],
                df_Data[df_Data['asin'] == similar_sub_cat[i]]['title'].values[0],  
                df_Data[df_Data['asin'] == similar_sub_cat[i]]['imUrl'].values[0]
            ]
            prodRec.append(rec_i)  
            
        for i in range(2):
            rec_i = [
                similar_brand[i],
                df_Data[df_Data['asin'] == similar_brand[i]]['title'].values[0],  
                df_Data[df_Data['asin'] == similar_brand[i]]['imUrl'].values[0]
            ]
            prodRec.append(rec_i)

        line_rec_1 = 'Based on the product above, here\'s our recommendations:'
        line_rec_2 = 'These products also has similar sub-category and brand:'
    else:
        prod_of_the_day = []
        for i in range(len(df_sum_clean_PB)):
            if df_sum_clean_PB['AvgScore'][i] >= 4.5:
                prod_of_the_day.append(df_sum_clean_PB['ProductId'][i])
        prod_of_the_day = random.sample(prod_of_the_day, 5)

        prodRec = []
        for i in range(len(prod_of_the_day)):
            rec_i = [
                prod_of_the_day[i],
                df_Data[df_Data['asin'] == prod_of_the_day[i]]['title'].values[0],
                df_Data[df_Data['asin'] == prod_of_the_day[i]]['imUrl'].values[0]
            ]
            prodRec.append(rec_i)

        for i in range(3):
            rec_i = [
                similar_sub_cat[i],
                df_Data[df_Data['asin'] == similar_sub_cat[i]]['title'].values[0],  
                df_Data[df_Data['asin'] == similar_sub_cat[i]]['imUrl'].values[0]
            ]
            prodRec.append(rec_i)  
            
        for i in range(2):
            rec_i = [
                similar_brand[i],
                df_Data[df_Data['asin'] == similar_brand[i]]['title'].values[0],  
                df_Data[df_Data['asin'] == similar_brand[i]]['imUrl'].values[0]
            ]
            prodRec.append(rec_i)

        line_rec_1 = 'This product hasn\'t had 100 reviews yet, but here\'s our recommendation:'
        line_rec_2 = 'These products also have similar sub-category and brand:'
        
    return render_template('product.html', 
        df_Data = df_Data, ProductId = ProductId, prodCat = prodCat, prodRec = prodRec, line_rec_1 = line_rec_1, line_rec_2 = line_rec_2
    )

# data visualization
@app.route('/visualization')
def visual():
    return render_template('visualization.html')

@app.route('/visualization/brand')
def brand():
    return render_template('brand.html')

@app.route('/visualization/postbrand', methods = ['POST'])
def postbrand():
    rank = request.form['rank']
    return redirect(url_for('topbrands', rank = rank))

@app.route('/topbrands/<int:rank>')
def topbrands(rank):
    if rank == 1:
        brand = 'Dorman'
    elif rank == 2:
        brand = 'ACDelco'
    elif rank == 3:
        brand = 'WeatherTech'
    elif rank == 4:
        brand = 'TYC'
    elif rank == 5:
        brand = 'K&N'
    elif rank == 6:
        brand = 'Beck Arnley'
    elif rank == 7:
        brand = 'Monroe'
    elif rank == 8:
        brand = 'Depo'
    elif rank == 9:
        brand = 'Bosch'
    elif rank == 10:
        brand = 'Raybestos' 

    return render_template('brandhist.html', rank = rank, brand = brand)

@app.route('/visualization/score')
def score():
    return render_template('score.html')

@app.route('/visualization/postscore', methods = ['POST'])
def postscore():
    score = request.form['score']
    return redirect(url_for('extremescore', score = score))

@app.route('/extremescore/<int:score>')
def extremescore(score):
    if score == 1:
        a = 'hist_score_1star.png'
        b = 'hist_score_1star_50up.png'
    elif score == 5:
        a = 'hist_score_5stars.png'
        b = 'hist_score_5stars_500up.png'
    return render_template('scorehist.html', a = a, b = b, score = score)

@app.route('/visualization/wordcloud')
def wordcloud():
    return render_template('wordcloud.html')

@app.route('/visualization/categories')
def categories():
    return render_template('categories.html')

@app.route('/visualization/price')
def price():
    return render_template('price.html')

# 404 route
@app.errorhandler(404)
def error404(error):
    return render_template('error.html')

if __name__ == '__main__':
    model_PB = joblib.load('ML_PB.joblib')
    model_UB = joblib.load('ML_UB.joblib')
    app.run(debug = True)

