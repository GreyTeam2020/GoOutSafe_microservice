from flask_wtf import FlaskForm
import wtforms as f
from wtforms.validators import DataRequired, Length, Email, NumberRange


class LoginForm(FlaskForm):
    email = f.StringField("email", validators=[DataRequired()])
    password = f.PasswordField("password", validators=[DataRequired()])
    display = ["email", "password"]


class UserForm(FlaskForm):
    email = f.StringField("email", validators=[DataRequired(), Email()])
    firstname = f.StringField("firstname", validators=[DataRequired()])
    lastname = f.StringField("lastname", validators=[DataRequired()])
    password = f.PasswordField("password", validators=[DataRequired()])
    phone = f.StringField("phone", validators=[DataRequired()])
    dateofbirth = f.DateField("dateofbirth", format="%d/%m/%Y")
    display = ["email", "firstname", "lastname", "password", "phone", "dateofbirth"]
    # TODO fixe the form date for future born people.


class UserEditForm(FlaskForm):
    email = f.StringField("email", validators=[DataRequired(), Email()])
    firstname = f.StringField("firstname", validators=[DataRequired()])
    lastname = f.StringField("lastname", validators=[DataRequired()])
    dateofbirth = f.DateField("dateofbirth", format="%d/%m/%Y")
    display = ["email", "firstname", "lastname", "dateofbirth"]


class RestaurantForm(FlaskForm):
    name = f.StringField("name", validators=[DataRequired()])
    ## FIXME(vincenzopalazzo) modify the phone length
    phone = f.StringField("phone", validators=[DataRequired(), Length(min=8, max=15)])
    lat = f.StringField("latitude", validators=[DataRequired()])
    lon = f.StringField("longitude", validators=[DataRequired()])
    n_tables = f.StringField(
        "Number of tables for 6 People", validators=[DataRequired()]
    )
    covid_measures = f.StringField("Anti-Covid measures", validators=[DataRequired()])
    # photo = f.FileField("Photo of restaurant")
    cuisine = f.SelectMultipleField(
        "Cuisine Type",
        choices=[
            ("Italian food", "Italian food"),
            ("Chinese food", "Chinese food"),
            ("Indian Food", "Indian Food"),
            ("Japanese Food", "Japanese Food"),
            ("Other", "Other"),
        ],
        validators=[DataRequired()],
    )
    open_days = f.SelectMultipleField(
        "Opening days",
        choices=[
            ("0", "Monday"),
            ("1", "Tuesday"),
            ("2", "Wednesday"),
            ("3", "Thursday"),
            ("4", "Friday"),
            ("5", "Saturday"),
            ("6", "Sunday"),
        ],
        validators=[DataRequired()],
    )
    open_lunch = f.TimeField("open time for lunch", validators=[DataRequired()])
    close_lunch = f.TimeField("close time for lunch", validators=[DataRequired()])
    open_dinner = f.TimeField("open time for dinner", validators=[DataRequired()])
    close_dinner = f.TimeField("close time for dinner", validators=[DataRequired()])
    display = [
        "name",
        "phone",
        "lat",
        "lon",
        "n_tables",
        "cuisine",
        "open_days",
        "open_lunch",
        "close_lunch",
        "open_dinner",
        "close_dinner",
        "covid_measures",
    ]


class RestaurantTableForm(FlaskForm):
    name = f.StringField("name", validators=[DataRequired()])
    capacity = f.IntegerField("capacity", validators=[DataRequired()])
    display = ["name", "capacity"]


class SearchUserForm(FlaskForm):
    email = f.StringField("email")
    phone = f.StringField("phone")
    display = ["email", "phone"]


class PhotoGalleryForm(FlaskForm):
    url = f.StringField("URL", validators=[DataRequired()])
    caption = f.StringField("caption")
    display = ["url", "caption"]


class ReviewForm(FlaskForm):
    stars = f.FloatField("stars", validators=[DataRequired()])
    review = f.StringField("review", validators=[DataRequired()])
    display = ["stars", "review"]


class ReservationForm(FlaskForm):
    reservation_id = f.HiddenField("")  # for update
    reservation_date = f.DateTimeField("Date", validators=[DataRequired()])
    people_number = f.IntegerField("N. of People", validators=[DataRequired()])
    friends = f.TextAreaField(
        "Friend's mails (separated by semicolon)", validators=[DataRequired()]
    )
    restaurant_id = f.HiddenField("")
    display = [
        "reservation_id",
        "reservation_date",
        "people_number",
        "friends",
        "restaurant_id",
    ]


class DishForm(FlaskForm):
    name = f.StringField("Dish name", validators=[DataRequired()])
    price = f.FloatField("Price", validators=[DataRequired()])
    display = ["name", "price"]
