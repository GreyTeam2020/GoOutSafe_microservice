# GoOutSafe with microservices

![GitHub Workflow Status](https://img.shields.io/github/workflow/status/GreyTeam2020/GoOutSafe_microservice/docker-compose-actions-workflow?style=for-the-badge)
![Codecov](https://img.shields.io/codecov/c/github/GreyTeam2020/GoOutSafe_microservice?style=for-the-badge)

## Table of Content

- [App Architecture](#)
- [How Build and run with Docker](https://greyteam2020.github.io/GoOutSafe_microservice/run-test-on-the-host-machine)
- [Developing](https://greyteam2020.github.io/GoOutSafe_microservice/GoOutSafe_microservice#developing)
- [Additional information](https://greyteam2020.github.io/GoOutSafe_microservice/additional-information)

## App Architecture

![](https://i.ibb.co/hc3V1mk/photo-2020-11-26-10-09-58.jpg)

![](https://i.ibb.co/CHRR11W/Selection-046.png)

## How clone it

Each microservices is a separate repository that you can clone with the following commands

```bash
git clone --recurse-submodules https://github.com/GreyTeam2020/GoOutSafe_microservice.git
```

[Source](https://stackoverflow.com/a/3797061/7290562)

The submodules are the microservices with the following proprieties:

- [Email Microservices](https://github.com/GreyTeam2020/email_microservice): Running on port 5001 and include some [celery](https://docs.celeryproject.org/en/stable/getting-started/introduction.html) tasks.
- [User Microservices](https://github.com/GreyTeam2020/users_microservice): Running on port 5002;
- [Restaurants Microservice](https://github.com/GreyTeam2020/restaurants_microservice): Running on port 5003;
- [Booking Microservice](https://github.com/GreyTeam2020/booking_microservice): Running on port 5004

## How Build and run with Docker

Clone the repository with the command above and run in the root folder the command
`docker-compose up`
This will make docker downloads all the file needed and start building the containers. 
After that, you can browse to http://localhost/ to use the app.

## Run test on the host machine

You can't without docker this time, to run it on the host machine without docker you can run the monolith version
available [here](https://github.com/GreyTeam2020/GoOutSafe_Primer2020)

## Developing

Each programmer has a personal style on write code and we accept this, but to make readability the
code from all component of the team, we used a good tool to format the code in automatically.

It is [black](https://github.com/psf/black), and it is installed with the requirements.txt

To format the code you can run the command below after `pip3 install -r requirements.txt --user`

`black monolith`

When you see the following line, you are done to push your PR

All done! ✨ 🍰 ✨


## Additional information

- Deadline - Wednesday, 25 November 2020, 23:59
