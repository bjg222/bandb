
from flask import redirect, session, render_template, request, flash

from . import main

@main.route('/')
def main():
    return render_template('main/index.html')