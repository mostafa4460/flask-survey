from flask import Flask, request, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from surveys import satisfaction_survey

app = Flask(__name__)

app.config['SECRET_KEY'] = '12345'
debug = DebugToolbarExtension(app)

# user answers
responses = []
# index of last question in the survey
last_question = len(satisfaction_survey.questions) - 1

@app.route('/')
def show_survey():
    " Shows the survey page with info about the survey"

    title, instructions = satisfaction_survey.title, satisfaction_survey.instructions
    return render_template('survey.html', title = title, instructions = instructions)

@app.route('/questions/<int:id>')
def show_question(id):
    """ Shows the question page (1 question per page) or redirects to the right page
    - id: index of a question in the survey

    IF we have a response from the user for every question:
    - redirect to thank you page

    IF the id is trying to take the user to the next question without having a response for the previous one:
    - redirect to the right question
    - flash error message
    """

    if id != len(responses):
        if len(responses) == len(satisfaction_survey.questions):
            return redirect('/thankyou')
        else:
            id = len(responses)
            flash("Tried accessing an invalid question in survey", "error")
            return redirect(f'/questions/{id}')
    else:
        question_obj = satisfaction_survey.questions[id]
        question, choices = question_obj.question, question_obj.choices
        # what the button will say
        button_msg = "Next" if id != last_question else "Submit"
        # need this to redirect in the /answer route
        session['id'] = id
        return render_template('questions.html', id=id, question=question, choices=choices, btn_msg=button_msg)        

@app.route('/answer', methods=["POST"])
def submit_answer():
    """ Adds the user's answer to responses[] then redirects to:
    - the next question if the user hasn't responded to all the questions
    - OR the thank you page where we flash a success message
    """

    answer = request.form.get('answer')
    responses.append(answer)
    # from the previous question page
    next_question = session.get('id') + 1

    if next_question > last_question:
        flash("Your answers have been successfully recorded", "success")
        return redirect('/thankyou')
    else:
        return redirect(f'/questions/{next_question}')

@app.route('/thankyou')
def show_thankyou():
    " Shows thank-you page "

    return render_template('thankyou.html')