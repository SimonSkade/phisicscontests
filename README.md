# physicscontests

This is the source code of a website that hosts physics contests. It is kind of like coding competitions, but with physics problems.

## Website

https://physicscontests.herokuapp.com/

## Try running it yourself

(It may not work if you are not using Linux)

Use pipenv to run the application.

Clone repo:

```
git clone https://github.com/SimonSkade/physicscontests.git
```

or 

```
git clone git@github.com:SimonSkade/physicscontests.git
```

No go into the project directory and install and setup pipenv:

```
cd physicscontests/ #go to project directory
pip install pipenv #install pipenv
pipenv shell #go into the virtual environment pipenv
pipenv install --ignore-pipfile #install necessary python-packages with the right version in your pipenv
```

The `--ignore-pipfile` is important so you have the same package versions.

Then inside your pipenv, you can run

```
python run.py
```

to deploy the website on your local machine.

In your browser, you can now open the link, outputted from the command (most often localhost:5000).

## License

This website is created from a template from colorlib. You are not allowed to remove the copywrite at the bottom of the website (except if you buy a license from colorlib).

Template: https://colorlib.com/wp/template/manup/

The way I built up this website was inspired by a flask tutorial series on youtube:

https://www.youtube.com/watch?v=MwZwr5Tvyxo&list=PL-osiE80TeTs4UjLw5MM6OjgkjFeUxCYH


