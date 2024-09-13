from flask import Flask,render_template,request,jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column,Integer,String,update
from sqlalchemy.exc import SQLAlchemyError


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:20022007@localhost:5432/admin_panel'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'users'
    id = Column(Integer, primary_key = True, index=True)
    first_name = Column(String, index=True)
    last_name = Column(String,index=True)
    email = Column(String, index=True)
    password = Column(String, index=True)

@app.route('/')
def register_form():
    return render_template('register.html')

@app.route('/index')
def index_form():
    data = User.query.all()
    return render_template('index.html',datas = data)

@app.route('/login')
def login_form():
    return render_template('login.html')

@app.route('/register/',methods=['POST'])
def register():
    id = User.query.with_entities(db.func.max(User.id)).scalar()
    if id is None:
        id = 0
    else:
        id = int(id)
    
    new_id = (id+1)
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        email = data.get('email')
        password = data.get('password')

        if not all([first_name, last_name, email, password]):
            return jsonify({'error': 'Missing required fields'}), 400

        if User.query.filter_by(email=email).first():
            return jsonify({'message': 'They are same'}), 200      
        else:
            new_user = User(
                id = new_id,
                first_name=first_name,
                last_name=last_name,
                email=email,
                password=password
            )
            
            db.session.add(new_user)
            db.session.commit()

            return jsonify({'status': 'success'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'failed', 'error': str(e)}), 500

@app.route('/login/',methods=['POST'])
def login():
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')
        
        user = User.query.filter_by(email=email).first()

        if user and user.password == password:
            return jsonify({'status': 'success'}), 200
        else:
            return jsonify({'status': 'failed'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'status' : 'failed'}), 500

@app.route('/index/',methods=['POST'])
def index():
    data = request.get_json()
    
    user_id = data.get('id')
    firstName = data.get('first_name')
    lastName = data.get('last_name')
    email = data.get('email')
    pswd = data.get('password')
    
    print(user_id)
    
    try:
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error' : 'User not found'}) , 404
        
        user.first_name = firstName
        user.last_name = lastName
        user.email = email
        user.password = pswd
        
        db.session.commit()
        return jsonify({'status': 'success'}), 200
        
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'failed', 'error': str(e)}), 500
    
@app.route('/index/addrow/',methods=['POST'])
def addRow():
    id = User.query.with_entities(db.func.max(User.id)).scalar()
    if id is None:
        id = 0
    else:
        id = int(id)
    
    new_id = (id+1)
    
    data = request.get_json()
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        email = data.get('email')
        password = data.get('password')

        if not all([first_name, last_name, email, password]):
            return jsonify({'error': 'Missing required fields'}), 400

        if User.query.filter_by(email=email).first():
            return jsonify({'message': 'They are same'}), 200      
        else:
            new_user = User(
                id = new_id,
                first_name=first_name,
                last_name=last_name,
                email=email,
                password=password
            )
            
            db.session.add(new_user)
            db.session.commit()

            return jsonify({'status': 'success'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'tatus': 'failed', 'error': str(e)}), 500
    
    
    
@app.route('/index/delete_user/', methods=['POST'])
def delete_users():
    data = request.get_json()

    # Gelen ID'lerin bir liste olup olmadığını ve içinin boş olup olmadığını kontrol et
    ids = data.get('ids', [])
    if not isinstance(ids, list) or not all(isinstance(id, int) for id in ids):
        return jsonify({'status': 'error', 'message': 'Invalid IDs format'}), 400

    if not ids:
        return jsonify({'status': 'error', 'message': 'No IDs provided'}), 400

    try:
        users_to_delete = User.query.filter(User.id.in_(ids)).all()
        if not users_to_delete:
            return jsonify({'status': 'error', 'message': 'No users found with the provided IDs'}), 404
        
        for user in users_to_delete:
            db.session.delete(user)
        db.session.commit()
        return jsonify({'status': 'success', 'message': f'Users with IDs {ids} deleted'}), 200

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': 'Database error: ' + str(e)}), 500
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': 'Unexpected error: ' + str(e)}), 500
    

if __name__ == '__main__':
    app.run(debug=True)