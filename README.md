# Dining Suggestion Chatbot

In this Project, I developed a serverless web chatbot with event-driven microservices using AWS S3, API Gateway, Lambda, Simple Queue Service, Amazon Lex, CloudWatch, Simple Email Service.  I also built a recommendation pipeline to suggest restaurants based on user inputs using OpenSearch Service, DynamoDB, and Yelp API. The website can be accessed at: https://6998hw1bucket.s3.amazonaws.com/chatbot.html

### Working Principle
Based on the conversation between chatbot and customer, chatbot collects the information from customers like location, cuisine, number of people, email address. Then, chatbot will search through ElasticSearch (OpenSearch Service) to get suggestions of restaurant IDs with their perference, especially cuisine. Moreover, the web application will also query the DynamoDB table with these restaurant IDs to get more information about the restaurants and send email to the customers.

### Example Dialogue
Chatbot: Hi there, I'm your personal Concierge. How can I help? <br>
User: Hello.
Chatbot: Hello there! What can I help you with?
User: I need some dining suggestions.
Chatbot: Great. I can help you with that. What city or city area are you looking to dine in?
User: New York.
Chatbot: What cuisine would you like to try?
User: Chinese.
Chatbot: How many people are there in your party?
User: 5.
Chatbot: What date would you like to dine in?
User: Tomorrow.
Chatbot: What time?
User: 6pm.
Chatbot: What is your email address?
User: ezhao19990516@gmail.com
Chatbot: I have received your request and will be sending the suggestions shortly. Have a Great Day !!
User: Thank you
Chatbot: You are welcome.

(a few minutes later)

User will get an email with the following content:
Hello! Here are my Chinese restaurant suggestions for 5 people, for 2023-02-26 at 18:00 : 1. Friendly Restaurant located at 1205 40th Ave, 2. Mala Project located at 245 East 53rd St, 3. Shu Han Ju located at 465 6th Ave. Enjoy your meal!






