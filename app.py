from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)

@app.route('/')
def home():
    return render_template('admin_dashboard.html')

@app.route('/manage_users')
def manage_users():
    return "Manage Users Page"

if __name__ == '__main__':
    app.run(debug=True)
