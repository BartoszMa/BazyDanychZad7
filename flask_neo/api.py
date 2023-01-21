from flask import Flask, request, jsonify, redirect, render_template
from neo4j import GraphDatabase
from dotenv import load_dotenv
import os

load_dotenv()

neo4j_username = os.getenv("USERNAME")
neo4j_password = os.getenv("PASSWORD")
neo4j_bolt_url = os.getenv("BOLT_URL")

driver = GraphDatabase.driver(uri=neo4j_bolt_url, auth=(neo4j_username, neo4j_password))
session = driver.session()
api = Flask(__name__)


def check_employee_exists(name: str, surname: str) -> bool:
    query = '''
    MATCH (n: Employee)
    WHERE n.NAME = $name and n.SURNAME = $surname
    RETURN n
    '''
    result = session.run(query, {"name": name, "surname": surname})
    if result.peek():
        return True
    else:
        return False


@api.route("/employees", methods=["GET"])
def get_employees():
    query = '''
    MATCH (n: Employee)
    RETURN n
    '''
    try:
        result = session.run(query)
        employees = []
        for record in result:
            employees.append(record["n"])
        return jsonify(employees)
    except Exception as e:
        return (str(e))


@api.route("/employees", methods=["POST"])
def create_employee():
    name = request.json["name"]
    surname = request.json["surname"]
    position = request.json["position"]
    department = request.json["department"]
    if check_employee_exists(name, surname):
        return "Employee already exists"
    q1 = '''
    CREATE (n: Employee{NAME: $name, SURNAME: $surname, POSITION: $position, DEPARTMENT: $department}) 
    '''
    map = {"name": name, "surname": surname, "position": position, "department": department}
    try:
        session.run(q1, map)
        return (f"employee node is created with employee name {name} and surname {surname}")
    except Exception as e:
        return (str(e))


@api.route("/employees/<id>", methods=["PUT"])
def update_employee(id):
    name = request.json["name"]
    surname = request.json["surname"]
    position = request.json["position"]
    department = request.json["department"]

    query = '''
    MATCH (n: Employee)
    WHERE ID(n) = $id
    SET n.NAME = $name, n.SURNAME = $surname, n.POSITION = $position, n.DEPARTMENT = $department
    RETURN n
    '''
    try:
        result = session.run(query, {"id": id, "name": name, "surname": surname, "position": position,
                                     "department": department})
        if result.peek():
            return "Employee updated successfully"
        else:
            return "No employee found with the given ID"
    except Exception as e:
        return (str(e))


@api.route("/employees/<id>", methods=["DELETE"])
def delete_employee(id):
    query = '''
    MATCH (n: Employee)
    WHERE ID(n) = $id
    OPTIONAL MATCH (n)-[r:MANAGES]->(d:Department)
    DELETE r
    WITH n,d
    WHERE d.MANAGER = ID(n)
    SET d.MANAGER = null
    DELETE n
    '''
    try:
        result = session.run(query, {"id": id})
        if result.summary().counters.nodes_deleted > 0:
            return "Employee deleted successfully"
        else:
            return "No employee found with the given ID"
    except Exception as e:
        return (str(e))


@api.route("/employees/<id>/subordinates", methods=["GET"])
def get_subordinates(id):
    query = '''
    MATCH (n:Employee)-[:MANAGES]->(s:Employee)
    WHERE ID(n) = $id
    RETURN s
    '''
    try:
        result = session.run(query, {"id": id})
        subordinates = []
        for record in result:
            subordinates.append(record["s"])
        return jsonify(subordinates)
    except Exception as e:
        return (str(e))


@api.route("/employees/<id>", methods=["GET"])
def get_employee(id):
    query = '''
    MATCH (n:Employee)-[:WORKS_IN]->(d:Department)
    WHERE ID(n) = $id
    RETURN n, d
    '''
    try:
        result = session.run(query, {"id": id})
        employee = None
        department = None
        for record in result:
            employee = record["n"]
            department = record["d"]
        if employee:
            return jsonify({"employee": employee, "department": department})
        else:
            return "No employee found with the given ID"
    except Exception as e:
        return (str(e))


@api.route("/departments", methods=["GET"])
def get_departments():
    sort_by = request.args.get("sort_by")
    order = request.args.get("order")
    name = request.args.get("name")
    query = '''
    MATCH (d:Department)
    WHERE d.NAME CONTAINS $name
    RETURN d
    ORDER BY d.{} {}
    '''.format(sort_by, order)
    try:
        result = session.run(query, {"name": name})
        departments = []
        for record in result:
            departments.append(record["d"])
        return jsonify(departments)
    except Exception as e:
        return (str(e))


api = Flask(__name__)

@api.route("/departments/<int:id>/employees", methods=["GET"])
def get_employees(id):
    query = '''
    MATCH (d:Department)-[:WORKS_IN]->(n:Employee)
    WHERE ID(d) = $id
    RETURN n
    '''
    try:
        result = session.run(query, {"id": id})
        employees = []
        for record in result:
            employees.append(dict(record["n"]))
        return jsonify(employees)
    except Exception as e:
        return (str(e))


if __name__ == "__main__":
    api.run(port=5050)
