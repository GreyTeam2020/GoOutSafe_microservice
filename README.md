# GoOutSafe

![Travis (.org)](https://img.shields.io/travis/GreyTeam2020/GoOutSafe_Primer2020?style=for-the-badge)
![Coveralls github](https://img.shields.io/coveralls/github/GreyTeam2020/GoOutSafe_Primer2020?style=for-the-badge)

## Table of Content

- [How Build and run with Docker](https://greyteam2020.github.io/GoOutSafe_Primer2020/)
- [Developing](https://greyteam2020.github.io/GoOutSafe_Primer2020/#developing)
- [Additional information](https://greyteam2020.github.io/GoOutSafe_Primer2020/#additional-information)

## How Build and run with Docker

>To enable celery you need to change the value inside the `monolith/utils/dispaccer_events.py` at line 4 
the propriety `_CELERY` from `False` to `True`.

Clone the repository and run in the root folder the command
`docker-compose up`
This will make docker downloads all the file needed and start building the containers. 
After that, you can browse to http://localhost:5000/ to use the app.

## Run test on the host machine

To run the test on your host machine you need to install the requirements with the following command

`pip3 install -r requirements.txt`

And only after you can run the tests from the root directory with the command

`python3 -m pytest --cov-config .coveragerc --cov monolith`

P.S: The python and pip command depend from your local configuration.

## Additional information

The docker share the db with the host machine, so if you ran the app the first time with docker and only after try to run 
the app without docker you need to change the permission at the db with he follow command `sudo chmod -R  777 monolith/db`

This could be an operation that you need to do, but depend to how you run docker and what is your docker conf.

## Developing

Each programmer has a personal style on write code and we accept this, but to make readability the
code from all component of the team, we used a good tool to format the code in automatically.

It is [black](https://github.com/psf/black), and it is installed with the requirements.txt

To format the code you can run the command below after `pip3 install -r requirements.txt --user`

`black monolith`

When you see the following line, you are done to push your PR

All done! ✨ 🍰 ✨


## Additional information

- Deadline - November 6th, 2020 at 08:59 am
  - (Sub) Deadline for the priority one - October 28th, 2020 at 06:00pm.
