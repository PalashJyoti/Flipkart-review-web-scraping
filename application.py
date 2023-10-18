from flask import Flask, render_template, request, jsonify
from flask_cors import CORS, cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq

application = Flask(__name__)
app=application

@app.route("/",methods=['GET'])
@cross_origin()
def homepage():
    return render_template('index.html')

@app.route('/review',methods=['POST', 'GET'])
@cross_origin()
def index():
    if request.method=='POST':
        try:
            searchString=request.form['content'].replace(" ","")
            flipkart_url = "https://www.flipkart.com/search?q=" + searchString
            response = requests.get(flipkart_url)
            flipkartpage=response.text
            flipkart_html = bs(flipkartpage,"html.parser")
            bigboxes = flipkart_html.find_all("div",{"class":"_1AtVbE col-12-12"})
            del bigboxes[0:3]
            box=bigboxes[0]
            productlink = "https://www.flipkart.com" + box.div.div.div.a['href']
            productreq = requests.get(productlink)
            productreq.encoding='utf-8'
            product_html = bs(productreq.text,"html.parser")
            comment_boxes = product_html.find_all("div",{"class":"_16PBlm"})
            
            filename=searchString+'.csv'
            fw=open(filename,'w')
            headers="Product, Customer Name, Rating, Heading, Comment \n"
            fw.write(headers)
            reviews=[]
            for comment_box in comment_boxes:
                try:
                    name=comment_box.div.div.find_all("p",{"class":"_2sc7ZR _2V5EHH"})[0].text
                except:
                    name='No Name'
                
                try:
                    rating=comment_box.div.div.div.div.text
                except:
                    rating='No Rating'
                    
                try:
                    commentHead=comment_box.div.div.p.text
                except:
                    commentHead="No Comment Heading"
                    
                try:
                    custComment=comment_box.div.div.find_all("div",{"class":""})[1].text
                except Exception as e:
                    print("Exception while creating dictionary: ",e)
                    
                mydict={'Product':searchString, 'Name':name, 'Rating':rating, 'CommentHead':commentHead, 'Comment':custComment}
                reviews.append(mydict)
                
            return render_template('results.html',reviews=reviews[0:(len(reviews)-1)])
        except Exception as e:
            print("Error occurred: ",e)


if __name__=="__main__":
    app.run(host="0.0.0.0",port=8000,debug=True)