import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
from models import *
import re

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)


    '''
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    '''
    CORS(app, resources={r"*": {"origins": "*"}})

    '''
    @TODO: Use the after_request decorator to set Access-Control-Allow
    '''

    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers','Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Methods','GET, POST, PUT, PATCH, DELETE, OPTIONS')
        return response
    '''
    @TODO: 
    Create an endpoint to handle GET requests 
    for all available categories.
    '''

    # this is a helping function to retrieve categories in dict form
    def get_categories():
        categories = Category.query.order_by(Category.type).all()

        if len(categories) == 0:
            abort(404)
        temp = [categr.format() for categr in categories]
        ctg_id = []
        ctg_type = []
        for ctg in temp:
            ctg_id.append(ctg['id'])
            ctg_type.append(ctg['type'])

        return dict(zip(ctg_id,ctg_type))




    @app.route("/categories")
    def retrieve_all_categories():
        return jsonify({
            'success': True,
            'categories': get_categories()
        })
    '''
    @TODO: 
    Create an endpoint to handle GET requests for questions, 
    including pagination (every 10 questions). 
    This endpoint should return a list of questions, 
    number of total questions, current category, categories. 
  
    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions. 
    '''

    def paginate_questions(request, selection):
        page = request.args.get('page', 1, type=int)
        start = (page - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE

        questions = [question.format() for question in selection]
        current_questions = questions[start:end]

        return current_questions

    @app.route("/questions")
    def retrieve_all_questions():
        selection = Question.query.all()
        current_questions = paginate_questions(request, selection)

        if len(current_questions) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'questions': current_questions,
            'total_questions': len(Question.query.all()),
            'current_category': None,
            'categories': get_categories()
        })
    '''
    @TODO: 
    Create an endpoint to DELETE question using a question ID. 
  
    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page. 
    '''

    @app.route("/questions/<question_id>", methods=['DELETE'])
    def delete_question(question_id):
        try:
            qus = Question.query.get(question_id)

            qus.delete()

            return jsonify({
                'success': True,
                'deleted': question_id,
            })
        except:
            abort(422)

    '''
    @TODO: 
    Create an endpoint to POST a new question, 
    which will require the question and answer text, 
    category, and difficulty score.
  
    TEST: When you submit a question on the "Add" tab, 
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.  
    '''
    @app.route("/questions", methods=['POST'])
    def post_new_question():
        body = request.get_json()

        new_question = body.get('question',None)
        new_answer = body.get('answer',None)
        new_difficulty = body.get('difficulty',None)
        new_category = body.get('category', None)

        try:
            question = Question(question=new_question, answer=new_answer,category=new_category,
                                difficulty=new_difficulty)
            question.insert()


            return jsonify({
                'success': True,
                'created': question.id,
            })
        except:
            abort(422)

    '''
    @TODO: 
    Create a POST endpoint to get questions based on a search term. 
    It should return any questions for whom the search term 
    is a substring of the question. 
  
    TEST: Search by any phrase. The questions list will update to include 
    only question that include that string within their question. 
    Try using the word "title" to start. 
    '''

    @app.route("/questions/outcomes", methods=['POST'])
    def search_questions():
        try:
            request_q = request.get_json()
            search = request_q['searchTerm']

            qus_search = Question.query.filter(Question.question.ilike(f"%{search}%")).all()
            questions = [qus.format() for qus in qus_search]


            return jsonify({
                'success': True,
                'questions': questions,
                'total_questions': len(Question.query.all()),
                'current_category': None,
                'categories': get_categories(),
            })
        except:
            abort(404)

    '''
    @TODO: 
    Create a GET endpoint to get questions based on category. 
  
    TEST: In the "List" tab / main screen, clicking on one of the 
    categories in the left column will cause only questions of that 
    category to be shown. 
    '''

    @app.route("/categories/<int:category_id>/questions")
    def get_questions_by_category(category_id):
        try:
            questions = Question.query.filter(Question.category == str(category_id)).all()
            qus = [qus.format() for qus in questions]

            ctg=get_categories()
            return jsonify({
                'success': True,
                'questions': qus,
                'total_questions': len(Question.query.all()),
                'current_category': ctg[category_id]
            })
        except:
            abort(404)

    '''
    @TODO: 
    Create a POST endpoint to get questions to play the quiz. 
    This endpoint should take category and previous question parameters 
    and return a random questions within the given category, 
    if provided, and that is not one of the previous questions. 
  
    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not. 
    '''

    '''
    @TODO: 
    Create error handlers for all expected errors 
    including 404 and 422. 
    '''

    @app.route('/quizzes', methods=['POST'])
    def play_quiz():
        try:
            body = request.get_json()

            category = body.get('quiz_category')
            previous_ques = body.get('previous_questions')

            if category['type'] != 'click':
                questions = Question.query.filter_by(
                    category=category['id']).filter(Question.id.notin_((previous_ques))).all()
            else:
                questions = Question.query.filter(
                    Question.id.notin_((previous_ques))).all()

            return jsonify({
                'success': True,
                'question': questions[random.randrange(0,
                 len(questions))].format() if len(questions) > 0 else None
            })
        except:
            abort(422)



    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found"
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
        }), 422

    @app.errorhandler(405)
    def not_allowed(error):
        return jsonify({
            'success': False,
            'error': 405,
            'message': 'Method not allowed'
        }), 405

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success': False,
            'error': 400,
            'message': 'Bad request'
        }), 400

    @app.errorhandler(500)
    def server_error(error):
        return jsonify({
            'success': False,
            'error': 500,
            'message': 'Internal server error'
        }), 500

    return app



