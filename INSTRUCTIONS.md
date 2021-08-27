# Numan Python take-home assignment: Instructions

Thank you for taking the time to work on this take-home technical challenge!

The assignment consists of two parts:

1. Review an existing pull request
2. Implement new functionality

Both of these will take place on GitHub, and more specifically on this repository, which has been created just for you.

# Existing System
In this repository you'll find a web service with simple functionality. It is implemented in Django 3 and Python 3
and it has a lot of the boilerplate code ready for you. It is a working service that serves a very basic API.

> ℹ️ No prior knowledge of Django is required for taking this assignment, however knowledge of other web frameworks
will certainly help. The existing codebase and the deliverables are designed in a way that completely avoids 
Django-specific features. Also, the existing code already contains a good deal of functionality you can use
as an example, such as how to perform a query using Django's ORM, as found in `main/views.py`:
> ```python
> BloodTestResults.objects.filter(user=request.user)
> ```

In order to help speed up things for you, we have compiled a list of [resources](#resources) on the most important
parts of Django you will need to use.

Please read the [README](/README.md) for more details on what the service does and how to set it up and run it.

Both parts of this take-home challenge are based on this system.


# Part I: PR Review
You'll find one pull request on this repository.

✅ We'd like you to do a code review, adding any comments you see fit. 

Treat it as you would treat a PR from a colleague of yours, giving feedback for any aspects you deem necessary.

> ℹ️ The PR contains more than one commits, which deal with different topics. If this wasn't an exercise but a real-life 
scenario, each of these commits would be a pull request on its own. We packed all changes into one PR on purpose,
so that it's easier for you to track everything and for us to evaluate your review. We suggest you review each commit
separately, in order to better understand what each one is about.

Apart from that, which we would all agree it's not a good practice in real-world development, everything else is
up for you to evaluate and see how well it has been implemented. 


# Part II: New functionality
The second part of this challenge is totally unrelated to the first.

We'd like you to implement the following features:


## 1. Labs
The system up until now assumed that a single lab would run all blood tests. Now we want the system to be able to work
with different labs in various countries and cities in the world.

Each lab needs to have two properties: `country` and `city`. A city can be associated with multiple labs.

✅ We'd like you to create a lab entity with the specs described above.


## 2. Lab retrieval endpoint
✅ We'd like you to create a Lab model to describe each lab, and an endpoint to fetch a lab by city and country.


## 3. Geolocation endpoint
In `views.py` you'll find a class named `APIGeolocation`. Right now it has a dummy implementation that always
returns the same, fake reply.

✅ We'd like you to update this view so that it performs actual geolocation based on a given IP address.

Please use [https://ipgeolocation.io](https://ipgeolocation.io/documentation.html), which is a free geolocation service.
You are welcome to use `a45776311c6a46babff923066daab671` as the API key if you don't want to create a new account
on the service.

The view should make a synchronous request to this service and return the country and city name,
formatted as `{"country": "<country_name>", "city": "<city_name>"}`.


## 4. Blood tests
Assume that up to now all blood tests were conducted by a certain lab, and were of specific tests types,
e.g. CBC (Complete Blood Count), LDL and HDL (cholesterol).
None of this information was known to the existing system, as it was the same for everyone, so you won't find
anything in the code about a lab or about test types.

Now we need the system to be aware of:
* which lab will conduct the blood tests each time
* which tests are to be included  

✅ We'd like you to add a new endpoint in the `APITestResults` view, in order to allow clients to create
new `BloodTestResults` entries through the API. 

Think of this as a way for the user to order a certain set of blood tests from a specific lab.

The payload of the endpoint should include the following:
* the ID of the lab (as found in the database)
* a list of test types to be conducted (e.g. CBC, LDL, HDL, and so on)

This information should be stored for each entry of blood test results.


## 5. User authentication
✅ We'd like you to create a proper authentication method based on API tokens.

For all the endpoints, the request should include the user's token. The token should be used to authenticate
the user and give them or deny them access accordingly. Each user can have multiple tokens.

Please note that you aren't expected to implement any endpoints for creating or retrieving API tokens,
just the mechanism that uses them for authentication.


## Considerations
Please make sure to include automated tests.

There are multiple features to implement, some of which depend on each other. Although in a real-life scenario
some of these features would be implemented in separate pull requests, you are more than welcome to create
one pull request for everything, if that's more convenient for you. If you do so, make sure that the pull request
is separated into different commits, so that it's easier for us to understand and review.

> ℹ️ If you have any questions whatsoever about this assignment, we'll be more than glad to answer them!
> Just write to your main point of contact in the hiring process, and they will delegate your inquiries
> to the engineering team.

# Resources
In case you haven't a lot of experience with Django, here are some things that could come in handy.

* [Django at a glance](https://docs.djangoproject.com/en/3.2/intro/overview/)
* [Introduction to models](https://docs.djangoproject.com/en/3.2/topics/db/models/)
* [ORM & QuerySet API](https://docs.djangoproject.com/en/3.2/ref/models/querysets/)
* [Customizing authentication in Django](https://docs.djangoproject.com/en/3.2/topics/auth/customizing/)
* [Writing and running tests](https://docs.djangoproject.com/en/3.2/topics/testing/overview/)
* [Django documentation](https://docs.djangoproject.com/)
