# Copyright (C) 2016 Baofeng Dong
# This program is released under the "MIT License".
# Please see the file COPYING in the source
# distribution of this software for license terms.


import os
import sys
import time
import json
from decimal import Decimal

from flask import make_response, Blueprint, redirect
from flask import url_for,render_template, jsonify, request
from sqlalchemy import func
import pygal
from pygal.style import DarkSolarizedStyle, LightStyle, CleanStyle, DarkStyle
from .helper import Helper
from dashboard import debug, error
from dashboard import Session as Session
from dashboard import app
from .metadata import metadata
from dashboard.auth import Auth


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/introduction')
def intro():
    return render_template("introduction.html")

@app.route('/progress')
def progress():
    return render_template("progress.html")

@app.route('/results')
@Auth.requires_auth
def result():
    routes = Helper.get_routes()
    questions = Helper.get_questions()
    directions = Helper.get_directions()
    return render_template("results.html",
        routes=routes,directions=directions, questions=questions)

@app.route('/results/_data', methods=['GET'])
def request_query():
    response = []
    where = ""
    args = request.args

    where = Helper.buildconditions(args)
    debug(where)
    qnum = int(request.args.get('qnum'))

    if qnum == 1:
        response = Helper.get_satisfaction(where=where, qnum=qnum)
    if qnum == 2:
        response = Helper.get_origin(where=where,qnum=qnum)
    if qnum == 3:
        response = Helper.get_destination(where=where,qnum=qnum)
    if qnum == 4:
        response = Helper.get_travel_change(where=where,qnum=qnum)
    if qnum == 5:
        response = Helper.get_travel_less(where=where,qnum=qnum)

    return jsonify(data=response, metadata=metadata[qnum])

@app.route('/map')
def map():
    routes = Helper.get_routes()
    directions = Helper.get_directions()

    return render_template("map.html",
        routes=routes,directions=directions)


@app.route('/map/_query', methods=['GET'])
def map_query():
    response = []
    where = ""
    args = request.args

    where = Helper.buildconditions(args)
    debug(where)

    response = Helper.query_map_data(where=where)

    return jsonify(data=response)


@app.route('/map/_data', methods=['GET'])
def sep_query():
    response = []
    where = ""
    args = request.args

    where = Helper.buildconditions(args)
    debug(where)

    #get the sel_boundary param from the request.args object
    sel_boundary = args.get('boundary')
    debug(sel_boundary)

    #call functions based on sel_boundary value
    if sel_boundary == 'sep':
        response = Helper.query_sep_data(where=where)

    if sel_boundary == 'zipcode':
        response = Helper.query_zipcode_data(where=where)

    if sel_boundary == 'cty':
        response = Helper.query_cty_data(where=where)

    return jsonify(data=response)

@app.route('/data')
def data():
    """Sets up table headers and dropdowns in template"""
    headers = ['Date', 'Time', 'Surveyor', 'Route', 'Direction', 'Satisfaction', 'Comments']
    routes = [ route['rte_desc'] for route in Helper.get_routes() ]
    directions = Helper.get_directions()
    users = Helper.get_users()

    return render_template('data.html',
            routes=routes, directions=directions, headers=headers,
            users=users)


@app.route('/data/_query', methods=['GET'])
def data_query():
    response = []
    user = ""
    rte_desc = ""
    dir_desc = ""
    csv = False

    if 'rte_desc' in request.args.keys():
        rte_desc = request.args['rte_desc'].strip()
        debug(rte_desc)
    if 'dir_desc' in request.args.keys():
        dir_desc = request.args['dir_desc'].strip()
        debug(dir_desc)
    if 'user' in request.args.keys():
        user = request.args['user'].strip()
        debug(user)
    if 'csv' in request.args.keys():
        csv = request.args['csv']
        debug(csv)

    if csv:
        data = Helper.query_route_data(
            user=user, rte_desc=rte_desc, dir_desc=dir_desc,csv=csv
        )
        response = ""
        # build csv string
        for record in data:
            response += ','.join(record) + '\n'
    else:
        response = Helper.query_route_data(
            user=user, rte_desc=rte_desc, dir_desc=dir_desc
        )

    return jsonify(data=response)


@app.route('/surveyors')
def surveyor_status():
    return render_template('surveyors.html')


@app.route('/surveyors/_summary', methods=['GET'])
def surveyor_summary_query():
    response = []
    date = time.strftime("%Y-%m-%d")
    debug(request.args)
    debug(request.args['date'])
    if 'date' in request.args.keys():
        date = request.args['date'].strip()
    debug(date)
    debug(type(date))
    response = Helper.get_user_data(date)
    debug(response)
    return jsonify(data=response)


