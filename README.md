# Dining Suggestion Chatbot

In this Project, I developed a serverless web chatbot with event-driven microservices using AWS S3, API Gateway, Lambda, Simple Queue Service, Amazon Lex, CloudWatch, Simple Email Service.  I also built a recommendation pipeline to suggest restaurants based on user inputs using OpenSearch Service, DynamoDB, and Yelp API.

### Working Principle
Based on the conversation between chatbot and customer, chatbot collects the information from customers like location, cuisine, number of people, email address. Then, chatbot will search through ElasticSearch (OpenSearch Service) to get suggestions of restaurant IDs with their perference, especially cuisine. Moreover, the web application will also query the DynamoDB table with these restaurant IDs to get more information about the restaurants and send email to the customers.

### Example Dialogue
Chatbot: Hi there, I'm your personal Concierge. How can I help? <br>

User: Hello.<br>

Chatbot: Hello there! What can I help you with?<br>

User: I need some dining suggestions.<br>

Chatbot: Great. I can help you with that. What city or city area are you looking to dine in?<br>

User: New York.<br>

Chatbot: What cuisine would you like to try?<br>

User: Chinese.<br>

Chatbot: How many people are there in your party?<br>

User: 5.<br>

Chatbot: What date would you like to dine in?<br>

User: Tomorrow.<br>

Chatbot: What time?<br>

User: 6pm.<br>

Chatbot: What is your email address?<br>

User: ezhao19990516@gmail.com<br>

Chatbot: I have received your request and will be sending the suggestions shortly. Have a Great Day !!<br>

User: Thank you. <br>

Chatbot: You are welcome.<br>

(a few minutes later)<br>

User will get an email with the following content:<br>
Hello! Here are my Chinese restaurant suggestions for 5 people, for 2023-02-26 at 18:00 : 1. Friendly Restaurant located at 1205 40th Ave, 2. Mala Project located at 245 East 53rd St, 3. Shu Han Ju located at 465 6th Ave. Enjoy your meal!<br>


### Built With
1. [S3](https://aws.amazon.com/s3/) - Used to host static frontend
2. [API Gateway](https://aws.amazon.com/api-gateway/) - For creating, monitoring, and securing REST APIs at any scale.
3. [Lambda](https://aws.amazon.com/lambda/) - Function as a Service,  event-driven, and serverless computing platform. Acted as backend to run code without provisioning or managing servers.
4. [Lex](https://aws.amazon.com/lex/) - Amazon platform to build conversational bots (lex V2).
5. [Simple Queue Service](https://aws.amazon.com/sqs/) - Message queue for communication between microservices.
6. [Simple Email Service](https://aws.amazon.com/ses/) - A cost-effective, flexible, and scalable email service.
7. [DynamoDB](https://aws.amazon.com/dynamodb/) - NoSQL database.
8. [Yelp API](https://www.yelp.com/fusion) - Scrape restaurant information.
9. [CloudWatch](https://aws.amazon.com/cloudwatch/) - Observe and monitor resources and applications on AWS.

### Architecture
![image](Architecture.png)
